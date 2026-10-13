# Policy-task audit — deferred_annuity_withdrawals_and_death_benefits / charter-global

## charter_global_frozen

- Scenario: env/env_0044_life_and_annuity_insurer; difficulty deferred_annuity_withdrawals_and_death_benefits; category fixed; M=2.
- Frozen inputs:
  - `tasks/deferred_annuity_withdrawals_and_death_benefits/fixed.extended.yaml` sha256 `d3c7e7a0d705be3f1cf19c090b49345ca053e91d2e0de19c78fd9e8f7603daf5` (matches brief)
  - `tasks/deferred_annuity_withdrawals_and_death_benefits/task_tools.py` sha256 `15a060860f596d8f1018b895d95e589fee54ad0e881e5f3c54421e292eb3ca00` (matches brief)
  - blueprint: `blueprint.yaml`, `db_schema.json`, `share_tools.py`, `products/fixed.yaml` (plus `products/{whole,income,term}.yaml` read only for lifecycle states of cross-read rows)
  - runtime DSL semantics (MONTHS / DAYS / SUM within_months / LATEST / EXISTS / XCOUNT / XLATEST / CFIELD) read from `skills/erl-task-instantiate/scripts/check_compute.py::build_env`. It holds no task data.
- Freeze time: 2026-10-08T03:02:50Z. Auditor: independent policy-task auditor (did not author any artifact of this difficulty).
- Permitted: the charter (base + extended), the tool contracts and bodies, blueprint, erlbench, and the two masked views (frozen_time, user_scenario, initial_state only).
- Masked / unread when this section was written: every `tasks/*.json` field beyond the masked views (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure), the difficulty's worklog.md, and any prior audit. Nothing in this section derives from a revealed GT.
- Entry conditions (Step 0): the brief supplied the gate snapshot (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; traceability deferred to render stage) and the masked views with hashes (task_0 `3e3e5afd…`, task_1 `548438b4…`, recomputed and matching). Input is complete. A green gate qualifies the difficulty for manual audit; it does not prove correctness.
- Base copy: lines 1–1019 of the extended yaml are byte-identical to `blueprint/products/fixed.yaml` (`diff` clean).

### policy_conflict_scan

The six extended policies form two chains with disjoint tool sets:

| id | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- |
| P1 fixed_ext_missed_withdrawal_charge | assess_missed_withdrawal_charge_e9f9c059 (agent) | charge_amount | [] |
| P2 fixed_ext_surrender_part_year_interest | credit_surrender_interest_88d8dad0 (agent) | interest_amount | P1 (value_input, state, gate b_cv) |
| P3 fixed_ext_surrender_value | confirm_full_surrender_fa1c6fc8 (user) | cash_surrender_value | P2 (value_input, state, gate a_cv) |
| P4 fixed_ext_claim_renewal_rate | renew_guarantee_period_14f04954 (agent) | renewal_rate | [] |
| P5 fixed_ext_death_valuation_interest | credit_death_valuation_interest_0cf0ffa2 (agent) | interest_amount | P4 (value_input, state, gate v_growth) |
| P6 fixed_ext_death_claim_settlement | settle_death_benefit_share_569ae0ca (user) | claim_interest | P5 (value_input, state, gate s_db) |

- Overlapping subjects. P2 and P5 both write `fixed_interest_credited`, but their triggers are exclusive: P2 fires when a full surrender is handled, P5 when an owner's death is on file. A death-pending contract takes no surrender (base fixed_death_claim_registered: "the contract stops accepting transactions other than the claim"). P1 and P3 both settle surrender charges. P1 corrects a past partial withdrawal; P3 settles the full surrender. Their objects and tools differ. P4 overlaps base fixed_guarantee_period_renewal only on default renewal, which P4 claims, and leaves elections to base.
- Eligibility, time anchors and terminal states. Two conflicts with base are recorded below (F-C1, F-C2), along with one terminal-state observation (O-C3).
- Cross-category reads: P1/P3 read whole (status `in_force` + whole_premium_paid count). P2 reads income (`income_active` + income_payment_issued count). P4 reads whole (any status). P5 reads whole service requests and income. P6 reads term holdings and service requests, and whole transactions. Each is declared in that policy's `cross_category`. All are read-only.
- Scopes (structural expectation, to be confirmed against `charter_scope` at reveal): the two chains {P1,P2,P3} and {P4,P5,P6} are disjoint and together cover all six extended policies.

### rule_compute_equivalence

I checked every binding against its `compute_basis` quotation and the rule sentence, and swept back sentence by sentence.

- P1. c_w_amt/c_w_date ("most recent excess partial withdrawal"). c_av: CV less rows after the anniversary that opened the withdrawal's contract year. c_before_w / c_before_rmd / c_before_waiver: earlier withdrawals of that contract year. c_free_pct, c_counted, c_free_rem, c_excess. c_sched_pct ("first-year percentage less ladder_step per completed schedule year" equals every tier's ladder, because all six ladders step by 0.01; this is equivalent to the base ladder). c_capped, c_rel_reduction (in-force whole + count over 12 months before booking), c_graded, c_share, result. Each has a rule sentence, and each rule sentence has a binding. Observation: the "earlier in that contract year" windows are approximated by MONTHS-offset windows. Two rows less than one month-offset apart could be misclassified. No such rows exist in either world.
- P2. b_last, b_recv, b_days (three end-date tiers), b_closing_add, b_income_add, b_history_adj (tier order: +addition when no non-RMD withdrawal, else −adjustment when an excess partial exists, else 0; matches the rule), b_rate, b_interest (simple / daily-compound nominal / effective), and result rounded once. Equivalent.
- P3. a_m_cy (months since latest anniversary), a_anniv_value, a_counted, a_free_pct (age on latest anniversary, schedule year on handling date), a_sched_pct, a_capped_pct (age on handling date), a_rel_reduction, a_graded_pct (months completed in current schedule year at handling), a_charge, a_ptax (issue_state ∈ [CA]; qualified 0.005 / non-qualified 0.0235 of premiums received), and result. Equivalent.
- P4. r_cv (ledger sum = value at last credit), r_value_renew (grown at expiring rate to the renewal date = GP end + 1), r_measure (death / waiting approved withdrawal / renewal date), r_band (4 tiers), r_persist, r_rel, and result max(min rate, base + three additions) rounded to 4 dp. Equivalent, with one interpretive point. The rule says "the owner holds an Ashgrove whole life policy", which is present tense and has no status qualifier. Compute implements it as `EXISTS('whole')` (any status). P1/P3 say "in-force", and P5 uses past tense "held" for the income annuity. This is a wording asymmetry, not a binding gap. It bears on task 1 and is assessed in 1.md.
- P5. v_end_days (WL certificate before this claim / claim > late_claim_days after death / this claim), v_d1/v_d2 (split at the renewal date, read from sc_schedule_start_date), v_band_add, v_age_add, v_inc_add, v_adds, v_growth (two-part / all-expiring / all-current), and result. Equivalent. The renewal date in the rule is a calendar fact (GP end + 1). The compute reads it from sc_schedule_start_date, which equals GP end + 1 only once the renewal is recorded. Before the renewal the rule's "current guaranteed rate" is still the expiring rate, so both faces give the same number (verified on task 1's opening world: 16666.01 both ways).
- P6. s_db, the s_own_share / s_pre_* reallocation (predeceased primary shown by a death claim on a policy insuring that beneficiary), s_val (interest_period_end of the latest credit = the valuation date), s_start_days, s_rate, s_late, s_coord, s_end_extra, s_divisor (360 for actual_360_states, 366 in a leap payment year, else 365), and result. Equivalent.
- Day-count wording (observation O-C4). P2/P5 say "runs from the date of the contract's most recent interest credit through the date …, counted in actual calendar days". The compute counts DAYS(start, end), i.e. elapsed days. That matches the seeded crediting convention (each credit is dated the day after its interest_period_end, and DAYS between consecutive credit dates reproduces the seeded amounts, e.g. 94 days for 2024-11-16→2025-02-18 in task 0). It also matches base fixed_surrender "interest is credited to that date". An inclusive "through" count (+1 day) is a weaker alternative reading. Not RED.

No rule sentence lacks a binding and no binding lacks a rule sentence.

### action_binding_and_uuids

- Each (target_tool, computes) pair is claimed by exactly one policy. P2 and P5 share `interest_amount` but target different tools.
- Docstrings name no other tool and state no position in a sequence. Each docstring has an "Afterwards the contract shows …" sentence describing its own post-state. That is not an ordering relation to other actions (observation only). No tool adds a confirmation, review or wait.
- Tool bodies check no eligibility and no prerequisite. None returns an error or a hint. They only create or update rows: `ctx.create` / `ctx.update`, with no branching on status, on the presence of a charge row, or on the presence of an interest credit.
- uuid8 tails: e9f9c059, 88d8dad0, fa1c6fc8, 14f04954, 0cf0ffa2, 569ae0ca. Six distinct values with no shared prefix, no sequence and no adjacent-value pattern. Consistent with independent generation. Generation provenance itself cannot be observed.

### prerequisite_graph

- `prerequisite` is filled for all six (`[]` on P1, P4). Every `problem` points to an extended policy id in this file, never to a base policy or to itself. The graph is P1→P2→P3 and P4→P5→P6: acyclic, with no cross-chain edge.
- `policy_source` is verbatim in the blocked policy's own rule for all four edges (E1 P2 rule sentence 2; E2 P3 rule sentence 2; E3 P5 rule sentence 2; E4 P6 rule sentence 2).
- `form: state` on all four. No `fallback_reason`, correctly, since none is action-form.
- `kind: value_input` on all four. Each `gate` names a real binding of the blocked compute (b_cv, a_cv, v_growth, s_db). Each `resolved_by` equals the depended-on policy's target_tool and moves that binding: P1's charge lowers contract_value; P2's credit raises it; P4's renewal sets guaranteed_rate and sc_schedule_start_date, which feed v_growth; P5's credit raises the ledger sum and writes interest_period_end.
- Conditions vs sentences. E1 adds "the contract value reflects that charge", which is implied by P1's "booked as a deduction". E3 adds "its surrender charge schedule start date is the renewal date", which the renew tool brings about together with the rate. Neither is a material strengthening. E4: see F-C2.
- No authoring-viewpoint phrasing ("in this task", "at the opening") appears in any `prerequisite`.

### prerequisite_sentences

Four-point test for each edge:

- **E1 (P2 ← P1)**: "The part-year surrender interest is worked out only after every excess partial withdrawal on the contract carries its surrender charge entry." The connective is "only after". The waited-on state is record-visible: a fixed_withdrawal_paid row with withdrawal_type excess_partial paired with a fixed_surrender_charge_assessed row (charge_reason partial_withdrawal) under the same fixed_request_id. No tool, id or snake_case token. Exactly one write of this difficulty creates such a row: assess_missed_withdrawal_charge (P1). Derivation: sentence → find excess_partial rows lacking a charge entry → the policy whose rule books "the missing charge" on "an excess partial withdrawal that was paid without the surrender charge entry it owed" is P1 → one reading. P1's rule does not restate the sentence. PASS.
- **E2 (P3 ← P2)**: "The cash surrender value is not fixed until the contract carries the part-year interest credited for the surrender." The connective is "not until". The state is record-visible: an interest credit dated after the signed surrender request's receipt. Of the two interest-crediting writes, only credit_surrender_interest (P2) is triggered by a surrender. P5's write requires "an owner's death is on file", so the hop resolves to P2 alone. PASS.
- **E3 (P5 ← P4)**: "The death benefit valuation interest is fixed only after the contract carries its renewed guaranteed rate for every guarantee period that ended before the valuation date." The connective is "only after". The state is visible through guaranteed_rate, guarantee_period_end_date and sc_schedule_start_date. Exactly one write sets a renewed rate: renew_guarantee_period (P4). PASS.
- **E4 (P6 ← P5)**: "A beneficiary's death benefit share is not paid until the contract carries the valuation interest credited through the date due proof of death was received." The connective is "not until". The only write is credit_death_valuation_interest (P5). The scope of the waited-on date does not match the edge's `condition` or P5's own rule. FAIL: see F-C2.
- Rules carry no second wording of any dependency and name no tool or other policy id. The depended-on rules (P1, P2, P4, P5) do not restate the sentences that wait on them.
- I found no undeclared cross-problem order in any extended rule.
- One base rule states a cross-problem dependency: base fixed_evt_rmd_and_systematic says systematic installments "are withdrawals under fixed_evt_withdrawal". No task tree rests on it. Observation only.

### override_declarations

Sentence-by-sentence findings against each `base_policy_refs` entry (finding half only; each task file demonstrates the consequences against its own world):

- **P1** against fixed_evt_withdrawal. Free percentage: declared (overwrite 1). Charge composition (cap → reduce → grade × recovered share): declared (overwrite 2). Ladder percentage: follows base, as shown above. "Deducted from the remaining contract value": follows base. Renewal window and waiver zeroing: follow base. P1 broadens the waiver zeroing to "the contract has an approved … waiver claim" without restating base fixed_sc_waivers' coverage conditions; approval status is base's own condition, so I record this as an observation. **"From contract year free_withdrawal_first_contract_year" is not named and not reproduced. P1's free amount exists in every contract year (dropped branch). See F-C1.** Against fixed_evt_rmd_and_systematic: "they count toward the free withdrawal amount" is declared replaced (overwrite 3). The RMD waiver itself is inherited. fixed_surrender and fixed_guarantee_period_renewal: no conflict.
- **P2** against fixed_interest_crediting. Convention: declared (overwrite 1). Rate composition: declared (overwrite 2). **The part-year end: base fixed_interest_crediting says interest is credited "on the date of any … surrender … for the part year since the last crediting", and base fixed_surrender says "The surrender is effective on the date the signed request is received in good order; interest is credited to that date." P2's end-date tiers run the part year "through the handling date" (handled > lag_long_days after receipt) or "through the day after the receipt date" (handled 1–lag_long_days after). Neither base sentence is named in P2's `overwrite`. This is an undeclared override. See F-C1.**
- **P3** against fixed_surrender. Charge formula: declared (overwrite 1). Premium tax: declared (overwrite 2). "No charge after the schedule / in a renewal window / under an approved waiver": follows base. Deferral and withholding: inherited. "Never less than the guaranteed minimum value required by the state nonforfeiture law": inherited, not restated. The charter has no figure for that floor, so it cannot be evaluated (observation). **"The surrender is effective on the date the signed request is received in good order": P3 instead says "The cash surrender value is worked out on the date the surrender is handled". This is not named. It is an undeclared change of the scored quantity's evaluation anchor. See F-C1.** Against fixed_evt_withdrawal: free percentage declared (overwrite 3). **The free_withdrawal_first_contract_year gate is dropped and not named (F-C1).** Against fixed_evt_rmd_and_systematic: RMD counting declared (overwrite 4). Against fixed_sc_waivers: approval timing declared (overwrite 5). fixed_guarantee_period_renewal: follows base.
- **P4** against fixed_guarantee_period_renewal: election deadline declared replaced (overwrite 1). Default renewal into the same length on GP end + 1 with a new SC schedule: follows base. Against fixed_interest_crediting: the band clause is declared replaced (overwrite 2), and the minimum-rate floor is kept. fixed_death_benefit: not touched.
- **P5** against fixed_death_benefit: the valuation date is declared replaced (overwrite 1), and "no surrender charge" is inherited. Against fixed_interest_crediting: overwrite 2 names "Each guarantee period earns the rate guaranteed for it". That covers the additions and the all-expiring / all-current rate tiers, since they deviate from that same sentence. The effective-rate convention follows base.
- **P6** against fixed_death_benefit: the interest sentence is declared replaced (overwrite 1), and start, rate, additions, extension and divisor are all under it. Proof + approval, disbursement status, pro-rata reallocation, settlement options and minor rule: follow base or are inherited. Withholding is inherited, but the user tool has no withholding argument. That is not a scored quantity (observation). Against fixed_beneficiary_designation: no conflict.

### factor_ladders

Per policy: factor, effect label, decides, number of tiers, and whether each non-fall-through tier is multi-source.

- **P1** (6 factors: 4 parameter, 2 method; cross_difficulty = whole).
  - withdrawal_free_percentage: parameter, c_free_pct, 3 tiers (0.15 / 0.12 / 0.10), age ∧ schedule year.
  - withdrawal_free_amount_usage: method, c_counted, 3 tiers (exclude RMD / exclude waiver / count all).
  - withdrawal_charge_age_cap: parameter, c_capped, 3 tiers (cap 0.02 / 0.03 / none).
  - withdrawal_charge_whole_life_relationship: parameter, c_rel_reduction, 3 tiers (0.005 / 0.0025 / 0), whole holding ∧ whole ledger.
  - withdrawal_charge_grading: method, c_graded, 3 tiers (monthly / quarterly / as-is), age ∧ schedule year.
  - withdrawal_charge_late_correction_share: parameter, c_share, 3 tiers (0.5 / 0.75 / 1), lag ∧ age.
  - Bindings are pairwise disjoint and every `decides` is an input. Every tier is stated in the rule and implemented. No two tiers share a value. Each fall-through equals the baseline.
  - baseline.rule: 5 sentences, all in the rule, params listed. It is self-sufficient.
- **P2** (5 factors: 3 parameter, 2 method; cross_difficulty = income).
  - surrender_interest_end_date: method, b_days, 3 tiers. Tier 1 reads a different date (handling date), so I accept the method label.
  - surrender_interest_closing_years_addition: parameter, 3 tiers, age ∧ schedule year.
  - surrender_interest_income_relationship: parameter, 3 tiers, income holding ∧ income ledger.
  - surrender_interest_withdrawal_history: parameter, 3 tiers (+0.001 / −0.001 / 0), disjoint as stated.
  - surrender_interest_convention: method, 3 tiers (simple / daily-compound nominal / effective). These are distinct algorithms.
  - baseline.rule: 3 sentences in the rule. It is self-sufficient.
- **P3** (6 factors: 4 parameter, 2 method; cross_difficulty = whole).
  - Same structure as P1 for free percentage, usage, cap, relationship and grading.
  - Plus surrender_premium_tax_recovery: parameter, 3 tiers (0.005 / 0.0235 / 0), issue state ∧ tax registration. These are real California annuity premium-tax rates.
  - baseline.rule: 5 sentences in the rule. It is self-sufficient.
- **P4** (4 factors: 3 parameter, 1 method; cross_difficulty = whole).
  - renewal_value_band: parameter, 4 tiers (0.003 / 0.002 / 0.0015 / 0).
  - renewal_value_measure_date: method, 3 tiers (date of death / less waiting withdrawal / renewal date).
  - renewal_persistency: parameter, 3 tiers, first-period ∧ withdrawal history.
  - renewal_whole_life_relationship: parameter, 3 tiers, whole holding ∧ ledger.
  - Observation O-C5: renewal_value_band's literal fall-through ("otherwise 0") is not the whole factor baseline (`P('high_band_rate_addition') if r_measure >= P('high_band_threshold') else 0`). The baseline reproduces the ladder's lower two tiers. Substituting the baseline is still well defined and honest to baseline.rule, so there is no consequence for the weight test.
  - baseline.rule: 2 sentences in the rule. It is self-sufficient.
- **P5** (5 factors: 3 parameter, 2 method; cross_difficulty = whole, income).
  - valuation_date_source: method, 3 tiers. These are different source records.
  - valuation_rate_split: method, 3 tiers. These are different formulas.
  - valuation_value_band: parameter, 3 tiers.
  - valuation_age_addition: parameter, 3 tiers, age at death ∧ years held.
  - valuation_income_relationship: parameter, 3 tiers, income holding ∧ ledger.
  - baseline.rule: 2 sentences in the rule. It is self-sufficient.
- **P6** (6 factors, labelled 3 parameter / 3 method; cross_difficulty = whole).
  - claim_interest_start: method, 3 tiers. These are different anchor records.
  - claim_interest_base_rate: parameter, 3 tiers.
  - claim_late_settlement_addition: parameter, 3 tiers, approval lag ∧ state.
  - claim_earlier_claim_coordination: parameter, 3 tiers, whole ledger.
  - claim_interest_end_extension: labelled method, 3 tiers (+3 / +1 / +0 days).
  - claim_interest_day_count: labelled method, 3 tiers (divisor 360 / 366 / 365).
  - **F-C3: the last two only substitute a different number into the same formula `share × rate × days / divisor` (a day offset, a divisor). By the skill's test they are parameters labelled method.** If they are relabelled, P6 is 5 parameter + 1 method, which is still within bounds. The mislabel itself is a listed SOURCE-FACTOR failure.
  - baseline.rule: 4 sentences in the rule. It is self-sufficient.
- Realism (observation O-C6): every ladder is a synthetic business rule. The conditions I judge least likely to be weighed by a fixed-annuity carrier for that quantity are:
  - P2 surrender_interest_convention, which chooses the compounding convention (simple vs daily-compound vs effective) by the annuitant's age;
  - P1/P3 grading granularity (monthly vs quarterly) chosen by age;
  - P6 day-count divisor by state, and the extension by mailing days;
  - P2 closing-years rate addition on surrender interest.
  - I record these as observations, not REDs, because I cannot demonstrate that no carrier in this line uses them.
- Counts by chain: P1–P3 include multi-source factors and cross-difficulty factors (whole, income). P4–P6 include multi-source factors and cross-difficulty factors (whole, income). Bounds of 4–6 factors per computation, ≥2 parameter and ≥1 method: met by all six, including after the F-C3 relabel.

### findings

- **F-C1 — SOURCE-POLICY RED (undeclared overrides).**
  - Symptom: the extended rules change base-governed quantities without naming the base sentence.
  - (a) Base fixed_surrender: "The surrender is effective on the date the signed request is received in good order; interest is credited to that date." Base fixed_interest_crediting: interest is credited "on the date of any … surrender … for the part year since the last crediting". P2 ends the part year "through the handling date" or "through the day after the receipt date". P3 works the CSV out "on the date the surrender is handled". Neither P2's nor P3's `overwrite` names these sentences.
  - (b) Base fixed_evt_withdrawal: "From contract year free_withdrawal_first_contract_year, withdrawals … are free". P1's "Its free amount is free_withdrawal_pct times the contract value on the contract anniversary that opened the withdrawal's contract year …" and P3's "The surrender free amount is free_withdrawal_pct times the contract value on the latest contract anniversary …" grant a free amount in every contract year. The gate is not named (dropped branch).
  - Demonstration of (b) in a general situation: a SecureRate contract (free_withdrawal_first_contract_year = 2) with a withdrawal or surrender in contract year 1. Base gives a free amount of 0. P1/P3 give 10% of the initial premium. Different charge.
  - Bears on: task 0 (claims P1, P2, P3). The consequence of (a) on task 0's world is demonstrated in 0.md. (b) has no consequence on task 0's world (contract years 5–6).
  - Affected: fixed.extended.yaml P2 `overwrite`, P3 `overwrite`, P1 `overwrite`.
- **F-C2 — SOURCE-POLICY RED (prerequisite sentence scope, E4).**
  - Symptom: P6's prerequisite sentence waits on valuation interest "credited through the date due proof of death was received". The edge `condition` says "an interest credit entry whose interest period closes on the valuation date". P5's rule defines the valuation date in three tiers, only one of which is a proof-receipt date for this contract.
  - Two passages: P6 "…not paid until the contract carries the valuation interest credited through the date due proof of death was received." versus P5 "…where no such certificate exists and this contract's death claim was received more than late_claim_days days after the date of death, the date of death plus late_claim_days days".
  - Same situation, different conclusions: death on D, claim with certificate received on D + 400, no whole life certificate. P5 credits interest closing on D + 365. P6's sentence requires interest credited through D + 400. P5's write can never satisfy P6's gate, so the root is either unpayable or computed off a non-P5 valuation.
  - The sentence also reuses the base phrase "date due proof of death is received", which P5's overwrite 1 superseded.
  - Bears on: task 1 (claims P4–P6). The task-world consequence is assessed in 1.md.
  - Affected: P6 `rule` sentence 2 / `prerequisite[0].policy_source` versus `condition`.
- **F-C3 — SOURCE-FACTOR RED (mislabelled effect).**
  - P6 claim_interest_end_extension and claim_interest_day_count are labelled `method`, but their tiers substitute a number (+3/+1/+0 days; 360/366/365) into one unchanged formula.
  - Bears on: task 1.
  - Affected: P6 `factors[4].effect`, `factors[5].effect`.
- **O-C3 — observation (terminal state vs base event model).**
  - confirm_full_surrender sets `termination_date` = today. Base fixed_contract_surrendered defines termination_date as "the date the signed surrender request was received in good order".
  - The tool zeroes contract_value and writes fixed_surrender_paid = CSV, but writes no fixed_surrender_charge_assessed (full_surrender) row and no premium-tax row. Base event fixed_surrender_charge_assessed expects one for a charged surrender, so the ledger does not balance.
  - The agent controls neither, so this does not create multiple solutions.
- **O-C4 — observation.** Day-count wording "from … through …"; see rule_compute_equivalence.
- **O-C5 — observation.** P4 band ladder fall-through versus baseline; see factor_ladders.
- **O-C6 — observation.** Realism of some ladder conditions; see factor_ladders.
- **O-C7 — observation.** P4 "holds an Ashgrove whole life policy" (no status qualifier, present tense) versus P1/P3 "in-force" and P5 "held". Assessed in 1.md.

## closing_checklist

Written after both task files' comparison sections; see the post-reveal section appended below.

### post-reveal status (written after both tasks' source_gt_comparison; nothing above this heading was changed after the reveal)

**The difficulty is not closed: not all four relationships PASS for every task.**

Step 4 checklist status:

- Per-task files correspond one-to-one with the tasks: `0.md`, `1.md`, with `_difficulty.md` alongside. This is the first revision. Each has a comparison section; neither carries an overall PASS.
  - task 0: SOURCE-POLICY RED (F-C1(a), demonstrated on its world) and SOURCE-FACTOR RED (free_portion_amount stamp; false factor_trace figure).
  - task 1: SOURCE-FACTOR RED (F-C3) and SOURCE-POLICY RED at charter level (F-C2, weak consequence on its world).
- Coverage and scope. charter_scope task 0 = {P1, P2, P3} with tools {assess…e9f9c059, credit_surrender…88d8dad0, confirm…fa1c6fc8}. Task 1 = {P4, P5, P6} with {renew…14f04954, credit_death…0cf0ffa2, settle…569ae0ca}. The scopes are pairwise disjoint and jointly cover all six extended policies and all six task tools. Six distinct uuid8 tails. ✓
- Trees. Each task has 2 prerequisite problems, 2 value_input edges (≥ 1), one owner=user root, and no cycle. The whole-difficulty graph P1→P2→P3, P4→P5→P6 is a DAG with no cross-task edge. ✓
- Factors. Every computation has a self-sufficient baseline giving a definite number different from gold: 1618.23 / 3056.66 / 148860.91 / 0.0455 / 14411.03 / 1157.03. It has 4–6 factors, each bearing weight on its task's world. The exceptions:
  - task 0: P1's free-percentage and usage factors are readable off a seeded stamp;
  - task 1: two P6 factors are mislabelled `method`.
- Undeclared overrides (F-C1) and the P6 prerequisite-sentence scope (F-C2) remain open in the charter.
- Gates: the instantiation-stage gate snapshot in the brief was taken on artifacts whose hashes are unchanged at the end of this audit (extended `d3c7e7a0…`, tools `15a06086…`, tasks/0.json `547d76b2…`, tasks/1.json `336c865a…`). There is no final post-rework form to re-run against.

Per-task verdicts:
- task0 = SOURCE-POLICY RED + SOURCE-FACTOR RED
- task1 = SOURCE-FACTOR RED + SOURCE-POLICY RED (charter F-C2)

## revision_2

### charter_global_frozen (revision 2)

- Inputs:
  - fixed.extended.yaml sha256 `d3faada49dc0634912504a33442e79da146b0615d37808db805581ed62956483`. **Changed** from round 1 (`d3c7e7a0…`), so every charter-global section below is re-derived in full, not carried forward.
  - task_tools.py `15a060860f596d8f1018b895d95e589fee54ad0e881e5f3c54421e292eb3ca00`. Unchanged, so the tool-body conclusions are carried forward on that hash.
  - Base copy (lines 1–1019) is still byte-identical to blueprint/products/fixed.yaml.
- Frozen at 2026-10-08 (round-2 pass), before tasks/0.json or tasks/1.json of this round was opened. Auditor: same independent auditor as round 1.
- Gate snapshot after rework (supplied by the orchestrator): EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; CACHE-DIFF INFO; traceability deferred. Input is complete.
- contamination_disclosure: round-1 GT for both tasks is already in this auditor's context, which is inherent to a re-audit. The round-2 derivation below was redone from the round-2 charter and the rebuilt masked views. I evaluated the round-2 compute independently and cross-checked it against my prose derivation. I did not read the round-2 task JSONs before this freeze. The round-1 text above is left untouched.

### policy_conflict_scan (r2)

- Same six policies, tools and chains as round 1. Subjects, triggers and cross-category reads are unchanged.
- New overlaps from the rework:
  - P2 and P3 both now supersede the base fixed_surrender sentence "The surrender is effective on the date the signed request is received in good order; interest is credited to that date." The replacements address different quantities, each of its own policy. P2's governs the end of the part-year surrender interest. P3's ("The surrender takes effect on the date it is handled, and the cash surrender value is worked out on that date.") governs the effective date and the CSV's evaluation date. Neither replacement speaks to the other's quantity, and the merged semantics are unique: interest end per P2's tiers, CSV at the handling date.
  - P2's new overwrite 4 names the base fixed_interest_crediting clause "on the date of any withdrawal, surrender, death benefit payment or annuitization for the part year since the last crediting". That clause is broader than P2's subject, while the replacement speaks only to the surrender. Read as scoped to P2's computed quantity (as every overwrite is), it leaves withdrawal, death and annuitization crediting under base or under P5's own rule. **Observation O-R2-1**: no consequence in either world.

### rule_compute_equivalence (r2)

- P1. New sentence: "Its free amount, where the withdrawal fell in contract year free_withdrawal_first_contract_year or later, is … (the initial premium in the first contract year) …; where the withdrawal fell in an earlier contract year its free amount is nothing." New binding c_cy_w = contract year of the withdrawal. c_free_rem = 0 below the first free year, otherwise uses initial_premium in year 1, else the anniversary value. compute_basis quotes the sentence for c_cy_w and c_free_rem. Equivalent. The baseline.rule carries the same sentence and baseline.params now lists free_withdrawal_first_contract_year.
- P3. Same structure (a_cy, a_free_rem); equivalent. New rule sentence "The surrender takes effect on the date it is handled, and the cash surrender value is worked out on that date." is the compute_basis of a_cv and is also baseline.rule sentence 1.
- P2. Rule and compute are textually unchanged. Equivalent as in round 1.
- P4. The rule now says "the owner has an Ashgrove whole life policy on record, whatever its current status". Compute is `EXISTS('whole')`. Equivalent, with no interpretive gap left.
- P5. Unchanged.
- P6. The rule's prerequisite sentence is reworded (see below). Compute is unchanged. Equivalent.
- Every other binding is identical to round 1; I re-read each one.

### action_binding_and_uuids (r2)

- Carried forward on the unchanged task_tools.py hash: six distinct (tool, computes) claims, independent uuid8 tails, no docstring sequence words beyond the self-describing "Afterwards", and no prerequisite checks in tool bodies.

### prerequisite_graph (r2)

- Unchanged shape: P1→P2→P3 and P4→P5→P6, acyclic. All four edges are state-form value_input, with gates b_cv, a_cv, v_growth and s_db. Each `policy_source` is verbatim in its blocked rule.
- E4 condition now reads "The contract shows an interest credit entry whose interest period closes on the valuation date of the death benefit, credited after the owner's death claim was received, and the contract value includes it." That matches the sentence's scope.

### prerequisite_sentences (r2)

- E1, E2, E3: textually unchanged, PASS as in round 1.
- **E4**: "A beneficiary's death benefit share is not paid until the contract carries the valuation interest credited through the valuation date of the death benefit." The connective is "not until". The state is record-visible (an interest credit whose period closes on the valuation date). It names no tool or id. Its scope equals the condition and P5's own term ("The valuation date of the death benefit is, where …"). In the late-claim tier (valuation date = date of death + late_claim_days) the sentence now waits on exactly what P5 writes. Exactly one write (P5) brings it about. **PASS. F-C2 closed.**

### override_declarations (r2)

- **F-C1(a) closed.**
  - P2 overwrites 3 and 4 name base fixed_surrender "The surrender is effective on the date the signed request is received in good order; interest is credited to that date." and base fixed_interest_crediting "on the date of any withdrawal, surrender, … for the part year since the last crediting". Both are replaced by the end-date tiers.
  - P3 overwrite 5 names the same fixed_surrender sentence and replaces it with "The surrender takes effect on the date it is handled, and the cash surrender value is worked out on that date."
  - No base sentence now ties the surrender interest or the CSV to the receipt date.
- **F-C1(b) closed.** P1's and P3's rules restore the free_withdrawal_first_contract_year gate and the first-year initial-premium base verbatim in substance. Example: a SecureRate withdrawal in contract year 1 now gets a free amount of nothing in both base and extended. The declared overwrite clauses (free percentage, RMD counting) are unchanged.
- I repeated the sentence-by-sentence sweep of every base_policy_refs entry for all six policies. No other base sentence is handled differently without being named. Round-1 observations stand: the P1 waiver-claim breadth, and the nonforfeiture floor having no charter figure.

### factor_ladders (r2)

- P1/P2/P3/P5: unchanged structure (6/5/6/5 factors, label counts as in round 1, ladders ≥3 tiers, distinct outcomes, stated in rule, fall-through = baseline).
- P1/P3 baselines now include the first-free-year gate. They are still self-sufficient and definite.
- P4: 4 factors, 3 parameter / 1 method. The renewal_whole_life_relationship ladder text now reads "on record, whatever its status". O-C5 (band fall-through vs two-branch baseline) is unchanged and deliberately retained. It is a non-RED observation with no weight consequence.
- **P6: claim_interest_end_extension and claim_interest_day_count are now `effect: parameter` with `value` tiers (+3/+1/0 days; 360/366/365). F-C3 closed.**
  - P6 now has 5 parameter and 1 method factor (claim_interest_start, which chooses an anchor record: date of death / claim receipt / valuation date). Bounds are met.
- Per chain: multi-source factors are present in each. Cross-difficulty factors: whole and income in P1–P3; whole and income in P4–P6.
- O-C6 realism notes are unchanged and deliberately retained (non-RED).

### findings (r2)

- F-C1(a), F-C1(b), F-C2, F-C3: **closed**, with evidence as above.
- O-C7: **closed**. P4 now states "whatever its current status".
- O-C3: partly resolved.
  - P3 now declares that the surrender takes effect on the handling date, which matches the tool's termination_date = today.
  - Residual: the base event field gloss (fixed_contract_surrendered.termination_date "the date the signed surrender request was received in good order") still reads otherwise.
  - Still residual: no full-surrender charge or premium-tax ledger rows.
  - Non-RED: the agent controls neither.
- O-C4, O-C5, O-C6: unchanged, as the reworker stated; non-RED.
- New O-R2-1 (observation): P2's overwrite 4 names a base clause broader than its subject. No consequence.
- No new RED found in the charter.

### closing_checklist (r2; written after both r2 comparisons)

- One-to-one files: `0.md`, `1.md` and `_difficulty.md`, with the round-1 text preserved and `## revision_2` appended to each. Both r2 comparison sections carry PASS. ✓
- Coverage and scope: task 0 = {fixed_ext_missed_withdrawal_charge, fixed_ext_surrender_part_year_interest, fixed_ext_surrender_value}; task 1 = {fixed_ext_claim_renewal_rate, fixed_ext_death_valuation_interest, fixed_ext_death_claim_settlement}. They are pairwise disjoint and jointly complete over the six extended policies and six task tools. The uuid8 tails are independent and unchanged. ✓
- Trees: each has 2 prerequisite problems, 2 value_input edges, an owner=user root, and no cycle. The difficulty graph is a DAG. ✓
- Factors: every computation has a self-sufficient baseline giving a definite number different from gold (1618.23 / 3056.66 / 148860.91 / 0.0455 / 14411.03 / 1157.03). Factor counts are 6/5/6/4/5/6, with labels honest after the P6 relabel and every factor bearing weight on its task's world. No stamp remains. Each task has multi-source factors and cross-difficulty factors (whole, income) with their rows seeded. ✓
- Round-1 REDs: F-C1(a), F-C1(b), F-C2, F-C3, task 0 findings 2 and 3, and task 1 finding 1 are verified closed. Observations O-C7 and task 1 observation 6 are also closed. O-C4, O-C5, O-C6 and task 1 observation 4 are retained unchanged and are non-RED. No new RED, no regression.
- Gates: the orchestrator's post-rework snapshot is all green (traceability deferred to the render stage). It was taken on the hashes audited here: extended `d3faada4…`, tools `15a06086…`, tasks/0.json `c682e9a6…`, tasks/1.json `ad1f7583…`.

**The difficulty passes the source-layer audit (revision 2).**

Per-task verdicts (r2):
- task0 = PASS
- task1 = PASS

## revision_3

### charter_global_frozen (revision 3)

- Inputs:
  - fixed.extended.yaml `d3faada49dc0634912504a33442e79da146b0615d37808db805581ed62956483`. **Unchanged** from revision 2, so § revision_2 policy_conflict_scan, rule_compute_equivalence, prerequisite_graph, prerequisite_sentences, override_declarations and factor_ladders are carried forward by reference on that hash.
  - task_tools.py `377c9f8d17e541ba7f5d7854cb1298f1a53e902c4aa97d82cadf041c8d4dce3e`. **Changed** from `15a06086…`, so § action_binding_and_uuids is re-derived below.
- Frozen before the revision-3 tasks/0.json (`7581cbaa…`) or tasks/1.json (`6874e065…`) was opened.
- Trigger: validate_scenario rejected the previous module ("forbidden 'from datetime' (real clock)").
- Orchestrator gate snapshot: EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE / TRACEABILITY OK; CACHE-DIFF INFO; validate_scenario clean for this difficulty.
- contamination_disclosure: GT of rounds 1–2 is known to this auditor (inherent to a re-audit). Nothing from the revision-3 task JSONs was read before this freeze.

### action_binding_and_uuids (r3, re-derived)

- The module imports only `from erlbench import ToolContext, tool`. No datetime, time or random. The module docstring is unchanged.
- Five tools are unchanged against the revision-1/2 text: assess_missed_withdrawal_charge_e9f9c059, credit_surrender_interest_88d8dad0, confirm_full_surrender_fa1c6fc8, credit_death_valuation_interest_0cf0ffa2, settle_death_benefit_share_569ae0ca. I checked the decorators (owner, rw), signatures, the `make_id` seeds, the `ctx.create` / `ctx.update` field sets and the receipt f-strings. All are identical.
- renew_guarantee_period_14f04954:
  - Decorator `owner="agent", rw="write"`, signature, docstring and receipt format ("Contract <id> renewed: rate <r:.4f> from <start> to <end>.") are unchanged.
  - The body now computes the dates without datetime. Start = GP end + 1 day, with month and year rollover and Gregorian leap rule. End = same month and day `years` later, with the day clamped to the month length, so Feb 29 → Feb 28 in a non-leap year. `years` is still parsed from the tier name; it falls back to 1 for a name without a trailing integer. An empty GP end still falls back to `ctx.now()`, which is the runtime clock, not the real clock.
  - **Equivalence test:** I compared old datetime logic against the new body for every GP end date from 1990-01-01 to 2100-12-31, over all six tier names (243,252 cases). There were **0 mismatches** in sc_schedule_start_date, guarantee_period_end_date or the 4-dp rounded rate. The empty-end fallback is also identical.
  - Still checks no eligibility and no prerequisite. No error path or hint is added. Deterministic.
- (target_tool, computes) claims and uuid8 tails are unchanged (e9f9c059, 88d8dad0, fa1c6fc8, 14f04954, 0cf0ffa2, 569ae0ca). Docstrings still name no other tool and state no sequence.
- **Conclusion:** the tool change is behaviour-preserving and introduces no defect. No new RED. Revision-2 charter findings and observations stand unchanged.

### closing_checklist (r3; written after both r3 comparisons)

- Files: `0.md`, `1.md` and `_difficulty.md`, with revisions 1–2 untouched and `## revision_3` appended. Both r3 comparisons PASS. ✓
- Scope, coverage, trees and DAG: unchanged from the r2 checklist. ✓
- Factors: unchanged; all bear weight against honest baselines. ✓
- Tool module: renew_guarantee_period_14f04954 is re-implemented without datetime and is behaviour-identical (243,252-case equivalence, 0 mismatches). The docstring and receipt are unchanged. The tool makes no prerequisite check, and its output depends only on its inputs and `ctx`. The other five tools are unchanged. uuid8 tails are unchanged. ✓
- Revision-2 status: there were no open REDs to close. The validate_scenario blocker that prompted this round is resolved (orchestrator snapshot, including TRACEABILITY OK). No new defect, no regression.
- Gates: the orchestrator's post-rework snapshot was taken on the hashes audited here: extended `d3faada4…`, tools `377c9f8d…`, tasks/0.json `7581cbaa…`, tasks/1.json `6874e065…`.

**The difficulty passes the source-layer audit (revision 3).**

Per-task verdicts (r3):
- task0 = PASS
- task1 = PASS
