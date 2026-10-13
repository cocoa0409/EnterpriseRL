# Policy-task audit — home_loan_servicing / charter-global

## charter_global_frozen

- Scenario: `env/env_0048_manufactured_home_community_operator`; difficulty `home_loan_servicing` (category `loan`), M = 2.
- Freeze hashes (re-checked with sha256sum at audit start, identical to the coordinator's HASHES.txt):
  - `tasks/home_loan_servicing/loan.extended.yaml` sha256 `2295b651337092be327a2cfa930f4809e5a660d70b2a6683401cf94f87af9cf2`
  - `tasks/home_loan_servicing/task_tools.py` sha256 `b49621f3b7b16747910dcf929edbc53accc326da4a958c2d483af5eba016d4c6`
- Freeze time: 2026-10-08T23:17Z (written before any task JSON was opened). Auditor: independent policy-task auditor (Claude agent), not the instantiating agent.
- Read for this section: `blueprint/blueprint.yaml`, `blueprint/products/loan.yaml`, `blueprint/products/resale.yaml` (the cross-read parameters and `resale_closing_conditions`), `blueprint/share_tools.py`, the extended charter, `task_tools.py`, and the gate snapshot `.audit_views/policy_task/home_loan_servicing/GATES.txt`. The restricted-expression semantics (`MONTHS`, `DAYS`, `within_months`, `RND`, `CFIELD`, `CPARAM`, `XLATEST`) were read from `skills/erl-task-instantiate/scripts/check_compute.py` (read only).
- Masked / not read at this point: every `tasks/home_loan_servicing/tasks/*.json` file and every masked field (`evaluation_criteria`, `computations`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `charter_scope`, `required_documents`, closure fields). Nothing in this section comes from a revealed GT.
- Entry conditions (Step 0): the gate snapshot came with the brief (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cache_diff, check_cross_fire all rc=0; check_traceability deferred to render). The masked views and hashes were supplied. Input complete.

### policy_conflict_scan

The base section of `loan.extended.yaml` (lines 1–1367) is byte-identical to `blueprint/products/loan.yaml` (diff shows only the two added lines 1368–1369: a blank line and the `# ==== extended policies ...` comment).

Seven extended policies, each with its own subject, target tool and computed quantity:

| policy | subject | computes | target_tool (owner) | prerequisite edges |
| --- | --- | --- | --- | --- |
| loan_ext_escrow_analysis | loan_escrow_analysis, loan_escrow_change | new_monthly_escrow | issue_escrow_analysis_2b6c143e (agent) | [] |
| loan_ext_returned_payment_fee | loan_nsf_fee | amount | assess_returned_payment_fee_86f751f1 (agent) | [] |
| loan_ext_good_faith_payment | loan_partial_payment | amount | make_good_faith_payment_f58b4303 (user) | [] |
| loan_ext_deferment_fee | loan_deferment_agreement, loan_deferment_fee | deferment_fee | sign_deferment_agreement_a442f6a7 (user) | escrow_analysis (value_input), returned_payment_fee (value_input), good_faith_payment (state_gate) |
| loan_ext_late_charge | loan_late_charge | amount | assess_late_charge_8f52dfa4 (agent) | [] |
| loan_ext_payoff_statement | loan_payoff_statement | payoff_amount | issue_payoff_statement_6569642c (agent) | late_charge (value_input) |
| loan_ext_sale_paydown | loan_curtailment | amount | make_principal_paydown_1606199b (user) | payoff_statement (value_input) |

Overlap scan:
- Subjects: no two extended policies share a subject event. `loan_ext_good_faith_payment` (partial payment) and `loan_ext_sale_paydown` (curtailment) both refine `loan_evt_payment_application`, but on disjoint events.
- Shared quantities read across policies: fees owed (written by the late charge, read by the payoff); the count of returned-payment fees (written by the returned-payment fee, read by the deferment fee's add-on); the monthly escrow deposit (written by the escrow analysis, read by the deferment fee's scheduled installment); the payoff statement (written by the payoff policy, read by the sale paydown). Each of these is a declared prerequisite edge. No undeclared read-after-write between policies.
- Trigger and time anchors: `state_due` policies (escrow analysis, returned-payment fee, late charge) are owed on world state, `on_request` policies on the customer's ask. Time anchors (analysis date, fee date, payment/signing date, assessment date, statement date, paydown date) all fall on the handling date. No conflicts found.
- Cross-category reads: insurance (escrow analysis, deferment fee), lease (good-faith, deferment fee, late charge, payoff, sale paydown), utility (good-faith), resale (payoff, sale paydown). All are read-only branches, and none writes another category.
- Terminal states: the only status-bearing write is none (no transitions). The deferment tool moves `next_due_date` and `maturity_date` and adds to `deferred_months_total`, which matches base `loan_deferment_terms` sentence 5.
- Cross-charter observation (O-8 below): `resale_closing_conditions` says "A home financed by Hearthstone Home Finance closes only with the payoff amount on a current payoff statement paid from the proceeds; when the proceeds would not cover it the sale cannot close and the request goes to a human representative." That governs the closing, while `loan_ext_sale_paydown` governs a pre-closing principal paydown. The two can be read together without contradiction.

Scope partition derived from the charter alone (compared against GT later in each task file). Two connected components of the prerequisite graph:
- {loan_ext_deferment_fee ← loan_ext_escrow_analysis, loan_ext_returned_payment_fee, loan_ext_good_faith_payment}
- {loan_ext_sale_paydown ← loan_ext_payoff_statement ← loan_ext_late_charge}

With M = 2, one tree per component covers all seven policies, and the two are pairwise disjoint.

### rule_compute_equivalence

Check 2 over all seven policies. Every compute binding has a `compute_basis` quotation that is a verbatim substring of that policy's `rule`. I swept back sentence by sentence over each rule and each factor ladder (every tier present in the rule prose and in the `decides` binding):

- loan_ext_escrow_analysis. Projection order, cushion ladder, deposit-window ladder, spread ladder, days past due and coverage term are all quoted and implemented. Discrepancy inside the rule (O-2): the otherwise tier of the deposit window says "the installments that fall due after the analysis date and on or before the last day of the home's current coverage term, that is the whole months from the analysis date to that last day". The compute implements the second phrase (`11 - MONTHS(coverage_start, NOW)`). The two phrases are not equivalent in general. Example from the seeded 2025-09-30 analysis of task 0's loan: due day 1, term ending 2025-11-11, installments 2025-10-01 and 2025-11-01 give 2, but whole months 2025-09-30→2025-11-11 gives 1, and the seeded escrow balance only reconciles with 1. On both task worlds' handling dates the two phrases agree (task 0: 2026-10-08→2026-11-11 holds one installment, 11-01, and one whole month), so no scored value is affected. Recorded as an observation.
- loan_ext_returned_payment_fee. Channel, window, multiplier and reason ladders are all quoted. The window's "fewer than 12 whole months separate" matches `_within` (`0 <= MONTHS(d, NOW) < 12`).
- loan_ext_good_faith_payment. Installments past due, P&I past due, percentage, seasoning, repeat, history, standing and rounding points ("rounded half up once at the end", "halved and rounded down", "times 0.75 rounded up") are all quoted and implemented.
- loan_ext_deferment_fee. Installments deferred (min with deferment_max_months_per_request), scheduled installment, deferral charge with rounding point, the five tiered inputs and the relationship adjustment are all quoted and implemented. The base lifetime cap (`deferment_lifetime_max_months`) is not in `installments_deferred` but stays inherited as base eligibility (O-12).
- loan_ext_late_charge. The rule says "otherwise the most recent installment received, received after its grace period". The compute `charge_due` else-branch takes `LATEST(... installment_due_date ...)` without checking receipt after grace. The rule's opening sentence ("A late charge is owed on an installment that was not paid in full within its grace period") gates the write, so compute is only wider on worlds where no charge is owed (O-7). The prompt-cure counting is consistent with base: "assessed no earlier than the day after the due date plus late_charge_grace_days" means receipt on day due+16 is 1 day after grace.
- loan_ext_payoff_statement. Day-count tiers, lien fee, statement fee, escrow adjustment, good-through period and weekend roll are all quoted. `last_paid_due` (LATEST installment_due_date of installment payments) agrees with base `loan_msr_payoff_interest_days` ("the same day one month before next_due_date") on any world without a returned or deferred newest installment. Both task 1 values are 2026-09-15.
- loan_ext_sale_paydown. Payoff measure, commission, closing charges, resale fees deducted, lease arrears and margin are all quoted. The resale parameters it reads exist in `products/resale.yaml` (`commission_pct`, `minimum_commission`, `transaction_fee`, `closing_fee`, `inspection_fee`, `inspection_fee_credited_at_closing`, `fees_deducted_from_proceeds`, `vacant_home_check_fee_monthly`, `seller_arrears_paid_from_proceeds`).

No compute binding invents a basis, and no rule sentence lacks an implementation, apart from the two noted (O-2, O-7). Neither moves a scored value on either task world.

Rounding observation (O-6): `compute_basis` says "rounded half up", but the checker's `RND` is Python `round(float, 2)`, which rounds half to even on binary floats. None of the gold-candidate values derived in the task files lands on an exact half cent, so no scored value is affected.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one extended policy (table above), and no base policy names a target tool.
- The uuid8 tails are 2b6c143e, 86f751f1, f58b4303, a442f6a7, 6569642c, 8f52dfa4 and 1606199b. All seven are distinct, share no common prefix, are not sequential, and none is a copy of another with a new tail. Nothing suggests batch derivation.
- Docstrings: none names another tool. None states the action's position in a sequence or uses before/after/first as an order between actions. The only occurrences are date semantics: "effective from the first installment that falls due after today" (escrow analysis) and "held ... until suspense funds add up to a full installment" (good-faith). The module docstring states "No tool checks eligibility, ordering or prerequisites, and none computes a policy value."
- Function bodies: no tool refuses, errors or hints on an unresolved prerequisite. Each body unconditionally creates its row and updates the balance or field (`issue_escrow_analysis` also sets `monthly_escrow_amount`, and `sign_deferment_agreement` also moves `next_due_date`/`maturity_date`, adds to `deferred_months_total` and books the fee).
- Owners: user for good-faith payment, deferment agreement and principal paydown. This matches the blueprint ("signing a deferment agreement and authorizing autopay are the borrower's own acts"; paydown and good-faith are borrower-authorized payments).

### prerequisite_graph

Check 7:
- `prerequisite` is filled on all seven policies: `[]` on five, three edges on loan_ext_deferment_fee, one on loan_ext_payoff_statement, one on loan_ext_sale_paydown.
- Every `problem` names an extended policy id in this file. None names a base policy or itself.
- The graph is acyclic: deferment → {escrow, nsf, good-faith}; paydown → payoff → late charge.
- Each `policy_source` is a verbatim sentence of that policy's own `rule` (rule lines 1862, 1863, 1864, 2255, 2451 of the yaml).
- All five edges are `form: state` and none carries a `fallback_reason`, which is consistent.
- `kind`/`gate`: value_input `installment`, `returned_fees_12m`, `fees_owed` and `payoff_measure` all name existing compute bindings. The state_gate `loan_holdings.suspense_balance` names a record field the tool moves.
- `resolved_by` equals the depended-on policy's `target_tool` on every edge, and each tool's effect makes the `effect` hold: the escrow tool sets `monthly_escrow_amount`; the nsf tool books a `loan_nsf_fee` row; the good-faith tool books a partial payment and raises `suspense_balance`; the late-charge tool books a row and raises `fees_balance`; the payoff tool books a statement dated today.
- `condition` vs sentence: edge 1's condition adds "and loan_holdings.monthly_escrow_amount is the deposit that analysis set", which the analysis write always brings about together with the notice, so the condition is not strengthened in effect. The other four conditions match their sentences in scope ("every payment returned for a fee-bearing reason" / "every installment that was not paid in full within its grace period" are all-time, and so are the conditions).
- No authoring-viewpoint phrasing ("in this task", "at the opening", "current world") appears in any prerequisite field.

### prerequisite_sentences

Check 6, four-point test per edge:

1. deferment ← escrow analysis: "The deferment fee is fixed only after the loan carries an escrow analysis dated within the twelve months before the signing date."
   - Connective "only after". The state is record-visible (`loan_notices` escrow analysis dated within 12 months), with no tool, id or snake_case. Scope is the 12 months, as in the condition.
   - One write brings it about: `issue_escrow_analysis_2b6c143e`, the only tool that creates a `loan_escrow_analysis` row.
   - Derivation: the reader sees no analysis within 12 months, so looks for the rule that issues analyses. `loan_ext_escrow_analysis` sentence 1 ("An escrow analysis is owed on every loan whose hazard premiums are escrowed once escrow_analysis_interval_months have passed since its last analysis, and it is issued on the analysis date ...") is the only rule producing one. Single reading.
   - "within the twelve months before the signing date" is read inclusive of a same-day analysis. The charter uses "before" inclusively throughout, and the deferment add-on's own window must count a fee charged on the signing date for edge 2 to mean anything.
2. deferment ← returned-payment fee: "Before the deferment fee is fixed, the fees owed on the loan must carry a returned-payment fee for every payment returned for a fee-bearing reason."
   - Connective "Before". The state is record-visible (`loan_nsf_fee` rows against returns). "fee-bearing reason" is the charter's own phrase (base event `loan_nsf_fee`: "a payment returned for a fee-bearing reason") and resolves to the four reasons in `loan_ext_returned_payment_fee` sentence 1.
   - One write: `assess_returned_payment_fee_86f751f1`. Single reading.
3. deferment ← good-faith payment: "The deferment agreement is not signed until a good-faith partial payment received on the signing date stands in suspense."
   - Connective "not ... until". The state is record-visible (a `loan_partial_payment` dated today and `suspense_balance`).
   - One write: `make_good_faith_payment_f58b4303`, the only tool booking a partial payment. "good-faith" resolves to `loan_ext_good_faith_payment`. Single reading.
   - Form defect (O-1): the depended-on rule restates the dependency. `loan_ext_good_faith_payment` sentence 1: "A borrower asking to defer installments through a hardship first makes a good-faith payment, ...". This is an action-form restatement of the same order on the depended-on side, which check 6 excludes ("the depended-on policy's rule does not restate the sentence"). It gives the same order and terminal state as the declared edge, so no second answer can be demonstrated. Recorded as an observation.
4. payoff ← late charge: "The payoff figure is fixed only after the fees owed on the loan carry the late charge due on every installment that was not paid in full within its grace period."
   - Connective "only after". The state is record-visible.
   - One write: `assess_late_charge_8f52dfa4`. The reader resolves it through `loan_ext_late_charge` sentences 1–2. Single reading, provided the world holds at most one uncharged late installment (the late-charge rule's "installment charged" selects one). Verified on task 1's world in its file.
5. sale paydown ← payoff statement: "The principal paydown for a pending sale is not worked out until the loan carries a payoff statement issued on the paydown date."
   - Connective "not ... until". The state is record-visible.
   - One write: `issue_payoff_statement_6569642c`. Single reading.

No rule carries a second wording of its edge, a tool name or another policy id. Apart from O-1, no depended-on rule restates the sentence. I found no cross-problem order in any rule that grounds no declared edge: the paydown's "before closing" refers to the resale closing, which is not a problem of this difficulty. No base rule sentence grounds any edge.

### override_declarations

Check 1 (finding half), base sentence by base sentence for each `base_policy_refs` entry:

- loan_ext_escrow_analysis vs `loan_escrow_terms`:
  - (1) disbursement even below zero: followed.
  - (2) "analyzed every ... projected disbursements ... target low point is escrow_cushion_months ...": named in `overwrite[0]`. Its `replaced_by` states only the projection order, not the cushion ladder, but the superseded clause is named, so the cushion change sits under a declared override (O-3).
  - (3) shortage spread and new deposit: named in `overwrite[1]`.
  - (4)–(5) surplus refund threshold and active-only refund: inherited, not touched.
  - (6) refund after payoff: not touched.
  - Base formula `new_monthly_escrow` is covered by both declarations. Declared.
- loan_ext_returned_payment_fee vs `loan_evt_returned_payment`:
  - (1) reversal and (2) once-only: not touched (returns are seeded).
  - (3) fee sentence: named in `overwrite[0]`.
  - (4) second autopay return cancels autopay: inherited, and the extended rule reads `autopay_enrolled` consistently with it.
  - Base formula `nsf_fee_amount` is covered. Declared.
- loan_ext_good_faith_payment vs `loan_evt_payment_application`, with `overwrite: []`:
  - (1) open loans only and (2) channels: inherited (phone_ach is accepted).
  - (3) full installment satisfies the oldest: inherited. A good-faith payment smaller than an installment never triggers it.
  - (4) suspense and its application at one installment: inherited. Per world, the good-faith amount plus existing suspense must stay below one installment (checked in task 0's file).
  - (5)–(7) leftover money, curtailment and no penalty: not reached.
  - The good-faith amount is a new quantity base does not govern. No undeclared override.
- loan_ext_deferment_fee vs `loan_deferment_terms`:
  - (1) nature, (2) availability, (3) open status, (4) eligibility counts and limits, (5) oldest unpaid installments with dates moving by the months deferred, and (7) modifications to a human: all inherited.
  - (6) fee sentence: named in `overwrite[0]`.
  - The extended "installments deferred ... up to deferment_max_months_per_request" fixes the count within base's per-request cap and leaves the lifetime cap to base eligibility (O-12). Declared.
- loan_ext_late_charge vs `loan_evt_late_charge`:
  - (1)–(2) grace period: followed.
  - (3) charge sentence: named in `overwrite[0]`. `replaced_by` states the community rate only, but the multipliers and prompt-cure adjustment act on the same named clause, so they are declared.
  - (4) one charge per installment and (5) exclusions: inherited.
- loan_ext_payoff_statement vs `loan_payoff_terms`:
  - (1) open loans: followed.
  - (2) issue timing, fee and good-through: named in `overwrite[0]`. The statement-fee ladder and weekend roll act on that named clause.
  - (3) payoff amount (per-diem basis, escrow not netted): named in `overwrite[1]`.
  - (4)–(6) no penalty, payoff receipt and lien release: inherited.
  - Outside `base_policy_refs`, `loan_escrow_terms` sentence 6 ("After payoff, the whole escrow balance is refunded to the borrower") sits beside the escrow-netting tier. It can be reconciled (a netted escrow is consumed at payoff, leaving nothing to refund), so no second payoff figure is entailed. Recorded as O-4.
- loan_ext_sale_paydown vs `loan_evt_payment_application` and `loan_payoff_terms`:
  - The leftover/curtailment/min_curtailment_amount sentence is named in `overwrite[0]`.
  - Curtailment-only, no due-date advance and no penalty are followed.
  - "made on a loan that is current" narrows base's open-loan gate rather than weakening it.
  - `loan_payoff_terms` sentences are untouched (the paydown reads a statement but does not issue one). Declared.

No undeclared override was found in the declared base refs. I checked the three disguised forms (anonymous intermediate, 0/1 multiplier, dropped branch) per policy and found none. No rule or note calls base's output a "wrong value".

### factor_ladders

Structure per policy (labels as declared; "MS" = every non-fall-through tier is a conjunction or disjunction over distinct records):

| policy | factor | label | tiers | MS | cross_difficulty | structural verdict |
| --- | --- | --- | --- | --- | --- | --- |
| escrow_analysis | escrow_projection_source | method | 3 (offer / HIA policy premium / ledger) | partly | insurance | ok |
| escrow_analysis | escrow_cushion_months | parameter | 3 (1.0 / 1.5 / 2) | yes (insurance billing plan AND loan ledger count) | insurance | ok |
| escrow_analysis | escrow_deposit_window | method | 3 | tier 2 yes | — | ok. Tier 2 (negative escrow → one extra installment) is unusual but can't be shown unreal (O-11) |
| escrow_analysis | shortage_spread_months | parameter | 3 written / **2 effective** | — | — | **CG-1 (SOURCE-FACTOR)** |
| returned_payment_fee | return_channel_charge | parameter | 3 | — | — | ok |
| returned_payment_fee | return_count_window | method | 3 | yes (autopay state AND return count) | — | ok |
| returned_payment_fee | return_repeat_multiplier | parameter | 3 | — | — | ok |
| returned_payment_fee | return_reason_charge | parameter | 3 | — | — | ok |
| good_faith_payment | good_faith_percentage | parameter | 3 | — | — | ok |
| good_faith_payment | good_faith_seasoning | parameter | 3 | — | — | ok |
| good_faith_payment | good_faith_repeat_hardship | parameter | 3 | — | — | ok |
| good_faith_payment | good_faith_payment_history | parameter | 3 | yes | — | ok |
| good_faith_payment | good_faith_resident_standing | method | 3 | yes (lease AND utility) | lease (+utility) | **CG-4 (label)** |
| deferment_fee | deferment_agreement_charge | parameter | 3 | — | lease | ok |
| deferment_fee | deferment_repeat_factor | parameter | 3 | nominal only (O-10) | — | ok |
| deferment_fee | deferral_rate_seasoning | parameter | 3 | — | — | ok |
| deferment_fee | deferral_risk_addon | parameter | 3 | — | — | ok |
| deferment_fee | deferral_charge_periods | method | 3 (n², 1, n) | — | — | ok (counting convention) |
| deferment_fee | deferral_relationship_adjustment | method | 3 | same insurance row | insurance | **CG-4 (label)** |
| late_charge | late_rate_by_community | parameter | 3 | — | lease | ok |
| late_charge | late_history | parameter | 3 | — | — | ok |
| late_charge | late_seasoning | parameter | 3 | — | — | ok |
| late_charge | residence_tenure | parameter | 3 | — | lease | ok |
| late_charge | prompt_cure_adjustment | method | 3 | — | — | **CG-4 (label)** |
| payoff_statement | payoff_day_count | method | 3 | — | — | ok |
| payoff_statement | lien_release_fee | parameter | 3 | — | lease | ok |
| payoff_statement | repeat_statement_fee | parameter | 3 | — | — | ok |
| payoff_statement | escrow_netting | method | 3 written / **2 effective** | yes (loan escrow AND resale status) | resale | **CG-3 (SOURCE-FACTOR)** |
| payoff_statement | good_through_period | parameter | 3 | tier 1 same resale row | resale | ok |
| payoff_statement | weekend_roll | method | 3 | — | — | ok (business-day convention; see O-5) |
| sale_paydown | payoff_measure_source | method | 3 written / **2 effective** | yes (loan notice AND resale closing date) | resale | **CG-2 (SOURCE-FACTOR)** |
| sale_paydown | commission_deduction | parameter | 3 | yes (package param AND file sale price) | resale | ok |
| sale_paydown | closing_charges | parameter | 3 | package params only | resale | ok |
| sale_paydown | resale_fees_deducted | parameter | 3 | yes (package flag AND file occupancy) | resale | ok |
| sale_paydown | closing_margin | parameter | 3 | — | — | ok |

Other structural checks:
- Every factor's `bindings` are disjoint from every other factor's in the same policy.
- Every `decides` is an input, never `result`.
- Every tier is stated in the rule prose with its condition and value or method, and is implemented in `compute`.
- Every fall-through equals the declared factor `baseline`, and every `baseline.rule` sentence is a sentence of the `rule`.
- Every policy declares 4–6 factors.

Declared counts per policy (parameter/method): escrow 2/2, nsf 3/1, good-faith 4/1, deferment 4/2, late 4/1, payoff 3/3, paydown 4/1.

Counts after striking the factors CG-1..CG-4 strike (whether the bounds hold is shown per task):
- escrow_analysis: 1 parameter (cushion) + 2 method. **Below the 2-parameter floor** (CG-1).
- good_faith_payment: 4 parameter + **0 method** (CG-4).
- deferment_fee: 4 parameter + 1 method (periods). Bounds hold.
- late_charge: 4 parameter + **0 method** (CG-4).
- payoff_statement: 5 factors, 3 parameter + 2 method (day count, weekend roll). Bounds hold.
- sale_paydown: 4 parameter + **0 method** (CG-2).
- returned_payment_fee: unchanged (3/1).

Cross-difficulty reads per tree: the deferment tree reads insurance (escrow projection, cushion, relationship) and lease (agreement charge, standing). The paydown tree reads lease (late rate, tenure, lien fee) and resale (good-through, netting, payoff measure, commission, closing charges, resale fees).

### findings

**CG-1 — SOURCE-FACTOR (structure); bears on task 0.** `loan_ext_escrow_analysis.shortage_spread_months` has an unreachable effective fall-through and a two-tier real ladder.
- Symptom: the ladder is "Where the analysis finds a shortage and the oldest unpaid installment is 30 or more days past due ... spread_months_delinquent; where it finds a shortage and the oldest unpaid installment is less than 30 days past due ... spread_months_current; otherwise ... escrow_shortage_spread_months installments." Tiers 1 and 2 split every shortage case exhaustively by days past due (≥30 / <30). The fall-through is therefore selected only when the shortage is zero, and then `shortage / shortage_spread` = 0 whatever the spread. So the fall-through value never changes any customer's result. The compound part "finds a shortage" holds of every customer for whom the quantity matters, so it restates the scope instead of dividing customers.
- Root cause: the baseline `escrow_shortage_spread_months` (12) is presented as the standard treatment, but the policy gives it to no customer whose result it could affect. It is a straw-man fall-through, and the real ladder is two tiers (24 / 18).
- Demonstrated consequence: on any world with shortage > 0 the selected spread is 24 or 18. With shortage = 0 the result is `projection/12` for every spread value. The factor fails the three-tier test and the honest-fall-through test, so it is struck. The policy then has one `parameter` factor (cushion), below the minimum of 2.
- Affected: `loan.extended.yaml` loan_ext_escrow_analysis rule sentence 13, `compute.shortage_spread`, `factors[3]`.

**CG-2 — SOURCE-FACTOR (structure); bears on task 1.** `loan_ext_sale_paydown.payoff_measure_source` has a fall-through that no customer reaching the write can be on.
- Symptom: tiers 1 and 2 both require "a payoff statement issued on the paydown date". The policy's own prerequisite sentence ("The principal paydown for a pending sale is not worked out until the loan carries a payoff statement issued on the paydown date") makes that condition true for every borrower who reaches this write. The fall-through and baseline ("the unpaid principal plus fees owed") is never applied to such a borrower.
- Root cause: the condition part restates the write's own prerequisite rather than dividing customers. The real ladder is two tiers: good-through on or after closing vs before closing.
- Demonstrated consequence: by construction, the fall-through is reached only if the paydown is worked out in breach of the policy's own prerequisite. The factor is struck, and `loan_ext_sale_paydown` is left with **0 `method` factors** (the other four are `parameter`), below the minimum of 1.
- Affected: rule sentences 10 and 15, `compute.payoff_measure`, `factors[0]`.

**CG-3 — SOURCE-FACTOR (structure); bears on task 1.** In `loan_ext_payoff_statement.escrow_netting`, two tiers select the same method.
- Symptom: tier 1 "the escrow balance is above zero AND ... under contract → credit the escrow balance against the payoff". Tier 2 "the escrow balance is below zero AND ... under contract → add the advanced amount to the payoff". In `compute`: `0 - F('escrow_balance')` when balance > 0 and `ABS(F('escrow_balance'))` when balance < 0. Both equal `-escrow_balance`, so both tiers apply one method: "settle the signed escrow balance against the payoff when the home is under contract".
- Root cause: one tier is written as two by splitting on the sign of the same quantity.
- Demonstrated consequence: the real ladder is two tiers (under contract → net the escrow; otherwise → 0). The factor is struck. Payoff still has 5 factors (3 parameter, 2 method), so the bounds hold, but the unreal-ladder test fails for any task whose tree contains this computation.
- Affected: rule sentence 14, `compute.escrow_adjustment`, `factors[3]`.

**CG-4 — SOURCE-FACTOR (label); bears on tasks 0 and 1.** Three factors labelled `method` are multipliers in substance.
- Symptom: `good_faith_resident_standing` is {×0.5 round down, ×0.75 round up, ×1}. `prompt_cure_adjustment` is {×0.5 round down, ×0.8 round up, ×1}. `deferral_relationship_adjustment` is {×0.5 round down, ×0.75 round up, ×1}. Each tier takes the same amount and multiplies it by a tier-selected fraction. The only non-numeric difference is a rounding direction attached to each fraction, and no lender varies rounding direction by customer standing. The quantity the business actually varies here is a discount rate, which is a `parameter`.
- Root cause: a multiplier ladder relabelled `method` through rounding-direction decoration. This is the "method whose tiers only substitute a different number into the same formula" shape.
- Demonstrated consequence: counting only factors that pass, `loan_ext_good_faith_payment` has **0 method** factors (task 0's tree) and `loan_ext_late_charge` has **0 method** factors (task 1's tree). `loan_ext_deferment_fee` keeps `deferral_charge_periods` (1 method), so for it this is a label defect without a count consequence.
- Affected: the three `factors[].effect` entries and the corresponding rule sentences.

Observations (no demonstrable consequence on either task's scored solution):
- **O-1** — `loan_ext_good_faith_payment` sentence 1 ("... first makes a good-faith payment ...") restates, on the depended-on side and in action form, the order that `loan_ext_deferment_fee`'s state-form prerequisite sentence carries. This is a check-6 form defect, but the order and terminal state are identical, so no second answer exists.
- **O-2** — In the escrow-analysis deposit-window otherwise tier, "the installments that fall due after the analysis date and on or before the last day ..." and "that is the whole months from the analysis date to that last day" are not equivalent in general (seeded 2025-09-30 analysis on task 0's loan: 2 vs 1). The compute and seed follow "whole months". The phrases agree on both handling dates.
- **O-3** — The escrow-analysis `overwrite[0].replaced_by` does not restate the cushion ladder. The superseded clause containing the cushion is named, so the override is declared.
- **O-4** — The escrow-netting tier (payoff) sits beside base `loan_escrow_terms` "After payoff, the whole escrow balance is refunded to the borrower", which `overwrite` does not name. The two can be reconciled (a netted escrow is consumed at payoff), so no second payoff figure is entailed.
- **O-5** — `weekend_roll` is labelled `method` with tiers of +2/+1/0 days. It is accepted as a business-day convention (a recognised servicing method), but it is the borderline case of the CG-4 shape. Payoff's counts hold either way.
- **O-6** — `compute_basis` says "half up", but the checker's `RND` is Python banker's rounding on floats. No gold-candidate value is at an exact half cent.
- **O-7** — The late-charge `charge_due` else-branch does not filter "received after its grace period". The rule's first sentence gates the write.
- **O-8** — `products/resale.yaml` `resale_closing_conditions` sends a sale whose proceeds would not cover the HHF payoff to a human, and the blueprint's resale summary lists that case as POLICY_NOT_COVERED. A reader of the loan KB alone has an explicit paydown rule for the pre-closing case. A handoff reading is possible but is not the better reading of the two charters. Verdict deferred to task 1's file.
- **O-9** — Base event `loan_payment_return` lists `loan_nsf_fee` as a trigger for fee-bearing reasons, so a seeded fee-bearing return without its fee row (the gap a returned-payment-fee prerequisite needs) sits against the base event model. The extended `state_due` policy makes the fee an agent-assessed write, so the policy surface is consistent.
- **O-10** — The `deferment_repeat_factor` conjunction "an earlier deferment agreement stands AND ≥2 / <2 installments deferred": the first part is implied by `deferred_months_total ≥ 1`, so the factor is not multi-source in substance. Counts are unaffected.
- **O-11** — Deposit-window tier 2 ("escrow below zero → count the next installment too") is an unusual convention. No demonstration of unreality is possible from the charter.
- **O-12** — `installments_deferred` omits the lifetime cap. Base eligibility (inherited) still bounds it.

## closing_checklist

Written after both reveals (task 0 at 2026-10-08T23:21:45Z, task 1 shortly after). Every section above this heading was on disk before either reveal (mtime 23:19:02Z) and has not been changed. Everything below comes after the reveals.

The difficulty does **not close**: not all four relationships PASS for both tasks.

| check | status |
| --- | --- |
| per-task files 1:1 with tasks; `_difficulty.md` alongside; first revision (no older revisions) | yes: `0.md`, `1.md` |
| every comparison section carries a PASS | **no**: task 0 RED (SOURCE-FACTOR; SOURCE-CHAIN on proof figures), task 1 RED (SOURCE-FACTOR) |
| extended policies fully covered; scopes pairwise disjoint | yes: GT `charter_scope` task 0 = {escrow_analysis, returned_payment_fee, good_faith_payment, deferment_fee}, task 1 = {late_charge, payoff_statement, sale_paydown}. This matches the frozen partition in §policy_conflict_scan. |
| task tools and GT closed; uuid8s independent | yes (§action_binding_and_uuids) |
| each tree has 1–3 prerequisites, ≥ max(n−1, 1) value_input edges, an owner=user problem, no cycle; whole graph acyclic | yes: task 0 n=3 with 2 value_input (users: good-faith, deferment); task 1 n=2 with 2 value_input (user: paydown) |
| every computation: self-sufficient baseline, 4–6 factors, ≥2 parameter and ≥1 method that survive the tests, real ladders, weight against an honest baseline | **no**: CG-1 (escrow analysis, 1 parameter), CG-2 (sale paydown, 0 method), CG-3 (escrow-netting duplicate tier), CG-4 (good-faith and late charge, 0 method); task 1 payoff has no near-miss (T1-4) |
| GT proof figures true | **no**: three task 0 figures contradict the half-up rounding rule (T0-3; root cause O-6) |
| gates re-run on the final form | not run by this auditor. Step 0 cites the coordinator's snapshot (all rc=0); a re-run is only owed once the difficulty closes. |

Gold write parameters in both tasks match the independent derivations exactly (task 0: 90.53 / 98.63 / 0.00, 35.00, 433.22, 2 months / 62.55; task 1: 15.38, 2026-11-02 / 65945.39, 3605.39). The unique-solution and policy-self-consistency relationships PASS for both tasks. The failures are in the factor structure (CG-1..CG-4, T1-4) and in three one-cent proof figures (T0-3).

## revision_2

### charter_global_frozen (revision 2)

- Inputs (sha256 verified against the coordinator's round-2 list):
  - `loan.extended.yaml` `530ceda97a0e0aee86d952981e041618554b81e9b8c950c02dc732208cc8ae83`: **changed** from round 1 (`2295b651…`).
  - `task_tools.py` `b49621f3…6c4c6`: unchanged.
- Because the charter changed, every charter-global section is re-derived in full below. Nothing is carried forward by reference except the tool-module checks, whose input is byte-identical.
- The base section (lines 1–1367) is still byte-identical to `blueprint/products/loan.yaml`.
- Freeze: written 2026-10-09 before either round-2 task JSON was opened. Auditor: same independent auditor as round 1.
- Read: the reworked charter, `task_tools.py`, `blueprint/products/{loan,resale,insurance}.yaml` (parameter look-ups only), `share_tools.py`, the round-2 GATES.txt, and the restricted-expression semantics in `check_compute.py`.
- Masked and unread: the round-2 `tasks/*.json` files and every masked field.
- Round-1 texts above are left untouched.
- contamination_disclosure: in round 1 this auditor opened the round-1 `tasks/0.json` and `tasks/1.json` (after freezing), so the round-1 gold values, proof fields and `design_rationale` are known to me. The round-2 worlds differ in exactly the inputs those values depend on (task 0 renewal premium and escrow balance; task 1 closing date and payoff-statement history), so no round-1 figure can be carried into a round-2 answer. No round-2 GT field has been seen.

### policy_conflict_scan (revision 2)

- Same seven policies, subjects, `(target_tool, computes)` pairs, owners and prerequisite edges as round 1. The prerequisite sentences are verbatim unchanged.
- Changes between rounds:
  - The payoff policy dropped the escrow-netting branch. Its rule and `overwrite[1].replaced_by` now say "the escrow balance is not netted and is refunded separately after payoff", which agrees with base `loan_payoff_terms` and `loan_escrow_terms`. Round-1 O-4 is moot.
  - The good-faith policy changed its first sentence, replaced the seasoning multiplier with an installment-count ladder, and relabelled standing as a fraction.
  - The deferment policy added a 36-month window to the repeat factor, put the lifetime cap into the installments deferred, and relabelled relationship as a fraction.
  - The late-charge policy added a history-window ladder and relabelled prompt-cure as a fraction.
  - The sale-paydown policy replaced the payoff-measure ladder with trim / extend / as-is relative to the closing date.
  - The escrow analysis re-tiered the shortage spread on shortage size and rephrased the deposit count.
- Overlap scan: no two policies share a subject or computed quantity. The shared reads (fees owed, the returned-fee count, the escrow deposit, the payoff statement) are still exactly the declared edges. Time anchors are all the handling date. Cross-category reads are read-only. No conflict found.
- Scope partition from the charter (unchanged): {deferment ← escrow analysis, returned-payment fee, good-faith} and {sale paydown ← payoff ← late charge}.

### rule_compute_equivalence (revision 2)

Every compute binding's `compute_basis` is a verbatim substring of its policy's rule. Swept back sentence by sentence and ladder by ladder:

- Rounding: every "rounded half up to the cent" is now implemented as `int(RND(x*100, 6) + 0.5) / 100`. That is half up for non-negative x, and every quantity so rounded is non-negative (target low, shortage, results, deferral charge, relationship charge, payoff interest, daily interest, commission). Round-1 O-6 is **closed** in the compute layer. The checker's own `RND` is still Python `round`, but it now only strips float noise at 6 decimals.
- Escrow analysis:
  - The deposit count is stated once in each tier as whole months: otherwise tier "the whole months from the analysis date to the last day ...", tier 1 "... from the oldest unpaid installment's due date ... plus one", tier 2 "... plus one".
  - `11 - MONTHS(coverage_start, X)` equals the whole months from X to the term's last day for due days 1 and 15 (checked at both day-of-month orders).
  - The round-1 "installments that fall due ..." phrase is gone. Round-1 O-2 is **closed**.
  - The spread compute `shortage >= escrow_projection / 12` matches "at least one month's escrow projection (the escrow projection divided by 12)".
- Good-faith: installment-window tiers, the single final rounding, and the standing fraction all match the rule.
- Deferment:
  - `installments_deferred = MN(months+1, per-request cap, lifetime cap − already deferred)` matches the rule. Round-1 O-12 is **closed**.
  - The repeat factor's `prior_agreements` is now `COUNT(... within_months=36 ...)`, matching "signed on the loan in the 36 whole months before the signing date".
- Late charge: window and multiplier match the rule. Round-1 O-7 (the else-branch does not filter "received after its grace period") is unchanged and remains an observation.
- Payoff: matches after the netting removal.
- Sale paydown:
  - The trim/extend tiers match the rule.
  - New observation **O-14**: `stmt_good_through` is `LATEST(good_through_date by notice_date)` over all statements, while the rule takes the good-through date of "that statement" (the highest-amount statement of the paydown date). The two diverge only when more than one statement exists on the paydown date, which neither world has.

### action_binding_and_uuids (revision 2)

`task_tools.py` is byte-identical to round 1, and the `(target_tool, computes)` claims are unchanged. The round-1 conclusions are carried forward on the grounds of the unchanged hash and unchanged claims: unique bindings, independent uuid8s, docstrings silent about sequence, bodies that never refuse.

### prerequisite_graph (revision 2)

Same five edges and the same `policy_source`, `condition`, `form`, `kind`, `gate` and `resolved_by`. The only text change is the paydown edge's `effect`, which now says "trimmed or extended to the closing date" and matches the new rule. All the round-1 graph checks hold again: filled everywhere, acyclic, sources verbatim in their own rules, `gate` bindings exist (`installment`, `returned_fees_12m`, `fees_owed`, `payoff_measure`), and no authoring-viewpoint text.

### prerequisite_sentences (revision 2)

The four-point test passes on all five sentences, as in round 1. Each state-form edge has exactly one write that brings its state about.

O-1 is **closed**. The good-faith rule's first sentence now reads "A good-faith payment is a one-time partial payment the borrower authorizes on their own loan toward a hardship deferment, and it is held in suspense ...". It states the payment's purpose with no ordering connective, and it no longer restates the deferment edge.

No rule states a cross-problem order outside the declared edges, and no base sentence grounds an edge.

### override_declarations (revision 2)

Base sentences per `base_policy_refs`, re-checked for the changed policies:
- Escrow: `overwrite[1].replaced_by` is now the size-and-delinquency spread ladder, which names the shortage-spread clause it replaces. O-3 is unchanged (`overwrite[0].replaced_by` still omits the cushion ladder, but the clause is named).
- Good-faith: `overwrite: []`. Every base payment-application sentence is followed. The new first sentence repeats base's suspense rule.
- Deferment: the fee clause is declared. The installments-deferred cap now carries base's lifetime limit itself.
- Late charge: the charge clause is declared. The window and fraction act on that named clause.
- Payoff: both superseded clauses are named. The second `replaced_by` keeps base's "not netted ... refunded separately".
- Paydown: the leftover/curtailment clause is declared. `loan_payoff_terms` is untouched.

No undeclared override, and none of the three disguised forms.

### factor_ladders (revision 2)

| policy | factor | label (honest?) | tiers real? | note |
| --- | --- | --- | --- | --- |
| escrow | escrow_projection_source | method, yes | 3 | unchanged |
| escrow | escrow_cushion_months | parameter, yes | 3 | multi-source (insurance plan AND loan ledger) |
| escrow | escrow_deposit_window | method, yes | 3 | O-11 unchanged |
| escrow | shortage_spread_months | parameter, yes | **3, all effective** | Small shortages (0 < shortage < projection/12) now receive the fall-through 12, and large ones 24/18 by delinquency. That matches the industry practice of spreading small shortages over 12 months and longer spreads for large ones. **CG-1 closed.** |
| nsf | four factors | as round 1 | 3 each | unchanged |
| good-faith | good_faith_percentage / repeat / payment_history | parameter, yes | 3 each | |
| good-faith | good_faith_resident_standing | **parameter** (0.5 / 0.75 / 1), yes | 3 | relabelled honestly |
| good-faith | good_faith_installment_window | method (counting rule) | **2 effective (CG-5, new)** | see findings |
| deferment | agreement / repeat / rate / addon | parameter, yes | 3 each | repeat now multi-source in substance (36-month agreement window AND lifetime total). **O-10 closed.** |
| deferment | deferral_charge_periods | method, yes | 3 | |
| deferment | deferral_relationship_fraction | **parameter** (0.5 / 0.75 / 1), yes | 3 | relabelled honestly. **CG-4 (deferment) closed.** |
| late | rate / history / seasoning / tenure | parameter, yes | 3 each | |
| late | prompt_cure_fraction | **parameter** (0.5 / 0.8 / 1), yes | 3 | relabelled honestly |
| late | late_history_window | method (lookback window, as accepted for the returned-payment window in round 1) | 3, all reachable | multi-source (autopay state AND late-charge ledger) |
| payoff | day count, weekend roll | method | 3 each | weekend roll, O-5 unchanged |
| payoff | lien / statement fee / good-through | parameter | 3 each | escrow netting removed. **CG-3 closed.** |
| paydown | payoff_measure_to_closing | method, yes (trim / extend / as is) | **3, all reachable** | The fall-through needs the same-day statement good through the closing date or up to 3 days after. Under the payoff policy an under-contract statement with closing ≤ 30 days is good through closing + 2 (+0/1/2 roll), so +2 and +3 land on the fall-through, +4 on trim, and closing > 30 days on extend. **CG-2 closed.** New observation O-13: the trim and extend tiers value days at the actual/365 daily payoff interest even when the statement itself was computed on actual/360 (2015–2019 contracts). The charter states it outright, so the policy is unambiguous, but the trimmed figure no longer equals the statement's own per-diem. |
| paydown | commission / closing charges / resale fees / margin | parameter | 3 each | |

Counts per policy (surviving parameter / method):
- escrow 2/2
- nsf 3/1
- good-faith 4/**0** (CG-5)
- deferment 5/1
- late 5/1
- payoff 3/2
- paydown 4/1

Cross-difficulty reads: the deferment tree reads insurance and lease; the paydown tree reads lease and resale.

### findings (revision 2)

Round-1 items, re-verified against the reworked charter:

| id | round-2 status | evidence |
| --- | --- | --- |
| CG-1 | **closed** | spread ladder tiered on shortage ≥ projection/12; the fall-through is effective for small shortages |
| CG-2 | **closed** | payoff measure ladder trim / extend / as-is; all three reachable by customers who reach the write |
| CG-3 | **closed** | escrow netting removed; base non-netting restored |
| CG-4 (good-faith) | **relabel closed, method floor NOT closed** | standing is now an honest parameter, but its replacement method factor fails (CG-5) |
| CG-4 (late charge) | **closed** | prompt-cure is now a parameter; late_history_window is a genuine method |
| CG-4 (deferment) | **closed** | relationship is now a parameter; periods remains the method |
| O-1, O-2, O-6, O-10, O-12 | **closed** | see sections above |
| O-3, O-5, O-7, O-8, O-9, O-11 | unchanged (observations) | |
| O-4 | moot | netting removed |

New charter-global finding:

**CG-5 — SOURCE-FACTOR (structure); bears on task 0.** One tier of `loan_ext_good_faith_payment.good_faith_installment_window` is unreachable.
- Symptom: the ladder is "36 or more whole months → months; fewer than 12 whole months → months + 2; otherwise → months + 1", keyed on months since the first installment fell due.
- Root cause: a good-faith payment is, by its own rule, "toward a hardship deferment", and it exists only as the state gate of the deferment agreement. Every program that offers deferment sets `deferment_min_installments_paid` to 12 (10-, 15-, 20-, 23- and 25-Year; the 7-Year offers none). Each unreturned installment payment advances `next_due_date` one month, and deferments push it further. So a deferment-eligible loan has `next_due_date` at least the first payment date + 12 months. The deferment also needs at least one installment falling due on or before the signing date ("whole months ... plus one"), so `next_due_date` must be on or before the payment date. Together: whole months from the first installment to the payment date ≥ 12.
- Demonstrated consequence: the "fewer than 12 whole months" tier holds of no borrower for whom a good-faith payment is taken. The ladder has two real tiers (≥36 → months; 12–35 → months + 1), so it fails the three-tier test and is struck. That leaves the good-faith computation with **0 genuine method factors**: standing is now honestly a parameter, and percentage, repeat and history are parameters. The round-1 method-floor defect (T0-2) therefore persists in a new form.
- Affected: loan_ext_good_faith_payment rule sentence 6, `compute.installments_past_due`, `factors[1]`.

New observations: **O-13** (paydown trim/extend per-diem basis) and **O-14** (paydown good-through look-up with several same-day statements). Neither affects either world.

### closing_checklist (revision 2)

Written after the round-2 reveals (09:15:00Z). Everything in revision_2 above this heading was on disk before (mtime 09:13:46Z) and is unchanged.

The difficulty does **not close**.

| check | status |
| --- | --- |
| per-task files 1:1, revision_2 appended, round-1 text untouched | yes |
| every comparison section PASS | **no**: task 0 RED (SOURCE-FACTOR, CG-5 / T0-4), task 1 RED (SOURCE-FACTOR, T1-5) |
| coverage complete; scopes disjoint | yes: GT scopes {escrow, nsf, good-faith, deferment} and {late, payoff, paydown}, matching the frozen partition |
| tool bindings and uuid8s | yes (module unchanged) |
| trees: 1–3 prerequisites, ≥ max(n−1, 1) value_input, user write, acyclic | yes for both |
| factor bounds and ladders | **no**: good-faith has 0 genuine method factors (CG-5); the late-charge computation of task 1 lacks a near-miss (T1-5). All other round-1 factor defects are closed (CG-1, CG-2, CG-3, CG-4 late / deferment) |
| GT proof figures true | yes: every round-2 figure matches the half-up recomputation (T0-3 closed) |
| gates re-run on final form | not run by the auditor; the coordinator's round-2 snapshot (all rc=0) is cited |

Round-2 regressions or new defects: CG-5 (introduced by the T0-2 rework) and T1-5 (introduced by the late-history rework). New observations: O-13 and O-14.

Gold write parameters in both tasks match the independent derivations exactly.

## revision_3

### charter_global_frozen (revision 3)

- Inputs (sha256 verified):
  - `loan.extended.yaml` `fbb2ee5e8a064172dc07b687bef6ed846e5b63b3cfcf99b15fa2002d6b1f0cf4`: **changed** from round 2 (`530ceda9…`).
  - `task_tools.py` `b49621f3…6c4c6`: unchanged.
  - The base section is still byte-identical to `blueprint/products/loan.yaml`.
- Written 2026-10-09, before either round-3 task JSON was opened.
- contamination_disclosure: round-1 and round-2 GT of both tasks are known to me from earlier rounds (each opened only after its freeze). No round-3 GT has been seen.
- Method: because the charter changed, every policy was re-read.
  - Five policies (escrow analysis, returned-payment fee, deferment fee, late charge, payoff statement) have rule, compute, factors, prerequisite and params identical to the round-2 text this audit derived from, and every policy keeps its round-2 start line. Their revision_2 conclusions are re-confirmed, not merely carried.
  - The changes are confined to `loan_ext_good_faith_payment` and `loan_ext_sale_paydown`, re-derived in full below.

### changed policies, re-derived

**loan_ext_good_faith_payment**:
- The installment-window ladder thresholds moved from 36 / 12 months to 48 / 24 months, consistently in rule sentence 6, `compute_basis`, `compute.installments_past_due` (`>= 48` / `< 24`) and `factors[1].ladder`. The baseline (`months + 1`) is still the fall-through, now for 24–47 months.
- All other sentences, bindings, params and factors are as in round 2.
- Reachability, given that a good-faith payment is taken only toward a deferment for which the borrower is eligible: a deferment-eligible loan has at least 12 installments paid and a past-due installment, so whole months since the first installment ≥ 12 (`_difficulty.md` revision_2 CG-5 argument).
  - The "fewer than 24" tier now covers 12–23 months, which is reachable.
  - "otherwise" covers 24–47 months, reachable.
  - "48 or more" is reachable.
  - All three tiers are disjoint and distinct in method (months + 2 / months + 1 / months).
- Business reading: a newer loan's good-faith payment also counts the next installment, a mid-seasoned loan's counts every installment due, and a long-seasoned loan's counts only those a full month late. That is a plausible hardship-programme convention, not demonstrably unreal.
- **CG-5: closed.** Good-faith now has 4 parameter / 1 method factors.

**loan_ext_sale_paydown**:
- `stmt_good_through` now also filters `notice_date=NOW`, so the good-through date is read only from statements issued on the paydown date.
- **O-14: narrowed, not eliminated.** With several same-day statements, `LATEST` by `notice_date` (all ties) returns the first row encountered, not necessarily the highest-amount statement the rule calls "that statement". It cannot arise in either world (one statement per paydown date); it remains an observation.
- Rule text, factors and params are unchanged. **O-13** (trim and extend at the actual/365 daily even on a /360 contract) is unchanged in the charter. The reworker says a rationale note was added; any such note would be in the task JSON, not the charter. It remains an observation.

### sections re-confirmed for revision 3

- **policy_conflict_scan:** no subject or quantity overlap; shared reads are exactly the declared edges; scopes as before.
- **rule_compute_equivalence:** holds, including the two changed bindings. O-7 is unchanged.
- **action_binding_and_uuids:** unchanged module, so carried on the identical hash.
- **prerequisite_graph** and **prerequisite_sentences:** five edges, sentences verbatim unchanged; O-1 stays closed.
- **override_declarations:** no change in any `overwrite`; no undeclared override.
- **factor_ladders:** counts are escrow 2/2, nsf 3/1, good-faith 4/1, deferment 5/1, late 5/1, payoff 3/2, paydown 4/1. Every ladder has three real tiers.

### findings (revision 3)

| id | status |
| --- | --- |
| CG-5 | **closed** |
| O-14 | narrowed (observation) |
| O-13 | unchanged (observation) |
| O-3, O-5, O-7, O-8, O-9, O-11 | unchanged (observations) |
| all other round-1 and round-2 items | remain closed |

No new charter-global finding.

### closing_checklist (revision 3)

Written after the round-3 reveals (10:15:30Z). Everything in revision_3 above this heading was on disk before (mtime 10:15:22Z) and is unchanged.

The difficulty **closes** for the source-layer audit: both tasks PASS all four relationships.

| check | status |
| --- | --- |
| per-task files 1:1 with tasks, `_difficulty.md` alongside; revisions 1–3 appended, older text untouched | yes |
| every comparison section carries a PASS | yes (revision 3: task 0 PASS, task 1 PASS) |
| extended policies fully covered; scopes pairwise disjoint (whole trees) | yes: {escrow analysis, returned-payment fee, good-faith, deferment} and {late charge, payoff statement, sale paydown}, matching the charter-derived partition |
| task tools and GT closed; each uuid8 independent and frozen | yes (module unchanged since round 1) |
| each tree: 1–3 prerequisites, ≥ max(n−1, 1) value_input, an owner=user problem, no cycle; difficulty graph acyclic | yes: task 0 n=3 with 2 value_input (users: good-faith, deferment); task 1 n=2 with 2 value_input (user: paydown) |
| every computation: self-sufficient baseline giving a definite number ≠ gold; 4–6 factors with ≥2 parameter and ≥1 method that survive the tests; ≥1 multi-source and ≥1 cross-difficulty per task; ladders of three real tiers stated in the rule; every factor bears weight against an honest baseline; near-miss present | yes. Counts: escrow 2/2, nsf 3/1, good-faith 4/1, deferment 5/1, late 5/1, payoff 3/2, paydown 4/1. In task 0 the near-misses exist but are tier-neutral (observation). |
| GT proof figures true | yes: all round-3 figures match the half-up recomputation |
| gates on the final form | the coordinator's round-3 snapshot was run on the final artifacts after the rework (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK; CACHE-DIFF info; all rc=0). It is cited, not re-run by the auditor; check_traceability is deferred to the render step. |

Remaining observations (not grounds for rework):
- O-3: escrow `replaced_by` omits the cushion text.
- O-5: weekend roll as a method.
- O-7: late-charge else-branch filter.
- O-8: resale closing-handoff rule beside the pre-closing paydown.
- O-9: base nsf trigger vs a seeded uncharged return.
- O-11: deposit-window tier 2 convention.
- O-13: paydown trim/extend at the /365 daily.
- O-14: several same-day statements.
- Task 0's tier-neutral near-misses.
- Task 1's overstated multi-source list in GT.
