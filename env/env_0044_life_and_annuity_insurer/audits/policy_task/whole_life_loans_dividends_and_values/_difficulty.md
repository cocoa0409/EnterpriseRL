# Policy-task audit — whole_life_loans_dividends_and_values / charter-global

## charter_global_frozen

- Frozen: 2026-10-08T07:40Z (pre-reveal hash 655e29ea… before the closing append), before any task's GT was revealed. Auditor: erl-task-policy-audit subagent (Claude Opus 5.5), independent of the instantiating agent.
- Inputs and hashes, checked against the brief:
  - `tasks/whole_life_loans_dividends_and_values/whole.extended.yaml` sha256 `acb3cc416f16665f1bb70c46926206e6b3f9312772130cb0e0e721dbc64dfc6b`
  - `tasks/whole_life_loans_dividends_and_values/task_tools.py` sha256 `1deb19235737efaffb838affa9f6dbfeb4468c0438cf3370dd10d07ce632f15b`
  - `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/whole.yaml`, `blueprint/products/term.yaml` (the cross-category charter read by the term factors), and `erlbench/` plus the restricted-expression evaluator in `skills/erl-task-instantiate/scripts/check_compute.py`, which I used only as a calculator over the masked worlds.
- Readable: the four artifacts above, plus the masked views `/tmp/erl0044_views/whole_life_loans_dividends_and_values/task_{0,1}.masked.json` (frozen_time, user_scenario, initial_state only). Their hashes match the brief: `aa005a69…bd09` and `a0326c14…3bb3`.
- Masked and unread while this section was written: everything in `tasks/*.json` except the masked fields (evaluation_criteria, computations, db_closure, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure), and the difficulty's worklog. Nothing in this section comes from a revealed GT.
- Entry conditions: the brief supplies the gate snapshot (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; traceability deferred) and the masked views with their hashes. The entry conditions are met, so I record no incomplete-input problem. I did not re-run the gates.
- Base section: the base section loaded from `whole.extended.yaml` is semantically identical to `blueprint/products/whole.yaml` for every top-level key (category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies). Only the YAML formatting differs.

### policy_conflict_scan

There are seven extended policies, each with its own `(target_tool, computes)`:

| policy | trigger | target_tool (owner) | computes | prerequisite |
|---|---|---|---|---|
| whole_ext_anniversary_interest_capitalization | state_due | capitalize_loan_interest_55a34971 (agent) | interest_amount | [] |
| whole_ext_offset_interest_extinguished | on_request | extinguish_policy_loan_1349795c (agent) | interest_amount | capitalization (value_input, state) |
| whole_ext_election_accumulation_withdrawal | on_request | withdraw_election_accumulations_2818c877 (agent) | withdrawal_amount | [] |
| whole_ext_reduced_paid_up_face | on_request | elect_reduced_paid_up_64725b60 (**user**) | reduced_face_amount | offset (value_input, state); withdrawal (value_input, state) |
| whole_ext_accumulation_interest_credit | state_due | credit_accumulation_interest_b6da2e99 (agent) | interest_amount | [] |
| whole_ext_anniversary_dividend_deposit | state_due | deposit_anniversary_dividend_704bd37e (agent) | deposit_amount | credit (state_gate, state) |
| whole_ext_net_surrender_value | on_request | complete_policy_surrender_23994b0e (**user**) | net_amount | deposit (value_input, state); credit (value_input, state) |

Overlap scan:
- **Two extended policies override one base clause.** The whole_dividends clause "accumulations are left on deposit and credited interest at dividend_accumulation_rate on each anniversary on the balance held for the whole policy year" is overridden by both the withdrawal policy (the election withdrawal event) and the credit policy (the anniversary credit event). Their subjects are disjoint (`whole_accumulation_withdrawn` vs `whole_accumulation_interest_credited`), so they do not conflict.
- **Both the capitalization and offset policies override the base interest clause** of whole_evt_policy_loan. The subjects are disjoint (capitalization vs offset). Their "interest start" ladders put the ledger dates in a different order of priority. Each is internally coherent for its own event, so this is not a conflict.
- **Latent conflict between offset and net surrender: see finding D-4.** The offset policy explicitly covers the surrender occasion. Its offset_effective_date tier reads "where a surrender request on the policy is on file, to the date that request was received", and its tool enum has `surrender`. The base sentence "A loan is extinguished against the policy values on surrender…" says the loan is extinguished on surrender. The net-surrender rule deducts "the loan balance shown on the policy", and no prerequisite or other sentence orders the two writes. Neither task world exercises this: task 1's loan balance is 0.00.
- Cross-category reads: five policies (capitalization, offset, RPU, deposit, surrender) read `term.issue_date` through `converted_from_term_policy_id`. That is a read only, and it is consistent with the term charter's `term_policy_converted` mapping (`issue_date: termination_date`).
- Scope: the seven policies form two disjoint trees. Tree A: RPU face ← offset ← capitalization, and RPU face ← withdrawal. Tree B: net surrender ← deposit ← credit, and net surrender ← credit. Two trees for M=2 tasks, with no policy shared, would be mutually exclusive and jointly complete. Which task claims which tree is masked (charter_scope) and is checked after the reveal under `closing_checklist`.
- Blueprint claim (observation O-9): the subjects `whole_loan_interest_capitalized`, `whole_accumulation_interest_credited` and `whole_dividend_accumulated` are not in this difficulty's claimed `event_types` list. Only this difficulty claims category `whole`, so no other difficulty overlaps. No relationship consequence.

### rule_compute_equivalence

Sweep of every binding's `compute_basis` quotation against the rule, and back (check 2). Every quoted `compute_basis` string is a verbatim sentence of its policy's rule, and every factor tier named in `factors[].ladder` appears as a rule sentence and as a branch of the `decides` binding. Exceptions and notes:

1. **SOURCE-POLICY RED (D-1): the surrender premium-record window is anchored on the wrong date.**
   - Rule: "judged by the premium payments returned unpaid on the policy ledger and dated within the 24 calendar months **before the surrender effective date**".
   - Compute: `returned_24m: COUNT('whole_transactions', within_months=24, date_field='transaction_date', event_type='whole_premium_payment_returned')`. The evaluator's `_within` anchors `within_months` on `NOW` (frozen_time), not on `effective` (`0 <= MONTHS(d, NOW) < within_months`).
   - Whenever the surrender request was received before the handling day, the two windows differ. A returned payment dated between 24 months before the effective date and 24 months before today is counted by the rule and dropped by compute. The demonstration is in `1.md`, where it changes the scored net amount.
2. **Latent SOURCE-POLICY divergence (D-5): repayment filter in the capitalization and offset interest-start ladders.**
   - Rules: capitalization says "the date of the latest loan repayment made on or before the anniversary that paid loan interest"; offset says "the date of the latest loan repayment that paid loan interest".
   - Compute: `LATEST(... event_type='whole_loan_repaid')` takes the latest repayment of any kind. Only then does it test `float(repayment_interest) > 0` (and, for capitalization, `<= anniversary`). It never looks back to an earlier repayment that did pay interest.
   - Divergent world: two repayments, where the later one paid no interest, or the later one falls after the anniversary. The rule picks the earlier interest-paying repayment; compute falls back to the capitalization anniversary or the paid-to date.
   - Similarly, `advance_date` and `apl_booked` take the latest advance overall and then test `<= anniversary`. The rule's "the latest owner loan advance made after the start of the interest period" would pick the latest one within the period.
   - Neither task world contains a second repayment or a post-anniversary advance (task 0: one repayment, 2026-02-10, with interest 252.18; task 1: the repayment does not feed any scored computation). So no scored value is affected.
3. Rounding (observation O-1): every rule says "rounded half up". `RND` is `round(float(x), n)`, which rounds half to even on a binary float. No scored intermediate in either world sits on an exact half cent or half dollar (checked in each task file), so there is no consequence.
4. Clean sweeps:
   - Withdrawal: the `ledger_deposit` band reads "the deposit as the policy ledger totals it", and its rule sentence repeats "where the balance is at least" for the ledger total. Both readings agree on task 0.
   - RPU: `accumulations_applied`, `offset_principal`, `offset_interest` and `loan_extinguished` read the entries the two prerequisite writes leave, in agreement with "for the election".
   - Credit and deposit: windows are anchored on `NOW`, matching "before the credit/deposit is booked" read as the booking day. Read that way the equivalence holds. Whether it is the only reading is a separate question (finding D-6).
   - Every `baseline.rule` is a verbatim sentence of its rule, and its `baseline.params` keys exist (loan_interest_rate, days_per_year, dividend_accumulation_rate, rpu_min_face_amount, federal_withholding_default_pct).

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (seven distinct tools).
- Docstrings, one business reading each:
  - None names another tool, a policy id, or a sequence position. The ordering-word scan found only "once recorded", "once the deposit is closed", "after any loan and tax withholding" (arithmetic, not sequence) and "rounded … before it is passed" (argument formatting).
  - The withdrawal docstring says the deposit "is applied … to the reduced paid-up insurance the owner is electing". That describes the occasion, not an order (observation O-10).
- Function bodies validate nothing. None reads a prerequisite state, refuses, or hints:
  - `capitalize…` creates the entry and adds to loan_balance.
  - `extinguish…` creates the entry and subtracts principal.
  - `withdraw…` creates the entry and sets the balance to 0.
  - `elect…` updates status, face, nonforfeiture_option and default_date.
  - `credit…` and `deposit…` create the entry and add to the balance.
  - `complete…` updates status, termination date and balance 0, and creates the payment.
- uuid8s: 55a34971, 1349795c, 2818c877, 64725b60, b6da2e99, 704bd37e, 23994b0e. They are pairwise unrelated, with no shared prefix or suffix, no sequence, and no reuse. PASS.

### prerequisite_graph

- `prerequisite` is filled on all seven policies. There are five edges, each pointing at a policy id in this file and none at itself. The graph is acyclic: two trees of depth ≤ 2.
- `policy_source` is verbatim in the blocked policy's own rule for all five edges. A substring check returned True for each.
- `form: state` on all five, with no `fallback_reason`, which is correct for the state form.
- `resolved_by` equals the depended-on policy's `target_tool` on all five.
- `kind`/`gate`:
  - value_input `interest_start` (offset), `offset_principal` and `accumulations_applied` (RPU), and `balance` (surrender, both edges) are real bindings of each policy's compute.
  - The deposit edge is `state_gate` with `gate: whole_transactions.interest_period_end`. That is a ledger column, not an eligibility gate; extended policies carry no `eligibility` list (observation O-4). Its weight is demonstrated by order in `1.md`.
- `condition` vs sentence:
  - Offset ← capitalization (O-2). The condition requires a capitalization at `values_as_of_date` "of a policy with a loan balance". The sentence requires one "for the most recent policy anniversary on which loan interest was owed". Corner world where they part: a policy whose only loan was advanced after the most recent anniversary has a loan balance (so the condition is unmet) but no anniversary on which interest was owed (so the sentence imposes nothing). This is an observation, because neither task world is that corner and the agent-facing sentence governs.
  - RPU ← offset (O-3). The condition adds `offset_reason nonforfeiture`. The sentence says "a loan offset entry for it", and the rule elsewhere says "the loan offset entry for the election", so it is consistent. Read literally, the sentence presupposes a loan: on a policy with no loan it would block forever. This is an observation; task 0 has a loan.
  - RPU ← withdrawal, surrender ← deposit, surrender ← credit, deposit ← credit: the conditions match their sentences.
- No authoring-viewpoint wording ("in this task", "at the opening") appears in any `prerequisite` field.

### prerequisite_sentences

Four-point test on each edge:

| # | blocked policy | sentence | connective | waited-on state (record-visible) | the one write that brings it about |
|---|---|---|---|---|---|
| 1 | offset | "The interest extinguished at an offset is fixed only after the policy ledger carries a capitalization entry for the most recent policy anniversary on which loan interest was owed." | only after | a `whole_loan_interest_capitalized` row with `interest_period_end` = that anniversary | capitalize_loan_interest (the only write creating that event type) |
| 2 | RPU face | "The reduced paid-up face is fixed only after the loan balance shown on the policy stands at zero with a loan offset entry for it on the policy ledger." | only after | `loan_balance` 0.00 and a `whole_loan_offset` row | extinguish_policy_loan (a repayment could zero the balance but leaves no offset entry; no other write books an offset) |
| 3 | RPU face | "The reduced paid-up face is not worked out until the dividend accumulation balance shown on the policy stands at zero with an accumulation withdrawal entry for the election on the policy ledger." | not … until | `dividend_accumulation_balance` 0.00 and a `whole_accumulation_withdrawn` row | withdraw_election_accumulations (complete_policy_surrender also zeroes the balance but books `whole_cash_value_paid`, not a withdrawal entry, and is not "for the election") |
| 4 | deposit | "A dividend is placed on deposit at an anniversary only after the interest credit for the policy year that anniversary closes stands on the accumulation ledger." | only after | a `whole_accumulation_interest_credited` row for that anniversary | credit_accumulation_interest |
| 5 | surrender | "The net cash surrender value is fixed only after the accumulation ledger carries the deposit of the dividend declared at the most recent policy anniversary." | only after | a `whole_dividend_accumulated` row for that anniversary | deposit_anniversary_dividend |
| 6 | surrender | "The net cash surrender value is not worked out until the accumulation ledger carries the interest credit for the policy year closed by the most recent anniversary." | not … until | a `whole_accumulation_interest_credited` row for that anniversary | credit_accumulation_interest |

- Wording: each sentence names states in the ledger's own words ("capitalization entry", "loan offset entry", "accumulation withdrawal entry", "interest credit", "deposit of the dividend"). None names a tool, a policy id, a snake_case token or a row id.
- Single statement: each blocked rule carries the dependency once. No depended-on rule restates the sentence. The capitalization rule never mentions offsets, the credit rule never mentions deposits or surrenders, and the deposit rule never mentions surrender.
- Derivation, one reading per edge:
  1. The sentence names a capitalization entry. Only the capitalization rule ("…it is added to the loan principal as a single capitalization entry dated that anniversary") describes a write that leaves one.
  2. The sentence names a zero loan balance with an offset entry. Only the offset rule ("…is extinguished … as one loan offset entry") describes such a write.
  3. The sentence names an accumulation withdrawal entry for the election. Only the withdrawal rule ("When the owner elects reduced paid-up insurance, the whole dividend accumulation deposit is withdrawn … as one accumulation withdrawal entry") describes one.
  4. and 6. The sentences name an interest credit for the closed year. Only the credit rule ("…as one interest credit entry dated that anniversary") describes one.
  5. The sentence names the deposit of the declared dividend. Only the deposit rule ("…placed on deposit … as one dividend deposit entry dated that anniversary") describes one.
- Undeclared cross-problem orders: a scan of every extended rule for before/after/first/until/only/prior found only the six sentences above, plus temporal or arithmetic uses (issue-date series cut-offs, "after the start of the interest period", "within interest_billing_days … after the anniversary"). None orders two problems.
- Base sentence stating an order (O-11): whole_reduced_paid_up_election says "Any loan is extinguished against the cash value first". The extended RPU rule carries its own prerequisite sentence (#2), so no tree rests on the base sentence. This is an observation only.

### override_declarations

Sentence-by-sentence sweep against each `base_policy_refs` entry (finding half only):

- **capitalization**
  - Refs `whole_evt_loan_interest_and_repayment`, `whole_evt_policy_loan`.
  - "Loan interest for the policy year is due on the anniversary" — followed ("billed on that anniversary").
  - "interest not paid by the anniversary is capitalized … on that anniversary and itself bears interest" — handled differently (31-day billing window). Named in overwrite.
  - "Interest accrues at loan_interest_rate, simple, for actual calendar days over 365…" — handled differently: series rate, continuity reduction, set-apart pieces, billing-mode part of a year. Named in overwrite. The `replaced_by` text spells out only the series-rate part; the other deviations sit in the rule under the same named clause (O-5).
  - Repayment-order, minimum-repayment, default and notice sentences — not touched.
- **offset**
  - Refs `whole_evt_loan_interest_and_repayment`, `whole_death_claim`, `whole_evt_policy_loan`, `whole_reduced_paid_up_election`.
  - The interest-accrual clause is named and replaced.
  - "A loan is extinguished against the policy values on surrender, death, … nonforfeiture … or loan default" — followed.
  - Death-claim "less the loan balance and interest accrued to the date of death" — compatible with the date-of-death tier.
  - RPU-election "Any loan is extinguished against the cash value first" — followed.
- **withdrawal**
  - Refs `whole_dividends`, `whole_reduced_paid_up_election`.
  - The whole-year crediting clause is named. Its `replaced_by` gives part-year interest but not the rate ladder, which lives in the rule (O-5).
  - "The owner may withdraw accumulations … at least accumulation_withdrawal_min unless the whole balance is withdrawn" — the whole balance is withdrawn, so this is followed.
  - Tax sentence — no cash is paid, so it does not apply.
- **RPU face**
  - Refs `whole_reduced_paid_up_election`, `whole_grace_apl_and_nonforfeiture`, `whole_dividends`.
  - "the reduced face is the net cash value divided by rpu_nsp_per_thousand times 1,000, rounded to the dollar, and must be at least rpu_min_face_amount" — named and replaced. The new net-cash-value composition, including the dropped-in-place paid-up additions, the termination and partial-year dividends, and principal plus interest, is all declared in `replaced_by`.
  - The `whole_grace_apl_and_nonforfeiture` formula `net_cash_value: guaranteed_cash_value + pua_cash_value + dividend_accumulation_balance - loan_balance` is not named (O-6). Its subject is `whole_nonforfeiture_applied`, the grace-end default, not the in-force election `whole_reduced_paid_up_elected`, so it does not govern this event.
  - "dividends continue on the reduced face" — not touched.
- **credit**
  - Refs `whole_dividends`. The same crediting clause is named. `replaced_by` states only the size band (O-5), and the rule carries the full ladder. Base formula `accumulation_interest` is superseded with it.
- **deposit**
  - Refs `whole_dividends`. "accumulations are left on deposit" is named and replaced by the adjusted amount.
  - The earlier base sentence "the dividend declared by the Board for a policy year is credited on the anniversary ending that year" is not separately named, although the amount placed on deposit is no longer the declared amount (O-7). The named clause is the one that governs what an accumulate-option policy places on deposit, so I count the override as declared.
- **net surrender**
  - Refs `whole_surrender`, `whole_dividends`. The gross/net sentence is named and replaced. Its `replaced_by` declares accumulation interest, termination dividend, "less the loan balance shown" (the accrued loan interest the base deducted is dropped — declared by replacement) and the premium refund.
  - The effective-date, signature, tax and deferral sentences are followed.

Disguised forms:
- No anonymous intermediate: every changed intermediate has a declared name.
- No 0/1 multiplier on an amount fixed by base.
- No dropped base branch.

**No undeclared override found.** The consequence half (whether any task acquires a second answer from a base sentence) is checked in each task file.

### factor_ladders

Counts are per computation: P = `parameter`, M = `method`, X = `cross_difficulty`.

| policy | factors (label) | P | M | X | every ladder ≥ 3 disjoint tiers in rule & compute | fall-through = baseline |
|---|---|---|---|---|---|---|
| capitalization | policy_series_rate (P), continuous_coverage_reduction (P, term), interest_period_start (M), late_owner_advance (M), late_automatic_premium_loan (M), billing_mode_interest_measure (M) | 2 | 4 | 1 | yes | yes |
| offset | offset_policy_series_rate (P), offset_continuous_coverage_reduction (P, term), offset_interest_start (M), offset_effective_date (M, 4 tiers), offset_billing_mode_measure (M) | 2 | 3 | 1 | yes | yes |
| withdrawal | large_deposit_increment (P), long_deposit_increment (P), withdrawal_frequency_reduction (P), loan_activity_reduction (P), accumulation_interest_start (M), accumulation_billing_mode_measure (M) | 4 | 2 | 0 | yes | yes |
| RPU face | termination_dividend_scale (P, term), termination_dividend_loan_cut (P), termination_dividend_application (M), partial_year_dividend_share (P), paid_up_additions_treatment (M) | 3 | 2 | 1 | yes | yes |
| credit | credit_large_deposit_increment (P), credit_long_deposit_increment (P), credit_withdrawal_frequency_reduction (P), credit_loan_activity_reduction (P), credit_half_year_movements (M) | 4 | 1 | 0 | yes | yes |
| deposit | additions_dividend_method (labelled M), large_policy_increment (P), interrupted_premium_reduction (P), continuous_coverage_increment (P, term) | 3 | 1 as labelled, **0 honest** | 1 | yes | yes |
| net surrender | surrender_termination_dividend_scale (P, term), surrender_premium_record_cut (P), unearned_premium_refund (M), surrender_accrual_start (M) | 2 | 2 | 1 | yes | yes |

- Binding sets are disjoint within each policy. No factor's `decides` is `result`.
- Multi-source factors: every continuity, termination or duration ladder forks on `coverage_months >= X and not F('reinstatement_date')`, two conditions over distinct records. The interest-start and set-apart ladders also fork on compound tests. So both trees reach a multi-source factor.
- Cross-difficulty factors read `term_holdings.issue_date` of the converted term policy. Tree A reaches 3 such factors and tree B reaches 2.
- No two tiers of any ladder select the same value or method. partial_year_dividend_share's middle tier gives months/12 ∈ {1/12…5/12}, which never equals 0.5 or 0.

Label honesty:
- **SOURCE-FACTOR RED (D-3): `additions_dividend_method` is labelled `method` but is a parameter.** Its three tiers compute `declared / base_face × additions_face × s` with s = 1, 0.5, 0 ("…the additions dividend is the declared dividend divided by the base face and multiplied by the paid-up additions face … where it shows additions bought at a single anniversary, the additions dividend is half that; where it shows none, there is no additions dividend"). It is one formula with a different number. With it relabelled, `whole_ext_anniversary_dividend_deposit` has **0 honest `method` factors**, below the floor of 1. The demonstration is in `1.md`.
- The remaining `method` labels change the algorithm or the measured quantity, so they are honest:
  - interest_period_start, offset_interest_start, accumulation_interest_start, surrender_accrual_start select which ledger date opens the accrual.
  - late_owner_advance and late_automatic_premium_loan split principal into separately timed pieces.
  - offset_effective_date selects the end date by occasion.
  - termination_dividend_application selects NCV inclusion, a separate purchase of additions outside the rounding, or cash.
  - paid_up_additions_treatment selects exclusion, dividend cash, or cash value.
  - credit_half_year_movements selects which ledger aggregate joins the base.
  - unearned_premium_refund selects a per-mode refund formula.
  - The billing-mode measures change the day-count convention.

Realism of conditions and outcomes:
- **SOURCE-FACTOR RED (D-2): unreal condition — the premium billing mode decides how interest accrues.** The three factors are `billing_mode_interest_measure` (capitalization), `offset_billing_mode_measure` (offset) and `accumulation_billing_mode_measure` (withdrawal). They make the part of a year for which policy-loan interest, or dividend-accumulation interest, is charged or credited depend on the premium billing mode: whole months on monthly EFT, whole quarters on quarterly, actual days otherwise, with "a remaining part month/quarter not being charged".
  - No whole-life carrier weighs the premium payment mode when it accrues policy-loan interest or accumulation interest. Loan interest accrues under the loan provision (daily simple, or annual in advance or arrears). Accumulation interest is credited at the declared rate, pro rata by days or completed policy months, whatever way the premium is paid.
  - The condition "the policy pays by monthly EFT draft" / "is billed quarterly" is therefore not a condition this line of business weighs for this quantity. The ladder is unreal. Its weight on task 0 is demonstrated in `0.md`.
- Recorded as observations (O-8), because they are unusual but have a recognisable business analogue:
  - The loan-rate reduction for 20/30 years of continuous coverage (a loyalty concession).
  - The interest-free period for an owner advance taken within 30 days before the anniversary.
  - Returned premium payments cutting the anniversary dividend placed on deposit, or the surrender termination dividend (a persistency-bonus analogue).
  - Size, duration and additions adjustments applied on top of a "declared" dividend rather than inside it.
  - partial_year_dividend_share capping at 0.5, below months/12 for 7–11 elapsed months.
- Real in business, and accepted:
  - Policy-series loan rates.
  - Termination dividends by duration.
  - Direct-recognition-style loan cuts.
  - Pro-rata dividends at termination.
  - Paid-up additions earning their own dividends.
  - Size-band dividend scales.
  - Unearned-premium refunds by mode.
  - Interest periods restarting at the latest interest settlement.

### findings

- **D-1 — SOURCE-POLICY RED.**
  - Symptom: surrender premium-record window — the rule anchors the 24 months on the surrender effective date; compute anchors on frozen_time.
  - Root cause: `returned_24m` uses `COUNT(..., within_months=24)`, whose window the evaluator fixes on NOW.
  - Evidence: rule sentence quoted above; `whole_ext_net_surrender_value.compute.returned_24m`; `check_compute.build_env._within`.
  - Bears on: **task 1** (demonstrated in `1.md`). Affected artifact: `whole.extended.yaml` → whole_ext_net_surrender_value compute/rule.
- **D-2 — SOURCE-FACTOR RED.**
  - Symptom: billing-mode day-count factors make an unreal condition (premium mode) decide loan and accumulation interest.
  - Affected factors: `billing_mode_interest_measure`, `offset_billing_mode_measure`, `accumulation_billing_mode_measure`.
  - Bears on: **task 0** (all three bear weight there; see `0.md`). Task 1 is not affected (credit, deposit and surrender carry no such factor).
- **D-3 — SOURCE-FACTOR RED.**
  - Symptom: `additions_dividend_method` is mislabelled, so the deposit computation has no honest method factor.
  - Bears on: **task 1** (see `1.md`).
- **D-4 — SOURCE-POLICY RED (latent; exercised by no task world).**
  - Symptom: for a policy with a loan, the offset policy (occasion `surrender`, "where a surrender request on the policy is on file") and the net-surrender policy ("less the loan balance shown on the policy") are unordered.
  - Two orders, two terminal states, in a world with loan balance L > 0 and a surrender request on file:
    - Offset first: loan_balance becomes 0, so the net surrender deducts nothing for the loan. The net is larger by L and no interest is deducted from the payout.
    - Surrender alone: net = gross − L.
  - The rules state no order and no edge.
  - Task 1 has loan_balance 0.00 and ledger principal 0.00 (3000.00 + 78.75 − 3078.75), so neither order arises there. Bears on no task.
- **D-5 — SOURCE-POLICY divergence (latent).**
  - Symptom: in the capitalization and offset computes, the repayment, owner-advance and APL "latest" filters are applied after LATEST rather than inside it.
  - Divergent world: described above. Bears on no task (task 0 has one repayment and no post-anniversary advance; task 1's capitalization and offset policies are not exercised).
- **D-6 — ambiguity in the credit policy's window anchor.**
  - The credit rule opens "On each policy anniversary the dividend accumulation deposit is credited with interest for the policy year that the anniversary closes, as one interest credit entry dated that anniversary". It then counts and half-credits withdrawals "dated within the 12 calendar months before the credit is booked".
  - The booking can be read as the handling day (compute's NOW) or as the anniversary on which the rule says the deposit "is credited" and to which the entry is dated. The half-year convention ("Money that moved through the deposit during the year") fits the anniversary reading.
  - Bears on: **task 1**, where the two readings give different credited interest (demonstrated in `1.md`, SOURCE-TASK).
  - The deposit rule's "before the deposit is booked" has the same form but gives the same count on task 1.
- **Observations:** O-1 (half-even `RND` vs half-up prose; no tie in either world), O-2 and O-3 (condition vs sentence corners), O-4 (state_gate `gate` is a column), O-5 (partial `replaced_by` texts), O-6 (grace-end NCV formula not named; different subject), O-7 (deposit vs "dividend declared … is credited"), O-8 (realism observations), O-9 (subjects outside the blueprint's claimed event_types), O-10 (withdrawal docstring names the occasion), O-11 (base "extinguished … first" sentence).

## closing_checklist

Written 2026-10-08T07:45Z, after both tasks were frozen, revealed and compared. Nothing above this heading was changed after any reveal; only the freeze-timestamp line was corrected before the reveal.

- Per-task audit files are one-to-one with the tasks: `0.md` ↔ tasks/0.json, `1.md` ↔ tasks/1.json, with `_difficulty.md` alongside. There is no previous revision. **Not every comparison section carries PASS.**
- Coverage and scope:
  - charter_scope task 0: capitalization, offset, withdrawal, RPU face, and their four tools.
  - charter_scope task 1: credit, deposit, surrender, and their three tools.
  - The two are pairwise disjoint and together cover all seven extended policies and seven tools.
  - Each task's scope spans its whole tree. uuid8s are independent (§ action_binding_and_uuids).
- Trees:
  - Task 0: 3 prerequisite problems, 3 value_input edges, owner=user root.
  - Task 1: 2 prerequisite problems, 2 value_input edges plus 1 state_gate, owner=user root.
  - No cycle. The union of the difficulty's edges is a DAG of two disjoint trees, with no cross-task reference.
- Factors:
  - Every factor bears weight on its task's world, and every whole-baseline number is definite and ≠ gold.
  - **Not met:**
    - D-2 (unreal billing-mode ladders bearing weight in task 0).
    - D-3 (the deposit computation in task 1 has no honest method factor).
    - The false `tier_taken` labels in task 0 (T0-F3).
- Policy self-consistency: **not met.** D-1 is demonstrated on task 1. D-4 and D-5 are latent, in the charter.
- Unique solution: **not met.**
  - Task 1: the derivation from the rule ≠ GT, and the credit window has a second reading.
  - Task 0: proof-only false intermediate (T0-F2).
- Instantiation-stage gates: I did not re-run them. The brief's snapshot is all green. The audited artifacts' hashes are unchanged from the brief (extended yaml `acb3cc41…`, task_tools `1deb1923…`, tasks/0.json `e3ca67fa…`, tasks/1.json `6aba4a2d…`). The gates being green does not cure the findings above: COMPUTE OK reflects compute's own anchor, which is exactly what D-1 contests.

**Difficulty result: does NOT pass the source-layer audit.**
- task0 = SOURCE-FACTOR RED + SOURCE-TASK RED (proof-only).
- task1 = SOURCE-POLICY RED + SOURCE-FACTOR RED + SOURCE-TASK RED.

## revision_2

### charter_global_frozen (revision 2)

- Frozen: 2026-10-08T09:04Z, before any round-2 task GT was revealed. Auditor: erl-task-policy-audit subagent (Claude Opus 5.5).
- Inputs, matching the coordinator's round-2 brief:
  - `whole.extended.yaml` sha256 `ee6e08dcc7cffc4eee6d050289f8a3ebb79d0362eb23e10b6277d65fbd6edd93` (changed from round 1's `acb3cc41…`).
  - `task_tools.py` `4118e911bfad0aa8f7f2ac5c0dfd92a38ada704104d9fc4058e16133b556d7d5` (changed from `1deb1923…`).
  - Both changed, so every charter-global section is re-derived in full, not carried forward.
- Base section: still semantically identical to `blueprint/products/whole.yaml`.
- Masked views: task_0 `f8de1d2c…2d65`, task_1 `52f0f278…b5db`.
- The round-1 text above is left untouched.

### What changed (charter)

- **Capitalization, offset and withdrawal.** The three billing-mode day-count factors were replaced by `policy_form_accrual_convention`, `offset_policy_form_accrual_convention` and `policy_form_part_year_convention`. The new tiers are set by issue date:
  - issued before 1985: whole policy months over 12, a part month not charged;
  - issued 1985–2004: actual days over 360 (`days_per_year_360`);
  - issued 2005 or later: actual days over 365.
- **Interest-start and set-apart sentences reworded.** The capitalization and offset sentences now describe exactly what compute does: "the latest loan repayment on the ledger … where [it] paid loan interest, falls on or before the anniversary, is later than … and no earlier than …"; "the latest owner loan advance on the policy ledger, where it falls after the start of the interest period and on or before the anniversary".
- **Offset no longer covers surrender.**
  - New overwrite of the base sentence "A loan is extinguished against the policy values on surrender, death, the application of a nonforfeiture option or loan default." It is replaced by "…on the insured's death, on the application of a nonforfeiture option or on loan default … a loan on a policy surrendered for cash is not extinguished by an offset entry, because the surrender payment itself deducts the loan and its interest".
  - The surrender tier of `offset_effective_date` was removed, leaving 3 tiers: death, paid-to, booked.
  - The tool enum's `surrender` value is now described as legacy ("an occasion Ashgrove now settles inside the surrender payment, so the value appears only on older entries").
- **Net surrender.**
  - It now deducts "the loan balance shown on the policy and the loan interest accrued on it at the tier's loan_interest_rate, simple, for the actual calendar days from the loan interest paid-to date to the surrender effective date over days_in_year". The compute adds `accrued_loan_interest`, the overwrite's `replaced_by` is updated, and the baseline rule and params include it.
  - The premium-record window now reads "within the 24 calendar months before the day the surrender is processed".
- **Credit.** The rule now states "every count and total below is taken over the policy ledger as it stands on the day the credit is processed, which may be later than the anniversary". Every window reads "before the day the credit is processed".
- **Deposit.** `additions_dividend_method` now selects between two allocation bases, depending on seasoning (`deposit_additions_seasoning_months` 36):
  - by face: declared dividend / base face × additions face;
  - by reserve: declared dividend / guaranteed cash value × additions cash value;
  - or none.
- Unchanged: the prerequisite sentences and graph, the uuid8s, every function body (no validation, no refusal), and the RPU and withdrawal ladders apart from the convention factor.

### Re-derived checks (revision 2)

- **policy_conflict_scan.** Seven policies with seven distinct `(target_tool, computes)` pairs, and the same two disjoint trees.
  - The offset vs surrender overlap (round-1 D-4) is removed: offset's scope now excludes surrender explicitly, and the surrender rule deducts the loan itself.
  - New latent conflict D-7, below.
- **rule_compute_equivalence.**
  - Every compute binding has a `compute_basis` that is a verbatim rule sentence. Every `replaced_by`, `baseline.rule` and `policy_source` is verbatim in its rule (script check: all True).
  - The surrender window now says "the day the surrender is processed", which is what compute's NOW-anchored `COUNT(..., within_months=24)` implements, so the two agree.
  - The repayment, owner-advance and APL "latest … where" sentences now match the compute's LATEST-then-test.
  - Corner (observation O-12): "bought more than deposit_additions_seasoning_months … months before" vs compute's `within_months=36` (recent means MONTHS in [0, 36)). An addition exactly 36 whole months back counts as seasoned in compute, while "more than 36 months" is arguable. No row in either world sits at 36 months.
  - O-1 (half-even `RND`) remains.
- **action_binding_and_uuids.** Same seven uuid8s. Bodies are unchanged and validate nothing. The docstrings' ordering-word scan is clean, and the offset enum change names no other tool. PASS.
- **prerequisite_graph / prerequisite_sentences.** Five edges, unchanged and verbatim, all state form, acyclic. My round-1 analysis is carried forward with these input changes re-checked: no rule now carries an undeclared cross-problem order (scan above). O-2, O-3, O-4 and O-11 remain.
- **override_declarations.**
  - The new offset overwrite names the base sentence it narrows.
  - The surrender's `replaced_by` now restores the accrued loan interest that base deducts, so it differs from base only by the termination dividend, accumulation interest and premium refund it declares.
  - No undeclared override found. O-5, O-6 and O-7 remain.
- **factor_ladders (revision 2).**

| policy | P | M (honest) | X | change |
|---|---|---|---|---|
| capitalization | 2 | 4 | 1 | billing-mode → policy-form accrual convention |
| offset | 2 | 3 | 1 | same; offset_effective_date now 3 tiers |
| withdrawal | 4 | 2 | 0 | billing-mode → policy-form part-year convention |
| RPU face | 3 | 2 | 1 | none |
| credit | 4 | 1 | 0 | windows anchored on the processing day |
| deposit | 3 | **1** (additions: face vs reserve allocation) | 1 | additions method now picks a different allocation basis per tier |
| surrender | 2 | 2 | 1 | window anchored on the processing day |

  - Realism. A loan- and accumulation-interest day-count convention fixed by the policy-form generation (monthly accrual on old forms, 360-day year on 1985–2004 forms, 365-day year on current forms) is something a whole-life carrier really prints in its contracts. The tiers are pairwise distinct, and the fall-through, actual/365, is the baseline.
  - Apportioning dividends on paid-up additions by face or by reserve, by their seasoning, is an actuarially recognisable choice of allocation basis. It is a genuine method change: a different base quantity and a different divisor.
  - New observation O-13: anchoring the surrender's 24-month premium-record window, and the credit's windows, on the processing day rather than the effective date or anniversary is now stated outright. It is unusual (the outcome moves with the day the work is done), but it is explicit and unambiguous.
  - O-8 (other realism observations) unchanged.

### findings (revision 2)

| round-1 item | status in revision 2 | grounds |
|---|---|---|
| D-1 (surrender window rule ≠ compute) | **closed** | Rule now says "before the day the surrender is processed", matching compute. The demonstration on task 1 is in `1.md` revision_2. |
| D-2 (billing-mode ladders unreal) | **closed** | Replaced by policy-form accrual conventions (above). |
| D-3 (additions method mislabelled) | **closed** | The tiers now select face vs reserve allocation, so the deposit has 1 honest method factor. |
| D-4 (offset vs surrender unordered) | **closed** | Offset excludes surrender by an overwrite; the surrender deducts the loan and interest itself. |
| D-5 (repayment/advance filter) | **closed** | Rule rewritten to the compute's semantics. |
| D-6 (credit window anchor ambiguous) | **closed** | The rule fixes the processing day explicitly. |

- **D-7 — new, SOURCE-POLICY RED (latent; exercised by no task world). Introduced by the D-4 rework.**
  - Symptom: the surrender's accrued loan interest conflicts with the capitalization and offset policies on how much interest is still owed on the same loan.
  - What the surrender charges: interest "from the loan interest paid-to date to the surrender effective date" at "the tier's loan_interest_rate … over days_in_year".
  - What the charter says elsewhere about that same date range:
    - The capitalization and offset rules treat the field as stale whenever a later repayment paid interest: "the period starts on that repayment's date, because the repayment settled interest up to its own date".
    - When a capitalization is booked, the capitalization tool "leaves the interest paid-to date shown on the policy as it stands", while the capitalized interest enters `loan_balance`.
  - Demonstration on task 0's own ledger, as if that owner had surrendered instead:
    - `loan_interest_paid_to_date` is 2025-08-20, while the 2026-02-10 repayment paid 293.85 interest.
    - The surrender rule would charge 12300.40 × 0.06 × days(2025-08-20 → effective)/365. That includes 2025-08-20…2026-02-10, which the capitalization rule's own sentence says that repayment already settled.
    - Also, with the 2026-08-20 capitalization due (state_due) and no order between it and a surrender:
      - Capitalize first: `loan_balance` rises by the capitalized interest while the paid-to date stays at 2025-08-20, so the surrender deducts that interest twice.
      - Surrender without capitalizing: deducted once.
    - Two orders give two net amounts.
  - The surrender also uses the tier rate 0.06 on actual/365, where the same loan's capitalization and offset use the series rate less the continuity cut on the form convention. This is the base clause for the surrender event, which is legal but inconsistent (observation O-14).
  - Task 1 does not exercise D-7: `loan_balance` 0.00 and ledger principal 0.00 (3000.00 + 84.14 − 3084.14).
- Observations: O-1…O-11 as before (O-9 and O-10 unchanged), plus O-12, O-13 and O-14.

### closing_checklist (revision 2)

Written 2026-10-08T09:06Z, after both revision-2 tasks were frozen, revealed and compared.

- Files are one-to-one, and the round-1 text is preserved above each `## revision_2`.
- Scope (round-2 charter_scope):
  - task 0 has capitalization, offset, withdrawal and RPU, with 4 tools;
  - task 1 has credit, deposit and surrender, with 3 tools;
  - they are disjoint and cover all seven policies. uuid8s are unchanged and independent.
- Trees:
  - task 0: n = 3, 3 value_input edges, user root;
  - task 1: n = 2, 2 value_input edges plus 1 state_gate, user root;
  - the union is acyclic.
- Factors:
  - Every computation has 4–6 factors with ≥ 2 P and ≥ 1 honest M; each task has a multi-source and a cross-difficulty factor.
  - Every factor bears weight against an honest baseline, and every all-baseline number ≠ gold.
  - Round-1 D-2 and D-3 are closed.
- Round-1 charter items D-1 to D-6 are closed (§ revision_2 findings).
- **Open:**
  - **D-7**: latent SOURCE-POLICY RED in the charter, introduced by the D-4 rework. The surrender's accrued loan interest counts from the loan interest paid-to date, which the capitalization and offset rules treat as stale, and its order against a due capitalization is unstated. No task world exercises it.
  - **T0-F4**: task 0's design_rationale carries stale round-1 figures (proof-only SOURCE-CHAIN RED).
- Gates: I did not re-run them. The round-2 brief reports all green on the audited hashes (extended yaml `ee6e08dc…`, task_tools `4118e911…`, tasks/0.json `48f7f8a5…`, tasks/1.json `250c85eb…`). Every round-2 scored value I recomputed equals GT.

**Difficulty result (revision 2): does NOT pass the source-layer audit**, because of D-7 (charter) and T0-F4.
- task0 = SOURCE-CHAIN RED (proof-only, T0-F4).
- task1 = PASS.
- Charter: D-7 latent SOURCE-POLICY RED.

## revision_3

### charter_global_frozen (revision 3)

- Frozen: 2026-10-08T10:58Z, before any round-3 task GT was revealed. Auditor: erl-task-policy-audit subagent (Claude Opus 5.5).
- Inputs:
  - `whole.extended.yaml` sha256 `a54b532a3855c3aaf8b790f02632326fb9101a4e7e1a44504405f327dc448a12` (changed from `ee6e08dc…`).
  - `task_tools.py` `4118e911…` (unchanged).
  - Masked views `f8de1d2c…` and `52f0f278…` (unchanged from round 2, so the worlds and personas are identical).
- Base section: still identical to the blueprint.

### What changed (charter)

- Only `whole_ext_net_surrender_value` changed.
  - I compared the rule and compute text of the withdrawal, credit and deposit policies against my saved round-2 dump: identical.
  - Capitalization, offset and RPU have the same binding lists, overwrites and rule texts as in round 2.
  - All round-2 values recompute identically (below).
- Surrender: "less the loan balance shown … and the loan interest accrued on it … from the loan interest paid-to date" is replaced by a **loan indebtedness**:
  - Interest runs from the *loan interest start*: the latest loan repayment on the ledger, where it paid loan interest and is later than the paid-to date shown; otherwise that paid-to date.
  - The *principal owed* is the ledger loan principal "less the latest capitalization entry where its anniversary is later than the loan interest start, because interest after that start is charged here instead and is never charged twice".
  - Interest is at the tier's loan_interest_rate, actual/365, rounded to the cent.
  - The compute adds `loan_repayment_date`, `loan_repayment_interest`, `loan_paid_to`, `loan_interest_start`, `latest_capitalization_end`, `latest_capitalization_amount`, `ledger_loan_principal` and `principal_owed`; `accrued_loan_interest` and `result` now use `principal_owed`.
  - A second overwrite is declared: the base clause "interest not paid by the anniversary is capitalized into the loan principal on that anniversary and itself bears interest" is replaced, for the surrender, by the indebtedness sentence.

### Re-derived checks (revision 3)

- **rule_compute_equivalence.** Every compute binding has a verbatim `compute_basis`. Every `replaced_by`, `baseline.rule` and `policy_source` is verbatim in its rule (script: all True). The new loan-indebtedness bindings implement the sentence exactly:
  - LATEST repayment, then tested for interest > 0 and for being after the paid-to date, as the rule words it;
  - the latest capitalization subtracted only when its interest_period_end is later than the start;
  - interest = principal_owed × tier rate × DAYS(start, effective)/365, RND to the cent.
- **policy_conflict_scan / D-7 re-run.** On task 0's own ledger, as a hypothetical surrender (request received 2026-09-25):
  - The loan interest start is the 2026-02-10 interest-paying repayment, no longer the stale paid-to date 2025-08-20.
  - Without the due 2026-08-20 capitalization: principal owed 12300.40, interest 458.99, net 56769.26.
  - With the capitalization (308.48) booked first: the latest capitalization anniversary 2026-08-20 is later than the start, so it is subtracted. Principal owed is again 12300.40, interest 458.99, net 56769.26.
  - **Order-invariant, and nothing is charged twice. D-7 closed.**
- **override_declarations.**
  - The surrender's second overwrite names the base capitalization clause it handles differently for the surrender event.
  - The capitalization policy overrides the same clause for `whole_loan_interest_capitalized`. The subjects are disjoint and the net is invariant to whether the capitalization is booked, so there is no conflict.
- **Residual corner (observation O-15).** The subtraction removes only the *latest* capitalization. Two capitalizations after the start would leave the earlier one double-counted. That arises only with two capitalizations on a stale paid-to date and no interest-paying repayment between them. The seeded histories advance the paid-to date at each historical capitalization (task 0: paid-to 2025-08-20 = the last seeded capitalization), and the capitalization tool books one entry per call. No world of this difficulty contains such a pair.
- **O-14 unchanged** (the surrender uses the tier rate on actual/365, where capitalization and offset use the series rate and the form convention). Non-RED, as the reworker notes.
- Unchanged and carried forward with the input change re-checked: action_binding_and_uuids (tools unchanged), prerequisite_graph / prerequisite_sentences (the five edges are verbatim and unchanged), and factor_ladders. The surrender's four factors are unchanged, and its baseline rule now names the indebtedness, with the same params.

### findings (revision 3)

| item | status | grounds |
|---|---|---|
| D-7 | **closed** | indebtedness from the interest-paying repayment; latest post-start capitalization subtracted; order-invariance demonstrated (56769.26 both ways) |
| D-1 … D-6 | stay closed | no regression: the texts are unchanged and every value recomputes identically |
| O-14 | open observation | unchanged |
| O-15 | new observation | the two-capitalizations corner, above |

### closing_checklist (revision 3)

Written 2026-10-08T10:59Z, after both revision-3 tasks were frozen, revealed and compared.

- The per-task files are one-to-one and every earlier revision is preserved.
- Scope (round-3 charter_scope) is unchanged: task 0 has 4 policies and 4 tools, task 1 has 3 and 3. They are disjoint and complete, and the uuid8s are independent.
- Trees:
  - task 0: n = 3, 3 value_input edges, user root;
  - task 1: n = 2, 2 value_input edges plus 1 state_gate, user root;
  - the union is acyclic; the tools validate nothing.
- Factors:
  - Every computation has 4–6 factors with ≥ 2 P and ≥ 1 honest M; each task has a multi-source and a cross-difficulty (term) factor.
  - Every factor bears weight against an honest baseline, and every all-baseline figure ≠ gold.
- Policy self-consistency: D-1 to D-7 are closed. No undeclared override, and no rule/compute divergence.
- Unique solution: every scored value of both tasks equals my independent recomputation. The proof fields (traces, tier labels, closures, rationale) were checked and are true.
- Open observations (non-RED): O-1 to O-15, including O-14 (surrender loan rate and day count differ from capitalization and offset) and O-15 (the two-capitalizations corner).
- Gates: I did not re-run them. The round-3 brief reports all green on the audited hashes (extended yaml `a54b532a…`, task_tools `4118e911…`, tasks/0.json `34811855…`, tasks/1.json `26cbfbfa…`). My recomputations agree with every gold argument.

**Difficulty result (revision 3): PASSES the source-layer audit.**
- task0 = PASS.
- task1 = PASS.
