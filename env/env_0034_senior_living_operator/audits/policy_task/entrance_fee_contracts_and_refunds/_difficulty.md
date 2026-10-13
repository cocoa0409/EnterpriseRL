# Policy-task audit — entrance_fee_contracts_and_refunds / charter-global

## charter_global_frozen

- Scenario: `env/env_0034_senior_living_operator`; difficulty `entrance_fee_contracts_and_refunds`; product category `entrance`; M = 2 (tasks 0, 1). Round 1 (revision_1).
- Auditor: independent policy-task auditor (erl-task-policy-audit), not the author of the artifacts.
- Freeze time of this charter-global section: 2026-10-05T09:07Z, before any task's GT was read.
- Freeze hashes (sha256, recomputed by the auditor; equal to the coordinator's MANIFEST and to the originals under `tasks/entrance_fee_contracts_and_refunds/`):
  - `entrance.extended.yaml` c593bac668cfdf669610af989a9447fe076cd9b60ff0c5865c9e2d1ce5cc3339
  - `task_tools.py` 04a31a9c345781addc0ef8ac96ff3122431b2e2a6aa96c871f8160eb304e3336
- Fields permitted for this section: `blueprint/` (blueprint.yaml, db_schema.json, share_tools.py, products/*.yaml), the extended charter, the task tool module, `erlbench/`, and the DSL primitive definitions in `skills/erl-task-instantiate/scripts/check_compute.py` (read for the semantics of `DAYS`/`MONTHS`/`within_months`/`RND` only; no task JSON was opened by the auditor).
- Fields masked: every task's `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`, and the difficulty `worklog.md`.
- Entry conditions (Step 0): gate snapshot supplied in the brief — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; traceability deferred (KB unpublished). Masked views supplied with MANIFEST hashes; the auditor re-hashed all four view files and they match. Entry conditions complete.
- The base section of the extended charter (lines 1-1196) is byte-identical to `blueprint/products/entrance.yaml` (`diff` shows only the trailing blank line before `extended_policies:`).

### policy_conflict_scan

Six extended policies, six task tools, one per policy:

| policy | trigger | subject | target_tool (owner) | computes |
| --- | --- | --- | --- | --- |
| entrance_ext_cancellation_processing_fee | on_request | entrance_cancel_pre_occupancy, entrance_processing_fee_retention | sign_pre_occupancy_cancellation_25852637 (user) | processing_fee |
| entrance_ext_pre_occupancy_refund | state_due | entrance_refund_payment | pay_pre_occupancy_refund_45806fa1 (agent) | refund_amount |
| entrance_ext_final_period_amortization | state_due | entrance_amortization | book_final_period_amortization_cad149c9 (agent) | amortization_amount |
| entrance_ext_annual_tax_letter | state_due | entrance_tax_letter | issue_annual_tax_letter_ce10c97a (agent) | medical_expense_amount |
| entrance_ext_closing_year_tax_letter | state_due | entrance_tax_letter | issue_closing_year_tax_letter_050bd78c (agent) | medical_expense_amount |
| entrance_ext_estate_refund_release | on_request | entrance_refund_payment, entrance_close | release_estate_refund_4b5e42b1 (user) | refund_amount |

Overlapping subjects and how they are separated:

- `entrance_tax_letter` (annual vs closing-year): annual rule "The annual letter covers a tax year other than the one in which the agreement terminated"; closing rule "The tax year in which an agreement ended receives one closing-year letter". Disjoint by tax year. Wording drift: "terminated" (annual) vs "ended" (closing, whose ladder also covers rescinded/cancelled agreements) — for a rescinded/cancelled agreement the annual rule's exclusion does not literally apply to the cancellation year. Observation O-6 (no task world has a rescinded/cancelled agreement needing a letter).
- `entrance_refund_payment` (pre-occupancy refund vs estate release): pre-occupancy refund governs "a refund on a cancellation before occupancy"; estate release governs "an estate refund" of an agreement "whose refund is scheduled" (tool docstring). For an estate refund on a death-before-occupancy cancellation both could claim the payment (see finding F-2). No task world reaches that overlap.
- Time anchors: cancellation fee uses the notice date / planned occupancy date; refund escrow uses deposit posting date → cancellation (termination) date; final amortization uses the last amortized month start → vacate/death/termination date; tax letters use whole months before the issue date; estate interest uses refund due date / estate documents date → payment day. No two policies fix the same date differently.
- Terminal states: cancellation → `cancelled`; refund → status unchanged (`cancelled`), balance negative by the escrow interest (see O-3); final amortization → status unchanged; tax letters → no balance change; estate release → `closed`, balance negative by the delay interest (declared). Compatible.
- Cross-category reads: respite (trial-stay nights/charges; care stays, credits, add-ons), independent (residency status/move-in/vacate/termination reason/monthly fee; ledger payments, returns, fees, offsets, charges, proration credits; CPARAM post_death_fee_days / internal_transfer_notice_days). All read-only; no write into another category.

Scope partition derived blind (to be compared with `charter_scope` at the reveal): task 0 = {cancellation_processing_fee, pre_occupancy_refund}; task 1 = {final_period_amortization, annual_tax_letter, closing_year_tax_letter, estate_refund_release}. Pairwise disjoint and jointly complete over the six extended policies.

### rule_compute_equivalence

Swept every binding of every policy against its `compute_basis` quotation and back against the `rule` (DSL semantics from `check_compute.py`: `MONTHS` = whole months with day-of-month borrow, `within_months=n` = rows with `0 <= MONTHS(posting, NOW) < n`, `RND` = Python `round` on a float).

- cancellation_processing_fee: notice date ladder (`notice_credit_days` + `notice_days` = DAYS(notice date, planned occupancy)) equivalent to "The days of notice are the calendar days from the notice date to the planned occupancy date"; percentage, surcharge, gross rounding, 12-month trial window (`within_months=12`), credit share, floor at 0.00, internal-move multipliers with floor/ceil to the whole dollar — all quoted and implemented. No invented basis.
- pre_occupancy_refund: money received, fee retained, escrowed deposit, escrow rate, days held (deposit posting → `termination_date`), term bonus, instrument hold (`check` = personal check, schema enum also has `certified_check`), campus day count (360 / whole months / 365), single rounding — quoted and implemented.
- final_period_amortization: last amortized start, thirty-day convention, end-date ladder (vacate before termination / death with the death date counted / termination date), share ladder, step rate on the count of amortization entries, surrender reduction on death + vacate days, order "rate − reduction → × share → cap → single rounding" — quoted and implemented.
- annual_tax_letter: window ladder (missed-run 13-24, first letter back to the first payment month, otherwise 1-12), settlement basis, post-acute percentage, care-stay share, stay-charges basis, add-on share, single rounding — quoted and implemented, with two latent mismatches (observations, no consequence on any task world):
  - O-1: `stay_charges` sums every `respite_nightly_charge` in the window, any tier, while the rule speaks of "Larkspur care stays charged in the window"; an Independent Living Trial Stay nightly charge in a letter window would be counted by compute and not by the rule. Task 1's window holds only Post-Hospital Recovery Stay nights.
  - O-2: `first_payment_age` reads `LATEST` of the deposit payments while the rule says "the month of the first entrance fee payment"; differs only when an agreement has more than one deposit row. No task world has that.
- closing_year_tax_letter: termination-in-closing-year test, retention + amortization in year, entrance percentage on the count of amortization entries, IL basis ladder, post-residency deduction (CPARAM of the paired residency's tier; monthly service fee / 30; rounding; floor 0), IL percentage on base-fee charge count, single rounding — quoted and implemented.
- estate_refund_release: refundable amount over all ledger in/out families, letters-late days, interest start ladder, payment-day inclusion ladder, campus rate gated on past-due, outstanding step on days past due, campus day count, single rounding — quoted and implemented.
- Rounding: every rule says "rounded to the cent half up", `RND` is Python's float `round` (banker's on exact binary halves). No intermediate on either task world lands on an exact half cent (checked: 362.50 is already a cent; 205.689375, 191.7333…, 26140.5904, 1385.184, 2118.6667, 667.2307 are not halves). Observation O-7.
- Every factor ladder tier is a rule sentence and a branch of its `decides` binding, and every branch is a stated tier (checked tier by tier for all 30 factors). No tier lives in only one face.

### action_binding_and_uuids

- Each `(target_tool, computes)` is claimed by exactly one policy (table above); no tool is shared.
- Docstrings: none names another tool, none states a position in a sequence; the only temporal words are business states ("cancelled or rescinded before occupancy", "a month of occupancy that has no amortization entry yet", "whose refund is scheduled"). The module header states the tools "never check eligibility, status, timing or any other policy condition and never compute an amount", and the bodies bear it out: each body only reads the agreement row for the current balance/payee and writes; no branch refuses, errors or hints on an unmet prerequisite.
- uuid8s: 25852637, 45806fa1, cad149c9, ce10c97a, 050bd78c, 4b5e42b1 — six distinct values, no shared prefix or suffix, no sequence or adjacency pattern. No evidence of reuse or batch derivation.

### prerequisite_graph

- `prerequisite` is filled on all six policies (`[]` on cancellation_processing_fee, final_period_amortization, annual_tax_letter).
- Edges (all `form: state`, no `fallback_reason`, none needed):
  1. pre_occupancy_refund → cancellation_processing_fee, value_input, gate `fee_retained` (a compute binding of the refund), resolved_by `sign_pre_occupancy_cancellation_25852637` = target tool of the depended policy.
  2. closing_year_tax_letter → final_period_amortization, value_input, gate `amortization_in_year` (compute binding), resolved_by `book_final_period_amortization_cad149c9`.
  3. closing_year_tax_letter → annual_tax_letter, state_gate, gate `entrance_ledger.tax_year`, resolved_by `issue_annual_tax_letter_ce10c97a`.
  4. estate_refund_release → final_period_amortization, value_input, gate `refundable_amount` (compute binding), resolved_by `book_final_period_amortization_cad149c9`.
  5. estate_refund_release → closing_year_tax_letter, state_gate, gate `entrance_ledger.tax_year`, resolved_by `issue_closing_year_tax_letter_050bd78c`.
- Every `problem` is an extended policy id of this file, none self-referencing, none a base policy. The graph is acyclic (sources: cancellation_processing_fee, final_period_amortization, annual_tax_letter).
- Every `policy_source` is verbatim in its own policy's `rule` (machine-checked after whitespace normalisation) and is not restated in the depended-on policy's rule.
- `condition` vs sentence: edge 1 condition adds "termination_reason pre_occupancy_cancellation", which the sentence implies ("the processing fee retained on that cancellation"); edges 2-5 match the sentences in scope and strength.
- `effect` claims, checked against the compute: edge 1 — the fee entry raises `fee_retained` from 0.00 and sets the cancellation date the escrow term is counted to; edge 2 — the entry is posted on the first day of the final month, inside the closing year, so `amortization_in_year` rises and the amortization entry count rises by one; edge 4 — `refundable_amount` falls by the entry and the interest with it. All hold on the compute.
- O-8 (observation): the two `state_gate` edges name a field (`entrance_ledger.tax_year`) as `gate`, not an eligibility id (the extended policies carry no eligibility blocks); edge 3's `effect` reads "The missed annual letter is entered for the year before the closing year", narrower than its condition (every earlier year) and phrased from one scenario's viewpoint.

### prerequisite_sentences

Four-point test on each sentence:

| edge | sentence | connective | waited-on state (record-visible) | no tool/id/snake | strength = condition |
| --- | --- | --- | --- | --- | --- |
| 1 | "A refund on a cancellation before occupancy is not paid until the agreement stands in cancelled status and its ledger carries the processing fee retained on that cancellation." | not … until | agreement status `cancelled`; ledger processing-fee entry | yes | yes |
| 2 | "The tax letter for the year in which an agreement terminated is issued only after the agreement's ledger carries an amortization entry for every month of occupancy that began on or before the termination date." | only after | amortization entry per month started on/before termination | yes | yes |
| 3 | "The tax letter for the year in which an agreement terminated is not issued until the agreement's ledger carries a tax letter for every earlier tax year in which entrance fee or independent living monthly fees were paid." | not … until | a tax-letter entry for every earlier paid year | yes | yes |
| 4 | "An estate refund is not released until the agreement's ledger carries an amortization entry for every month of occupancy that began on or before the termination date." | not … until | as edge 2 | yes | yes |
| 5 | "An estate refund is released only after the agreement's ledger carries the tax letter for the tax year in which the agreement terminated." | only after | tax-letter entry for the termination year | yes | yes |

Unique resolving write per state-form edge (derived from the other policies' rules, as the reader must):

- Edge 1: the only rule whose write moves an agreement to `cancelled` and books a processing fee is cancellation_processing_fee ("signing it cancels the agreement and retains the processing fee from the money paid"). Single reading.
- Edges 2 and 4: the only rule that books an amortization entry after termination is final_period_amortization ("A month of occupancy that began on or before the termination date and carries no amortization entry when the agreement terminates is amortized after the termination"). Single reading.
- Edge 3: tax-letter entries are written by two policies; the closing-year rule restricts itself to the year the agreement ended, the annual rule covers "a tax year other than the one in which the agreement terminated". An earlier-year letter is therefore an annual letter. Single reading.
- Edge 5: the termination-year letter is excluded from the annual rule and is the closing-year rule's own object. Single reading.

Rules carry no second wording of any edge, no tool name and no other problem's id. Depended-on rules do not restate the sentences. Docstrings are silent about sequence (above).

Cross-problem orders stated in base rules: base `entrance_refund_timing` "A refund payable to an estate … may be paid only after letters testamentary or letters of administration are on file, shown by estate_documents_date" states an order against `entrance_estate_documents_record`, which has no task tool in this difficulty. No task tree rests on it (task 1's letters are on file at the opening, `estate_documents_date` 2026-12-28) → observation O-9. Base "refunds may be paid only while the agreement is in rescinded, cancelled or refund_scheduled status" repeats the order of edge 1. Edge 1 is grounded by the extended rule's own sentence, so no tree rests on the base sentence alone.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (finding half only).

- cancellation_processing_fee vs `entrance_pre_occupancy_cancellation`. S1 fee clause: declared superseded. The replacement text summarises only the notice ladder, but the surcharge, trial credit and internal-move rounding all change the same superseded quantity, and the extended rule states them in full. Merged semantics are unique (O-10, wording only). S1 refund clause: superseded in pre_occupancy_refund. S2-S7 (death/illness path, death evidence, deadline/extension, extension only while reserved, deemed cancellation at deadline, signer): followed.
- pre_occupancy_refund vs `entrance_pre_occupancy_cancellation`, `entrance_rescission`, `entrance_refund_timing`. Declared: "the rest of the money paid is refunded no later than pre_occupancy_refund_days calendar days after the cancellation". The replacement is about amount only, so the base refund deadline (60 days) is dropped from the merged text (O-11; a payment deadline, not scored). **Undeclared:** base `entrance_pre_occupancy_cancellation` S2 "Where the resident dies before occupancy, or a physician certifies … no processing fee is retained and pre_occupancy_health_refund_pct percent of the money paid is refunded, to the estate after a death" vs the extended gate "A refund on a cancellation before occupancy is not paid until the agreement stands in cancelled status and its ledger carries the processing fee retained on that cancellation" and "paid in one payment to the resident". See F-2. `entrance_rescission`: no conflict, because the extended rule speaks only of a cancellation before occupancy. `entrance_refund_timing` "The agreement is closed once the refund is paid and the refundable balance is 0.00": after an escrow-interest refund the balance is negative (e.g. −interest). A cancelled agreement has no lifecycle transition to `closed`, so no scored conclusion differs (O-3).
- final_period_amortization vs `entrance_occupancy_and_amortization`. Three declared supersessions (status gate, monthly percentage clause, full-month clause). **Dropped branch:** the superseded clause "of amortization_pct_per_month percent of the entrance fee rounded to the cent half up" is the clause of base S3 that fixes the amount of every month's amortization. Its replacement, "The monthly amortization percentage of the final period steps down with the months already amortized…", speaks only of the final period. See F-3.
- annual_tax_letter / closing_year_tax_letter vs `entrance_tax_letter_policy`. Declared: the amount clause and the one-letter sentence. **Undeclared:** the trailing clause of the same base sentence, "; a plan whose percentages are 0.0 receives a letter stating 0.00", is not inside either superseded clause and is not otherwise named. See F-1. Base S1 "issued by tax_letter_deadline of the following year" vs the annual rule's late issue of a missed letter with the next January run: base sets a deadline but forbids no late issue, so no different scored conclusion (O-12).
- estate_refund_release vs `entrance_refund_timing` (+ `entrance_rescission`, `entrance_pre_occupancy_cancellation` listed but not engaged). Declared: the close-at-0.00 sentence. Delay interest is an addition that no base sentence contradicts. Base S5 payee (estate's personal representative named in the letters) is compatible with "check to the estate in care of the address on file". `entrance_refund_calculation`, which governs the refundable amount, is not in `base_policy_refs`, but the extended refundable amount is the same ledger quantity (O-13).
- Disguised forms: no anonymous intermediate or 0/1 multiplier found beyond the above. No rule or `compute_basis` calls a base output "wrong".

### factor_ladders

Per policy (effect labels; every ladder has 3 pairwise-disjoint tiers including the fall-through; every tier is stated in the rule with its condition and value/method and is implemented in compute; `decides` is an input, never `result`; binding sets are disjoint within each policy):

| policy | factor | effect | multi-source tiers | cross_difficulty | tier outcomes distinct? | real? |
| --- | --- | --- | --- | --- | --- | --- |
| cancellation_processing_fee | cancellation_notice_date | method | no | — (reads independent for tier 2) | yes (three anchors) | yes |
| | notice_fee_percentage | parameter | no | — | yes (1.0 / 1.5 / plan 2.0 in all six plans) | yes |
| | occupancy_extension_surcharge | parameter | yes (extension on file AND notice days) | — | yes | yes |
| | trial_stay_credit_share | parameter | no | respite | yes | yes |
| | internal_move_rounding | method | no | independent | yes | label borderline (O-14) |
| pre_occupancy_refund | escrow_deposit_rate | parameter | no | — | yes | yes |
| | escrow_term_bonus | parameter | no | — | yes | yes |
| | deposit_funds_availability | method | no | — | yes | yes |
| | escrow_bank_day_count | method | no | — | yes | yes |
| final_period_amortization | final_month_share | method | no | — | yes | yes |
| | final_month_count_end | method | yes (death AND vacate date) | independent | yes | yes |
| | amortization_step_rate | parameter | no | — | **no on three plans** (F-4) | **no on three plans** (F-4) |
| | estate_surrender_reduction | parameter | yes (death AND vacate days) | independent | yes | yes |
| annual_tax_letter | letter_window | method | no | — | yes | yes |
| | settlement_basis | method | no | independent | yes | yes |
| | post_acute_monthly_pct | parameter | yes (recovery nights AND base-fee months) | independent | yes | **no** (F-5) |
| | care_stay_share | parameter | no | respite | yes | yes |
| | stay_charges_basis | method | no | respite | yes | yes |
| | stay_addon_share | parameter | no | respite | yes | yes |
| closing_year_tax_letter | closing_entrance_basis | method | yes (reason AND date) | — | yes | yes |
| | closing_entrance_pct | parameter | no | — | yes | **no** (F-5) |
| | closing_il_basis | method | no | independent | yes | yes |
| | post_residency_deduction | parameter | no | independent | yes | yes |
| | closing_il_pct | parameter | no | independent | yes | **no** (F-5) |
| estate_refund_release | delay_interest_start | method | no | — | yes | yes |
| | interest_day_inclusion | method | no | — | yes | borderline (O-15) |
| | campus_statutory_rate | parameter | yes (campus AND past due) | — | yes | yes |
| | outstanding_step | parameter | no | — | yes | yes |
| | delay_interest_day_count | method | no | — | yes | yes |

Declared counts per policy: cancellation 5 (3 parameter / 2 method); pre-occupancy refund 4 (2/2); final amortization 4 (2/2); annual 6 (3/3); closing 5 (3/2); estate 5 (2/3). All within 4-6, with ≥2 parameter and ≥1 method as declared. The counts after striking the factors flagged unreal: final amortization 3 factors / 1 parameter on the three affected plans (F-4); annual 5 / 2; closing **3 / 1** (F-5). Every `baseline` block is the fall-through of its ladder. Every policy's `baseline.rule` is a sentence of its `rule`, and `baseline.params` names the plan parameters it uses.

Per-task availability of a multi-source and a cross-difficulty factor: task 0 (cancellation + refund) has occupancy_extension_surcharge (multi-source) and trial_stay_credit_share / internal_move_rounding (respite / independent). Task 1 (final amortization + annual + closing + estate) has final_month_count_end / estate_surrender_reduction / campus_statutory_rate (multi-source) and several independent/respite factors. Both satisfied structurally. Seeding and weight are checked per task.

### findings

- **F-1 SOURCE-POLICY RED — undeclared override of "a plan whose percentages are 0.0 receives a letter stating 0.00".**
  - Symptom: both tax-letter extended policies state non-zero medical expense amounts for plans whose percentages are 0.0.
  - Root cause: the superseded clause of both overwrites stops at "rounded to the cent half up". The base sentence continues "; a plan whose percentages are 0.0 receives a letter stating 0.00", and no overwrite names that continuation.
  - Evidence: base `entrance_tax_letter_policy` rule S2 (extended.yaml line 1166) vs annual rule "where the window holds any Post-Hospital Recovery Stay nights the share is 1.0" and "where the window holds 10 or more nights … and 12 or more monthly base fee charges … the percentage is 41.0", and closing rule "24 or more amortization entries take 40.0 percent" / "where the closing year holds 3 or fewer monthly base fee charges the percentage is 45.0".
  - Demonstrated consequence: take a LifeChoice Declining Balance resident (medical_expense_pct_entrance_fee 0.0, medical_expense_pct_monthly_fee 0.0) whose window holds a Post-Hospital Recovery Stay. The base sentence gives 0.00. The annual rule gives 1.0 × the stay charges plus 41.0 % of the IL payments (> 0). Two readings, two numbers.
  - Bears on: no task world (both tasks' tax letters are on a LifeCare plan with 34.6 / 38.5). Task 1 file records "no consequence on this world".
  - Affected: entrance.extended.yaml `entrance_ext_annual_tax_letter.overwrite[0]`, `entrance_ext_closing_year_tax_letter.overwrite[0]`.
- **F-2 SOURCE-POLICY RED — the pre-occupancy refund gate contradicts the base death/illness refund.**
  - Symptom: the extended refund of a death/illness pre-occupancy cancellation can never be paid, and is paid to the resident rather than the estate.
  - Root cause: the extended rule covers every "refund on a cancellation before occupancy". Its prerequisite sentence waits on "the processing fee retained on that cancellation", which base S2 says is never retained for death/illness, and its payee sentence says "to the resident". Only the 60-day refund clause is named in `overwrite`.
  - Demonstrated consequence: a reserved agreement cancelled with termination_reason pre_occupancy_death_or_illness after a death. Base: 100 % refunded to the estate. Extended: not paid until a processing fee is on the ledger (never), then paid to the resident.
  - Bears on: no task world (task 0 is a resident's own cancellation). Task 0 file records "no consequence on this world".
  - Affected: `entrance_ext_pre_occupancy_refund.rule` S1-S2, `.overwrite`.
- **F-3 SOURCE-POLICY RED — dropped branch: ordinary monthly amortization loses its rate.**
  - Root cause: overwrite[1] of `entrance_ext_final_period_amortization` supersedes the base S3 clause "of amortization_pct_per_month percent of the entrance fee rounded to the cent half up", which fixes every month's amount. The replacement fixes only "the final period".
  - Demonstrated consequence: month 19 of a LifeCare Declining Balance agreement (rate 2.0, 18 months already amortized). Reading A, where the plan rate survives for ordinary months although its clause was superseded, gives 2.0 % → 5,752.00 on a 287,600.00 fee. Reading B, where the replacement step-down is the only stated percentage, gives 1.5 % → 4,314.00. Task 1's seed carries months 19-23 at 4,314.00, which only reading B produces.
  - Bears on: task 1 (the seed was built on reading B, and those rows leak the step tier; see task 1 F-T1-2). Ordinary amortization is not itself a scored write in either task.
  - Affected: `entrance_ext_final_period_amortization.overwrite[1]`; task 1 seed `entrance_ledger` amortization rows months 19-23.
- **F-4 SOURCE-FACTOR RED — amortization_step_rate ladder collapses on three plans.**
  - Root cause: the ladder is 1.0 (36+) / 1.5 (18-35) / plan `amortization_pct_per_month` (fewer than 18).
  - Demonstrated consequence: two tiers select the same value. On LifeChoice 75% Refundable (plan rate 1.5) the 18-35 tier and the fall-through both select 1.5. On LifeChoice 90% Refundable and LifeCare 90% Refundable (plan rate 1.0) the 36+ tier and the fall-through both select 1.0, and the "steps down" tier at 18-35 is a step *up* to 1.5, which no amortization schedule applies.
  - Bears on: task 1 is on LifeCare Declining Balance (2.0), so its three tiers are distinct on that world. The defect is the charter's.
  - Affected: `entrance_ext_final_period_amortization.factors[amortization_step_rate]`, rule S6.
- **F-5 SOURCE-FACTOR RED — medical-expense percentage ladders keyed to an individual's own history are not a treatment that line of business applies.**
  - Root cause: a CCRC's medical-expense percentage of the entrance fee and of the monthly fee is a community-wide allocation (actuarial/cost-based) for the contract type and year, the same for every resident on that plan. The charter itself treats it so in `parameter_schema`, where it is per plan.
  - The flagged ladders make the percentage depend on the individual resident's own history:
    - post_acute_monthly_pct: "The monthly fee portion's percentage reflects post-acute care received during the year" — 41.0 / 39.5 for one's own recovery nights;
    - closing_entrance_pct: "The percentage applied to that entrance fee amount rises with the months of occupancy amortized over the whole agreement";
    - closing_il_pct: "follows how much of the closing year was lived".
  - The conditions (own rehab nights, own tenure, own months lived) are not weighed by any CCRC for that quantity. The fall-through for the four LifeChoice plans is 0.0, so the tiers would state 41-45 % of fees as medical on a fee-for-service plan whose monthly fee prepays no care.
  - Consequence: these three factors are struck. The closing-year computation keeps 3 factors with 1 `parameter` (closing_entrance_basis, closing_il_basis, post_residency_deduction), below the 4-factor / 2-parameter floor. The annual computation keeps 5 (2 parameter / 3 method).
  - Bears on: task 1.
  - Affected: the three factors and their rule sentences.
- Observations (charter-global, no demonstrated consequence on a task world): O-1, O-2 (above); O-3 negative balance after an escrow-interest refund on a cancelled agreement; O-6 annual/closing "terminated" vs "ended"; O-7 `RND` is not half-up on exact binary halves; O-8 state_gate `gate` names a field, edge-3 `effect` phrased from one scenario; O-9 base estate-documents order grounds no edge; O-10 replacement text of the cancellation fee overwrite summarises only the notice ladder; O-11 the pre-occupancy refund deadline is dropped from the merged text; O-12 base tax-letter deadline vs late missed-run issue; O-13 `entrance_refund_calculation` missing from estate `base_policy_refs`; O-14 internal_move_rounding mixes a multiplier with a rounding direction under a `method` label, and its rounding direction varying with tenure is not a business convention; O-15 interest_day_inclusion varies a day-count convention by payee type, which no business does — recorded as an observation because the realism judgement is less clear-cut than F-5.

## closing_checklist

Written after both reveals (2026-10-05T09:16Z). The charter-global sections above were frozen pre-reveal at sha256 60bad74f5e7d9776974cae6e312a1455fc4101df40f1bd13881d299c22d6a69f and are unchanged.

- Per-task files: `task_0.md` and `task_1.md` correspond one to one with tasks 0 and 1. Each has a frozen section written before any reveal and a `source_gt_comparison`. First revision; no older revisions.
- Comparison verdicts:
  - task 0 **PASS**;
  - task 1 **SOURCE-FACTOR RED** (F-T1-1, F-T1-2). The blind derivation equals GT on every scored argument in both tasks.
- Coverage and scope: the six extended policies are covered. Scopes {cancellation_processing_fee, pre_occupancy_refund} and {final_period_amortization, annual_tax_letter, closing_year_tax_letter, estate_refund_release} are pairwise disjoint and jointly complete, and match `charter_scope` of both tasks. Task tools and GT are closed. uuid8s are distinct.
- Trees:
  - task 0: 1 prerequisite problem, 1 value_input edge, user write present;
  - task 1: 3 prerequisite problems, 2 value_input edges, user write present (root).
  - The difficulty-wide graph is acyclic.
- Factors:
  - task 0: all 9 factors bear weight against honest baselines, and the whole baseline gives 8,126.00 / 38,272.00 ≠ gold.
  - task 1: all 20 bear weight numerically. The closing-year computation keeps only 3 real factors / 1 parameter after F-5, and amortization_step_rate's tier is leaked by the seeded months 19-23 (F-T1-2).
- Charter-level REDs F-1 (undeclared "0.0 plan → 0.00" override), F-2 (pre-occupancy refund gate vs death/illness refund), F-3 (dropped ordinary-month amortization rate), F-4 (step-rate ladder collapse on 1.5 % / 1.0 % plans) and F-5 (unreal medical-expense percentage ladders) stand. Only F-3 (through F-T1-2) and F-5 (through F-T1-1) bear on a task's scored world.
- **The difficulty does not close.** It does not pass the source-layer audit in this round. The instantiation-stage gates are therefore not re-run on a final form here. The round-1 gate snapshot supplied with the brief remains the only gate evidence.

## revision_2

### charter_global_frozen (revision_2)

- Re-audit round 2, by the same independent auditor. Freeze time 2026-10-05T09:59Z (wall clock), before either round-2 task JSON was opened.
- Inputs re-hashed by the auditor; they match the coordinator's round-2 MANIFEST and the originals under `tasks/`:
  - `entrance.extended.yaml` 056b1ff64e62d5ca011e57a96811fbb347b82fe02d6877e771d3ed6145a599cb — **changed** from round 1 (c593bac6…).
  - `task_tools.py` 04a31a9c…a4e3336 — unchanged.
  - `task_0.view.json` c9256f57…7c38 — unchanged.
  - `task_1.view.json` c403a4ad…598a05 — changed.
- Because the extended charter changed, every charter-global section is re-derived in full below rather than carried forward. The round-1 text above is left untouched.
- Base section lines 1-1196 are still byte-identical to `blueprint/products/entrance.yaml`. The base sentences cited in round 1 read the same, verified on entrance_occupancy_and_amortization S3 and entrance_tax_letter_policy S1-S4.
- contamination_disclosure (difficulty level): the auditor read both tasks' round-1 GT in round 1, so the round-1 scored values are known. The brief says task 1's scored values changed but gives none. Round-2 values below come only from evaluating the round-2 charter's own `compute` and the auditor's hand arithmetic over the round-2 views.
- Gate snapshot (coordinator, after rework): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; traceability deferred. Entry conditions complete.

### charter delta found by the auditor (round 1 → round 2)

| policy | change |
| --- | --- |
| cancellation_processing_fee | none (rule, compute, factors identical) |
| pre_occupancy_refund | scope narrowed to "a resident's own cancellation"; new sentence carving out death/illness/injury cancellations ("stays governed by the pre-occupancy cancellation terms of the base charter, outside this rule"); refund deadline restated ("paid no later than pre_occupancy_refund_days calendar days after the cancellation"); prerequisite sentence reworded the same way; compute unchanged |
| final_period_amortization | overwrite[1] replacement and rule S6 now read "Every month of occupancy is amortized at amortization_pct_per_month percent … except the final period of a terminated agreement, whose percentage is the plan's monthly amortization percentage scaled by the months already amortized" (one half / three quarters / the plan's percentage); compute `step_rate` = plan × 0.5 / × 0.75 / × 1 |
| annual_tax_letter | post_acute_monthly_pct removed (monthly fee portion at the plan's percentage); new factor stay_payer_basis (method, respite: LTC-insurer payments, else guest refunds, reduce the stay charges); Independent Living Trial Stay charges excluded from stay charges; "0.0 plan → 0.00" stated in the rule and in `result`; window tier 2 now reads "back to the month of the latest deposit payment"; the year-exclusion now says "ended" |
| closing_year_tax_letter | closing_entrance_pct and closing_il_pct removed (both shares at the plan's percentages); new factors closing_care_share (parameter, respite) and closing_stay_payer (method, respite); new respite cross-category read; "0.0 plan → 0.00" stated in the rule and in `result`; edge-3 `effect` generalised |
| estate_refund_release | `base_policy_refs` adds entrance_refund_calculation; nothing else |

### policy_conflict_scan (revision_2)

- Six policies and six tools as in round 1; subjects and tools are unchanged.
- Tax letters: the annual rule now excludes "the one in which the agreement ended", matching the closing rule's "The tax year in which an agreement ended". Disjoint (O-6 fixed).
- Refund payments: the pre-occupancy refund now covers only "a cancellation signed by the resident or the resident's financial agent". Death/illness cancellations are expressly left to the base terms. The estate release governs a scheduled refund. The round-1 overlap is gone.
- Time anchors, terminal states and cross-category reads are as in round 1, plus respite reads (payer_type) in both letters. All reads are schema-valid: `respite_ledger.payer_type` ∈ {resident_or_family, ltc_insurer}; event `respite_refund` exists; payment_method `insurer_eft` exists. The respite charter itself says "a long-term care insurer may pay a stay directly when the guest assigns benefits".
- Scope partition derived blind: unchanged — task 0 = {cancellation_processing_fee, pre_occupancy_refund}; task 1 = {final_period_amortization, annual_tax_letter, closing_year_tax_letter, estate_refund_release}.

### rule_compute_equivalence (revision_2)

- Re-swept the changed policies:
  - pre_occupancy_refund: compute unchanged. The new scope, carve-out and deadline sentences are not computational, and they invent no compute basis.
  - final_period_amortization: `step_rate` = P × 0.5 / P × 0.75 / P, equal to the rule.
  - annual_tax_letter:
    - `stay_charges` now subtracts Trial Stay charges (O-1 fixed).
    - `stay_charges_borne` implements the insurer / guest-refund / as-counted ladder with the floor at 0.00.
    - `result` returns 0 when both plan percentages are 0.0.
    - `first_payment_age` reads LATEST deposit, and the rule now says "the month of the latest deposit payment" (O-2 fixed by wording).
  - closing_year_tax_letter: the shares use P percentages; care share, Trial-Stay-excluded charges, insurer / early-departure / full ladder, 0.0-plan gate. All equal to the rule.
- Wording point O-17 (annual): S7 says the care-stay share "applies to the stay nightly charges counted", while S9 states the charges "counted are reduced by the insurer's payments", and compute applies the share to `stay_charges_borne`. S9 modifies the counted charges themselves, so a single reading results (share × charges after the insurer reduction). Observation.
- Every tier of every declared factor is a rule sentence and a branch of its `decides` binding, and the reverse holds (checked for the 29 factors).
- O-7 (`RND` vs half-up) stands as an observation.

### action_binding_and_uuids (revision_2)

- `task_tools.py` is unchanged (same hash), so the round-1 conclusion is carried forward on that ground: unique `(target_tool, computes)`, docstrings silent about sequence, bodies that never judge a prerequisite, six distinct uuid8s.
- The charter's `target_tool`/`computes` pairs are unchanged.

### prerequisite_graph (revision_2)

- Edges are unchanged in endpoints, kinds, gates, forms and resolved_by. Machine re-check: every `policy_source` is verbatim in its own rule and not restated in the depended rule; every resolved_by equals the depended policy's target tool; the value_input gates `fee_retained`, `amortization_in_year` and `refundable_amount` are compute bindings. The graph is acyclic.
- Edge 3 `effect` now reads "Each missing annual letter for an earlier tax year is entered…", matching its condition (O-8 fixed in that part). The state_gate `gate` still names a field, not an eligibility id (O-8 residual, observation).
- New O-18: edge 2 `effect` still says "the count of amortization entries rises by one". That is true of the world, but the closing-year compute no longer reads the count since closing_entrance_pct was removed. Stale wording, no consequence.

### prerequisite_sentences (revision_2)

- Edge 1 sentence is now "A refund on a resident's own cancellation before occupancy is not paid until the agreement stands in cancelled status and its ledger carries the processing fee retained on that cancellation." It passes the four-point test: "not … until", a record-visible state, no tool/id/snake, and the same scope as its condition, which now matches more exactly because the sentence itself is limited to the resident's own cancellation.
- The single resolving write is unchanged (signed cancellation).
- Edges 2-5 have verbatim the same sentences as round 1, with the same single-reading derivations.
- No new cross-problem order appears in any rule.

### override_declarations (revision_2)

- pre_occupancy_refund:
  - Base pre_occ S2 (death/illness, 100 %, to the estate) is no longer contradicted: the extended rule expressly leaves it outside. **F-2 closed.**
  - The deadline is restated in the rule, so the merged text keeps it (O-11 fixed).
  - Base refund_timing "closed once … 0.00" vs the negative balance after escrow interest: O-3 stands as an observation (cancelled has no `closed` transition).
- final_period_amortization:
  - The superseded rate clause is now replaced by a sentence that keeps the plan rate for every ordinary month and scales only the final period. The merged base S3 now has a rate for every month and a single reading. **F-3 closed.**
- annual / closing letters:
  - The base continuation "a plan whose percentages are 0.0 receives a letter stating 0.00" is now stated in both extended rules ("…whatever else the window holds" / "…whatever else the closing year holds") and implemented in `result`. It is followed, not overridden. **F-1 closed.**
  - O-12 (deadline vs late missed-run issue) stands as an observation.
- estate_refund_release: `entrance_refund_calculation` is now in `base_policy_refs` (O-13 fixed). The rest is as in round 1.
- cancellation_processing_fee: unchanged; O-10 stands as an observation.

### factor_ladders (revision_2)

| policy | factors (effect) | P / M | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- |
| cancellation_processing_fee | unchanged (round 1 table) | 3 / 2 | extension surcharge | respite, independent |
| pre_occupancy_refund | unchanged | 2 / 2 | — | — |
| final_period_amortization | final_month_share (M), final_month_count_end (M), amortization_step_rate (P), estate_surrender_reduction (P) | 2 / 2 | count_end, surrender | independent |
| annual_tax_letter | letter_window (M), settlement_basis (M), stay_payer_basis (M), care_stay_share (P), stay_charges_basis (M), stay_addon_share (P) | 2 / 4 | — | independent, respite |
| closing_year_tax_letter | closing_entrance_basis (M), closing_il_basis (M), post_residency_deduction (P), closing_care_share (P), closing_stay_payer (M) | 2 / 3 | closing_entrance_basis | independent, respite |
| estate_refund_release | unchanged | 2 / 3 | campus rate | — |

- **F-4 closed.** amortization_step_rate now selects plan × 0.5 / plan × 0.75 / plan. On every plan the three tiers are distinct and descending: 2.0 → 1.0 / 1.5 / 2.0; 1.5 → 0.75 / 1.125 / 1.5; 1.0 → 0.5 / 0.75 / 1.0. It no longer steps *up* on any plan. A tenure-scaled final-period amortization schedule is a plausible contract term.
- **F-5 closed.** The three ladders keyed on the resident's own history are gone. Both letters now apply the plan-wide medical-expense percentages, which is how a CCRC states them.
- The new ladders are real:
  - stay_payer_basis / closing_stay_payer: the medical expense stated is what the resident bore, net of LTC-insurer reimbursement or refunds. That is the unreimbursed-expense treatment a tax statement uses.
  - closing_care_share mirrors the annual care-stay share judged real in round 1.
- Each new ladder has 3 distinct tiers, is stated in the rule, and is implemented. Each `baseline` is its fall-through.
- O-16 (new, latent): closing_stay_payer ranks the insurer tier over the early-departure tier, so a closing year holding both an insurer payment and an early-departure credit nets only the insurer payment. The annual letter nets both, through two separate factors. A business would net both. No task world holds both in the closing year (task 1's 2026 stay has an insurer payment and no credit), so this is an observation.
- O-14 and O-15 stand as observations.
- Counts per policy are within 4-6 with ≥2 parameter and ≥1 method. Per task, a multi-source factor and a cross-difficulty factor are available structurally; seeding and weight are checked per task.

### findings (revision_2)

- Round-1 charter REDs: F-1 closed; F-2 closed; F-3 closed; F-4 closed; F-5 closed (evidence above).
- Round-1 observations: O-1, O-2, O-6, O-11, O-13 fixed. O-8 fixed for edge-3 `effect`; the field-valued `gate` remains. O-3, O-7, O-9, O-10, O-12, O-14, O-15 remain as observations, matching the reworker's claim.
- New: O-16 (closing_stay_payer drops the early-departure netting when an insurer also paid), O-17 (annual S7/S9 wording), O-18 (stale entry-count clause in the edge-2 `effect`). All are observations; none has a consequence on a task world.
- No new charter-level RED.

### closing_checklist (revision_2)

Written after both revision_2 reveals (2026-10-05T10:02Z). The revision_2 charter-global sections above were frozen pre-reveal at sha256 a9d0da6b148b3d4a76c97e654f0ce0c949436ea4f5a6f024a7fb6204c5e56f5f.

- Per-task files `task_0.md` and `task_1.md` each carry revision_1 (untouched) and revision_2, and each revision_2 has a frozen section followed by a comparison. Comparison verdicts: task 0 **PASS** (no regression), task 1 **PASS** (round-1 SOURCE-FACTOR RED closed). The blind derivation equals GT on every scored argument of both tasks.
- Coverage and scope: the six extended policies are covered. The scopes are pairwise disjoint and jointly complete, and match both `charter_scope` entries. Task tools are unchanged and closed. The six uuid8s are distinct.
- Trees:
  - task 0: 1 prerequisite problem, 1 value_input edge, user write;
  - task 1: 3 prerequisite problems, 2 value_input edges, user write (root).
  - The difficulty graph is acyclic.
- Factors:
  - task 0: 9 factors, all bearing weight; whole baselines 8,126.00 / 38,272.00 ≠ gold.
  - task 1: 20 factors, all bearing weight, all real after the rework. Whole baselines 5,752.00 / 3,495.80 / 3,495.80 / 143,608.27 ≠ gold (191.73 / 22,768.05 / 3,886.83 / 144,243.69).
  - Each task has at least one multi-source factor and at least one cross-difficulty factor, with seeded rows.
- Charter REDs F-1 to F-5: all closed (§ revision_2 findings).
- Remaining observations: O-3, O-7, O-8 (field-valued gate), O-9, O-10, O-12, O-14, O-15, O-16, O-17, O-18.
- Gates on the final form: the coordinator's post-rework snapshot is EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; traceability is deferred to the render stage (KB unpublished). The snapshot was taken on the same artifacts the auditor hashed. Per Step 0 the auditor cites it and does not re-run it.
- **The difficulty passes the source-layer audit in revision_2.**
