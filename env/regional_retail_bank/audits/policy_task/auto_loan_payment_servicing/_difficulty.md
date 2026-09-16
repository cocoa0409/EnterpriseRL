# Policy-task audit — auto_loan_payment_servicing / charter-global

## charter_global_frozen

- auditor: independent source-layer auditor (not the instantiating agent); revision 1.
- freeze time: 2026-09-16 (repo clock), written before any task's `evaluation_criteria` / `computations` were read.
- frozen inputs and their hashes:
  - `env/regional_retail_bank/tasks/auto_loan_payment_servicing/auto.extended.yaml`
    sha256 `f1f7344d864fd0ba46f60f1778c42f50f047546069f6246f46c3dec948e2ab1a`
  - `env/regional_retail_bank/tasks/auto_loan_payment_servicing/task_tools.py`
    sha256 `f31b4354f63165e8aec9a1e65470e7b7a9e9fc10c59930eca9c3512b96f767a0`
- fields permitted while this section was written: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`,
  `blueprint/share_tools.py`, `blueprint/products/auto.yaml`, `blueprint/products/checking.yaml`
  (only for `waiver_min_daily_balance`, which `CPARAM('checking', …)` reads), the whole of
  `auto.extended.yaml`, the whole of `task_tools.py`.
- fields explicitly masked and not read: `evaluation_criteria`, `computations`, `charter_scope`,
  `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`,
  `db_closure`, `db_closure_matches_initial_state` for both tasks. The masked views used were
  `/tmp/claude-10250/…/scratchpad/masked/auto_loan_payment_servicing/{0,1}.json`,
  sha256 `757aedc9…461d6f` and `487a1fa3…5d73133e`, which contain only `frozen_time`,
  `user_scenario` and `initial_state`.
- entry condition: the instantiation-stage gate snapshot (EXTENDED, TASK-TOOL-CONTRACT, REPLAY,
  SOLVABILITY, COMPUTE, GROUNDING, SCOPE — all OK) was supplied with the brief and is cited, not
  re-run. `check_traceability.py` is correctly deferred to the render stage. Entry conditions are
  complete; no "incomplete input" finding.

### policy_conflict_scan

The structured policy in force for category `auto` is the 14 base policies plus the 6 extended
policies of `auto.extended.yaml`.

**Base copy is verbatim.** A key-by-key JSON comparison of `blueprint/products/auto.yaml` against the
base section of `auto.extended.yaml` (`category`, `display_name`, `binding`, `lifecycle`, `accounts`,
`parameter_schema`, `variants`, `events`, `measures`, `policies`) returns an empty diff; the only
extra key is `extended_policies`. PASS.

**Overlapping subjects.** Each extended policy binds a distinct `(target_tool, computes)` pair and a
distinct `subject`, except that `auto_ext_call_payment_amount` and `auto_ext_payoff_settlement` both
carry `subject: [auto_payment]`. They are separated by `payment_type`: the first writes
`payment_type="scheduled"` and satisfies one installment, the second writes `payment_type="payoff"`
and closes the loan. No world admits both as the same act. PASS.

**Claimed scopes of the M tasks.** The `prerequisite` graph partitions the six extended policies into
exactly two connected components:

- component A: `auto_ext_due_day_realignment` → {`auto_ext_autopay_rate_restatement`,
  `auto_ext_call_payment_amount`}, `auto_ext_autopay_rate_restatement` → `auto_ext_call_payment_amount`,
  `auto_ext_call_payment_amount` → `auto_ext_fee_overcharge_correction`;
- component B: `auto_ext_payoff_settlement` → `auto_ext_gap_cancellation_refund`.

The two components share no policy, and their union is all six. With M=2 the scopes are therefore
pairwise disjoint and jointly complete, provided each task's root is the root of one component.
PASS on the charter side.

**Conflicts found.** Five, all of them conflicts between an extended policy and a base sentence that
its own `overwrite` does not name. They are set out in `override_declarations` below and repeated in
`findings`.

### rule_compute_equivalence

Checked per policy, sentence by sentence, in both directions.

PASS on substance for all six: every quantity, window, filter, tier, branch, cross-category read,
acting base, cap and rounding point named in a `compute` binding has a `compute_basis` entry, every
`factors[].ladder` tier is a branch of the `decides` binding, and every branch of each `decides`
binding is a tier the ladder names. No tier appears in one face and not the other.

Two defects in the quotation layer, neither of which changes a computed quantity:

1. **`compute_basis.recurring_deposits_3m` quotes a parameter that does not exist.** In four policies
   — `auto_ext_fee_overcharge_correction`, `auto_ext_call_payment_amount`,
   `auto_ext_autopay_rate_restatement`, `auto_ext_due_day_realignment` — the entry reads
   "at least **deposits_deep** recurring deposits have posted to that account in the last three
   months". No `params` block in the charter defines `deposits_deep`; the `rule`, the ladder and the
   `compute` all use `deposits_mid` (value 2). The `compute_basis` value is therefore not a verbatim
   quotation of any sentence of the rule. `auto_ext_gap_cancellation_refund` and
   `auto_ext_payoff_settlement` quote `deposits_mid` correctly, which shows the other four are a
   copy error rather than a convention. **Observation** — no computed quantity moves.

2. **A garbled tier in `auto_ext_call_payment_amount.rule`.** The middle tier of the charges window
   reads: "they are the charges assessed in the last three calendar months net of the corrections
   booked against them in those months where more than charge_entries_few but **more than
   charge_entries_few but** no more than charge_entries_some charges have been assessed on the loan
   in the last twelve months". The clause is duplicated. `factors[].ladder` and `compute` both state
   the intended `charge_entries_few < n <= charge_entries_some`, so the duplication is redundant
   rather than contradictory, and the ladder tier is consequently **not** verbatim in the rule.
   **Observation.**

### action_binding_and_uuids

| policy | target_tool | computes | owner |
| --- | --- | --- | --- |
| auto_ext_fee_overcharge_correction | correct_loan_fee_ab5fa380 | correction_amount | agent |
| auto_ext_call_payment_amount | post_installment_payment_1d25a699 | payment_amount | user |
| auto_ext_autopay_rate_restatement | set_loan_autopay_8313b066 | restated_apr | user |
| auto_ext_due_day_realignment | change_payment_due_day_9dcc583e | realigned_due_day | agent |
| auto_ext_gap_cancellation_refund | post_gap_refund_16f4decd | refund_amount | agent |
| auto_ext_payoff_settlement | post_loan_payoff_a84c6454 | settlement_amount | user |

Every `(target_tool, computes)` pair is claimed by exactly one policy. PASS.

**uuid8s:** `ab5fa380`, `1d25a699`, `8313b066`, `9dcc583e`, `16f4decd`, `a84c6454`. Six distinct
8-hex-digit values, no shared prefix or suffix, no arithmetic or lexical progression, no reuse. PASS.

**Docstrings and sequence.** No docstring names another task tool, and none states its action's
position relative to another problem's write. `correct_loan_fee_ab5fa380` and
`change_payment_due_day_9dcc583e` do carry the argument-sourcing phrase "read it from the loan record
returned by the auto loan lookup **before the call**", and `post_gap_refund_16f4decd` the same. The
phrase orders a *read* against the *same* call rather than ordering two business actions, so it does
not disclose the problem tree; recorded as an **observation** only.

**Tool bodies judge no prerequisite.** Read in full: `correct_loan_fee_ab5fa380`,
`post_installment_payment_1d25a699`, `set_loan_autopay_8313b066`, `change_payment_due_day_9dcc583e`,
`post_gap_refund_16f4decd`, `post_loan_payoff_a84c6454`. Every body is an unconditional
`ctx.create` / `ctx.find` / `ctx.update` sequence followed by a formatted return. The only branch in
any of them is `if rows:` / `if ctx.find(...)`, which guards against a missing holding row, never
against an unresolved prerequisite. None raises, none returns a refusal string, none emits a hint.
PASS.

### prerequisite_graph

Four declared edges; every policy has `prerequisite` filled in (`[]` on the two leaves).

| blocked policy | problem | kind | gate | form | resolved_by |
| --- | --- | --- | --- | --- | --- |
| auto_ext_call_payment_amount | auto_ext_fee_overcharge_correction | value_input | charges_to_clear | state | correct_loan_fee_ab5fa380 |
| auto_ext_autopay_rate_restatement | auto_ext_call_payment_amount | value_input | arrears_adjustment | state | post_installment_payment_1d25a699 |
| auto_ext_due_day_realignment | auto_ext_autopay_rate_restatement | state_gate | auto_loans.autopay_enrolled | state | set_loan_autopay_8313b066 |
| auto_ext_due_day_realignment | auto_ext_call_payment_amount | value_input | record_span | state | post_installment_payment_1d25a699 |

- Every `problem` names another extended policy id of this file; none names a base policy and none
  names itself. PASS.
- **Acyclic.** Topological order over the whole difficulty:
  `auto_ext_fee_overcharge_correction` < `auto_ext_call_payment_amount` <
  `auto_ext_autopay_rate_restatement` < `auto_ext_due_day_realignment`; and
  `auto_ext_gap_cancellation_refund` < `auto_ext_payoff_settlement`. No back edge exists, and the two
  components are disconnected, so no cross-task cycle is possible. PASS.
- Every `policy_source` is verbatim locatable in the blocked policy's own `rule` — verified by string
  containment against the `rule` text of each blocked policy. PASS.
- `form` is `state` on all four edges; no `fallback_reason` appears, which is correct, since
  `fallback_reason` is required exactly on action-form edges. PASS.
- `kind` matches `gate`: the three `value_input` edges name `charges_to_clear`, `arrears_adjustment`
  and `record_span`, each of which is a real binding name in the blocked policy's `compute`; the one
  `state_gate` names `auto_loans.autopay_enrolled`, a real field of the holding table. PASS.
- `resolved_by` genuinely makes `effect` hold in each case — demonstrated against the tool bodies:
  `correct_loan_fee_ab5fa380` writes an `auto_fee_waiver` row and lowers `fees_due`, which moves all
  three tiers of `charges_to_clear`; `post_installment_payment_1d25a699` writes an `auto_payment`
  row with `payment_type="scheduled"`, advances `next_payment_due_date` and zeroes `days_past_due`,
  which moves both `arrears_adjustment` and `record_span`; `set_loan_autopay_8313b066` sets
  `autopay_enrolled=False` and clears `autopay_source_account_id`. PASS.
- No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") appears in
  any `prerequisite` field. PASS.

### prerequisite_sentences

The four-point test, edge by edge.

1. `auto_ext_call_payment_amount` → `auto_ext_fee_overcharge_correction`
   > "The amount a payment taken during a call must cover is fixed only after every late charge standing on the loan carries the amount this charter fixes for it."

   Ordering connective "only after" ✓. What it waits on is a record-visible state of the fee rows
   ("every late charge standing on the loan carries the amount this charter fixes for it"), with no
   performer and no action ✓. No tool name, no policy id, no snake_case, no row id ✓. Scope matches
   `condition` ("No late charge standing unpaid on the loan shows an amount greater than the amount
   this charter fixes for that charge") — both are closed over the late charges standing on this loan ✓.
   **One write brings it about:** `correct_loan_fee_ab5fa380` is the only write in this difficulty
   that changes a fee amount; `post_installment_payment_1d25a699` and `post_loan_payoff_a84c6454`
   lower `fees_due` by paying, which settles a charge rather than changing what it "carries", and
   neither books an entry against a charge. Single reading ✓.
   **Derivation:** the sentence names "the amount this charter fixes for it", a term defined only in
   `auto_ext_fee_overcharge_correction.rule` ("The amount this charter fixes for a late charge is
   worked out from the scheduled installment in four steps…"); that rule's own opening sentence says
   the discrepancy "is put right by one correction entry booked against that charge"; its
   `target_tool` is `correct_loan_fee_ab5fa380`. Exactly one resolving action. ✓

2. `auto_ext_autopay_rate_restatement` → `auto_ext_call_payment_amount`
   > "The rate restated on the loan is fixed only after every installment already due stands satisfied on the loan's records."

   "only after" ✓; state form, no performer ✓; no tokens ✓; matches `condition` ("The loan's records
   show no installment whose due date has passed still unsatisfied") ✓.
   **One write:** `post_installment_payment_1d25a699` is the only write that credits an installment
   and advances `next_payment_due_date`. `post_loan_payoff_a84c6454` would also leave every
   installment satisfied, but it closes the loan to `paid_off`, after which
   `auto_evt_autopay`'s inherited "the loan must be active or delinquent" bars the restatement
   outright; so it is not a second candidate for this hop. Single reading ✓.

3. `auto_ext_due_day_realignment` → `auto_ext_autopay_rate_restatement`
   > "A due day is moved only once no standing instruction to draft the installment from a deposit account remains on the loan."

   "only once" ✓; state form — "no standing instruction to draft the installment from a deposit
   account remains on the loan" is `auto_loans.autopay_enrolled` / `autopay_source_account_id` in
   business words ✓; no tokens ✓; matches `condition` ✓.
   **One write:** `set_loan_autopay_8313b066` is the only write that touches `autopay_enrolled`. ✓

4. `auto_ext_due_day_realignment` → `auto_ext_call_payment_amount`
   > "The realigned day is settled only after the loan stands current with no installment past due on its records."

   "only after" ✓; state form ✓; no tokens ✓; matches `condition` ("The loan's records show every
   installment whose due date has passed satisfied and the past-due day count at zero") ✓.
   **One write:** `post_installment_payment_1d25a699` sets `days_past_due=0`. ✓

**No second wording, no tool name, no other problem's id** appears in any of the four blocked rules
beyond the single prerequisite sentence — checked by reading each `rule` end to end. **The
depended-on rule does not restate the sentence:** `auto_ext_fee_overcharge_correction.rule` does not
contain sentence 1, `auto_ext_call_payment_amount.rule` does not contain sentences 2 or 4,
`auto_ext_autopay_rate_restatement.rule` does not contain sentence 3. PASS.

**A cross-problem order stated in a rule that grounds no declared edge.** One is present, and it
runs against a declared edge rather than merely beside it — see finding **F-C1**.

### override_declarations

Sentence by sentence against each `base_policy_refs` entry. Findings only; each affected task's file
demonstrates the cost.

**`auto_ext_fee_overcharge_correction`** (refs `auto_evt_fee_waiver`, `auto_evt_late_charge`).
Two conflicts, both declared: the late-charge amount sentence and the "waived in full, never in part"
sentence are each named in `overwrite` with their replacement. Every other base sentence of both
policies is followed or untouched — the dedup sentence "Each installment carries at most one late
charge", the bank-error definition, the "A fee can be waived at most once" dedup and the courtesy
gates are inherited unaltered, and the extended rule adds no courtesy path. **No undeclared override.**

**`auto_ext_call_payment_amount`** (refs `auto_evt_payment_allocation`, `auto_evt_payoff_and_lien`),
`overwrite: []`. **Undeclared override — F-C3.** `auto_evt_payment_allocation` states: *"interest owed
at any moment is auto_msr_accrued_interest, computed on the principal balance from last_payment_date"*,
and `auto_msr_accrued_interest` is defined in `measures` as running "From last_payment_date
(exclusive) through the measurement date (inclusive)" at `interest_rate`, "rounded half-up to the
cent". The extended policy computes the same quantity — the interest a payment taken on the call must
cover — at a `payment_rate` that may be `apr_floor` or `interest_rate − autopay_discount_pct`, over a
span anchored at `next_payment_due_date`, at the most recent fee date, or at `last_payment_date`,
lengthened or shortened by one day, and rounded down or half-up to the **whole dollar**. Its own
`baseline` already deviates: "the clock runs from the date of the last payment credited to the loan
**and a further day is added to that span**". No `overwrite` entry names the base sentence.

**`auto_ext_autopay_rate_restatement`** (refs `auto_evt_autopay`, `auto_agg_relationship_discount`).
One conflict declared — `auto_evt_autopay`'s "Enrolling adds the autopay discount to the APR … from
the next installment due at least autopay_lead_days calendar days after enrollment; cancelling removes
it on the same schedule" is named, and replaced by a same-day restatement. **Undeclared override —
F-C4:** `auto_agg_relationship_discount` states *"When autopay is cancelled and
autopay_discount_removed_on_cancel is true, the APR rises by the autopay discount actually applied,
and re-enrolling later restores it"*. `autopay_discount_removed_on_cancel` is `true` for every
variant and `autopay_discount_pct` is 0.25 throughout. The extended policy raises the APR instead by
`restored_reduction` (0.10 / 0.15 / 0.25) **plus** an `arrears_adjustment` (0 to 0.50) **plus** a
`manual_payment_step` (0.00 / 0.05 / 0.10), less a `deposit_allowance`. The base sentence is listed in
`base_policy_refs` and governs the scored quantity; it is named in no `overwrite` entry. The
surviving base sentences that *are* inherited and respected are the cap/floor ("never below
apr_floor" → `MX(P('apr_floor'), …)`) and "the relationship discount is unaffected by autopay
changes".

**`auto_ext_due_day_realignment`** (refs `auto_due_date_change`), `overwrite: []`.
The base sentences on the shift ceiling ("at most due_date_change_max_shift_days calendar days"),
the once-per-window gate, the active/no-past-due gate, "The maturity date is not changed, and no fee
is charged" are all followed. **One base sentence is neither followed nor declared — F-C8
(observation):** *"A borrower may move the monthly due day to another day from 1 to 28."* The
extended `compute` ends `result: float(int(current_due_day + realignment_shift))` with no clamp to
28, and `realignment_shift` may reach `P('due_date_change_max_shift_days')` = 15, so
`current_due_day` of 14 or more yields a day above 28. The tool's own Args contract repeats the base
bound ("given as an integer 1-28"). Recorded as an observation because no task in this difficulty
lands in the region where the two disagree (see `0.md`); the defect is latent, not demonstrated.
The extended rule also introduces a gate the base does not have — "A due day is moved only once no
standing instruction to draft the installment from a deposit account remains on the loan" — but this
narrows eligibility where base is silent rather than contradicting a base sentence, and it is the
declared prerequisite sentence of edge 3, so it is not an override.

**`auto_ext_gap_cancellation_refund`** (refs `auto_evt_gap_refund`).
Two conflicts declared: the full-refund-window sentence, and "The refund is paid to a PCB checking
account of the borrower or by official check; it is never applied to the loan balance". **Two
undeclared overrides:**

- **F-C2.** `auto_evt_gap_refund` states: *"After that window the refund is gap_premium times the
  number of whole months remaining to the scheduled maturity_date divided by term_months, rounded
  half-up to the cent, minus gap_cancellation_fee, and no refund is made when that is zero or less."*
  The extended policy multiplies in a `refundable_share` of 90 / 95 / 100 percent that base does not
  have, re-anchors "months remaining" to the day of cancellation or to `next_payment_due_date`,
  admits a days-over-days and a ceil-to-quarter convention, and rounds down or half-up to the whole
  dollar. Even the extended `baseline` deviates, since `refundable_pct_standard` is 90. The sentence
  is named in no `overwrite` entry — the classic anonymous-intermediate override, hidden in
  `refundable_premium`.
- **F-C5.** `auto_evt_gap_refund` states: *"cancelling is the borrower's own decision recorded through
  an auto_requests row of request_type gap_cancellation that the borrower confirms."* The extended
  policy's `target_tool` `post_gap_refund_16f4decd` is `owner="agent"`, writes no `auto_requests`
  row, and needs no borrower confirmation; `binding.intake_tables` still lists `auto_requests`, and
  neither task seeds that table or offers any tool that writes it. The sentence is named in no
  `overwrite` entry.

**`auto_ext_payoff_settlement`** (refs `auto_evt_payment_allocation`, `auto_evt_payoff_and_lien`),
`overwrite: []`. **Two undeclared overrides:**

- **F-C6.** `auto_evt_payoff_and_lien` states: *"The payoff amount on a date is principal_balance plus
  auto_msr_accrued_interest through that date plus fees_due."* This is the same scored quantity the
  extended policy computes as `settlement_amount`. Extended substitutes a `settlement_rate` that may
  be `apr_floor` or `interest_rate − autopay_discount_pct`, a clock anchored at the most recent
  ledger entry or at `next_payment_due_date` rather than at `last_payment_date`, a `transit_allowance`
  of up to 3 extra days of interest, and whole-dollar rounding. Its `baseline` already adds
  `transit_days_standard` = 3 days that the base measure does not have. Named in no `overwrite`.
- **F-C1 (cross-problem order).** `auto_evt_payoff_and_lien` states *"A loan that is paid off with GAP
  coverage in force earns a GAP refund under auto_evt_gap_refund"*, and `auto_evt_gap_refund` states
  *"Paying the loan off early with GAP in force is treated as a cancellation on the payoff date."*
  Both put the payoff **first** and the GAP refund **after** it, on the payoff date. The extended
  prerequisite sentence *"The amount required to settle the loan in full is fixed only after the
  refund owed on the waiver coverage financed with the loan stands entered on its records"* puts the
  refund **first**. Two orders, two terminal states, and neither base sentence is named in any
  `overwrite`. The consequence is demonstrated against task 1's world in `1.md`.

`post_loan_payoff_a84c6454` is `owner="user"`, which is the reverse of the charter's own allocation
in `blueprint.yaml` — see F-C5 in `findings`.

### factor_ladders

Structure only. Per policy: factor count, effect labels, `decides` bindings, disjointness of binding
sets, tier count, multi-source tiers, rule coverage, label honesty, and the cross-difficulty
categories read.

| policy | factors | parameter | method | multi-source | cross_difficulty | bounds |
| --- | --- | --- | --- | --- | --- | --- |
| auto_ext_fee_overcharge_correction | 4 | 2 | 2 | 2 | 2 (card, checking) | OK |
| auto_ext_call_payment_amount | 6 | 2 | 4 | 3 | 4 (card ×3, checking) | OK |
| auto_ext_autopay_rate_restatement | 5 | 3 | 2 | 3 | 3 (card ×2, checking) | OK |
| auto_ext_due_day_realignment | 4 | 2 | 2 | 2 | 3 (card, checking ×2) | OK |
| auto_ext_gap_cancellation_refund | 5 | 2 | 3 | 2 | 3 (checking ×2, card) | OK |
| auto_ext_payoff_settlement | 4 | 2 | 2 | 3 | 3 (card ×2, checking) | OK |

Every policy is inside the 4–6 bound with at least 2 of each effect, at least 2 multi-source and at
least 2 cross-difficulty. Every ladder has exactly three pairwise-disjoint tiers with the
fall-through counted, and every tier's condition and its value or method is stated in the policy's
own `rule` in prose, with no tier living only in `compute`. No `decides` binding is `result`; within
each policy the factors' `bindings` sets are disjoint.

**Label honesty**, checked tier by tier:
- `parameter` factors all substitute a number into an unchanged formula — `correction_rate`,
  `charge_ceiling`, `payment_rate`, `charge_allowance`, `restored_reduction`, `manual_payment_step`,
  `deposit_allowance`, `base_shift`, `deposit_step`, `refundable_share`, `cancellation_fee`,
  `settlement_rate`, `transit_allowance`. `standing_deposit_allowance` is borderline in wording
  (its tiers read "deposit_allowance_pct_deep percent of the raised rate") but the operation is the
  same in every tier and only the percentage changes, so `parameter` is honest.
- `method` factors all change the operation, base, window or rounding point — `acting_base`
  (which addends enter the base), `charter_charge` / `interest_owed` / `rounded_rate` /
  `rounded_refund` (rounding mode and rounding point), `accrual_span` and `settlement_span` (which
  date anchors the clock), `accrual_days` (endpoint convention), `charges_to_clear` (which window of
  charges), `arrears_adjustment` (constant vs. a per-step count vs. a flat cap), `record_span`
  (which window of installments), `deposit_measure` (max vs. sum vs. latest), `unearned_share`
  (days-over-days vs. ceil-to-quarter vs. months-over-term). Every method tier names a rule the
  charter states.

**Multi-source tiers** are conjunctions over distinct records: card purchases (`card_transactions`)
with loan installments (`auto_transactions`); checking balance (`checking_accounts.ledger_balance`
against the tier's `waiver_min_daily_balance`) with recurring deposits (`checking_transactions`);
card reward points (`card_accounts.rewards_balance`) with card purchases (`card_transactions`).
The one marginal case is `realignment_base_shift`, whose two conditions are a sum and a count over
`card_transactions` in different windows — counted as multi-source, but noted.

**Cross-difficulty reads** are `card` (`card_transactions.amount`, `card_accounts.current_balance`,
`credit_limit`, `rewards_balance`) and `checking` (`checking_accounts.ledger_balance`,
`variant_name`, `opened_date`, `checking_transactions.amount`). Whether the rows those reads need
are actually seeded, and whether each factor bears weight, are facts about one world and live in the
task files under `factor_weight`.

### findings

Each names the tasks it bears on; the demonstration of cost lives in those tasks' files.

---

**F-C1 — SOURCE-POLICY RED — the charter states the payoff/GAP order in both directions.**

- *Symptom.* Two base sentences put the GAP refund after the payoff; the extended prerequisite
  sentence puts it before. Both orders are in force, and they produce different terminal states.
- *Root cause.* `auto_ext_payoff_settlement.overwrite` is `[]`, and
  `auto_ext_gap_cancellation_refund.overwrite` names only the full-refund-window sentence and the
  payment-destination sentence, so neither ordering sentence of the base is superseded.
- *Evidence.*
  - `auto.extended.yaml` → `policies` → `auto_evt_payoff_and_lien.rule`, last sentence:
    "A loan that is paid off with GAP coverage in force earns a GAP refund under auto_evt_gap_refund."
  - `auto.extended.yaml` → `policies` → `auto_evt_gap_refund.rule`:
    "Paying the loan off early with GAP in force is treated as a cancellation on the payoff date."
  - `auto.extended.yaml` → `extended_policies` → `auto_ext_payoff_settlement.prerequisite[0].policy_source`:
    "The amount required to settle the loan in full is fixed only after the refund owed on the waiver
    coverage financed with the loan stands entered on its records."
  - `auto_ext_payoff_settlement.overwrite: []`.
- *Demonstrated consequence.* Demonstrated on task 1's world in
  `env/regional_retail_bank/audits/policy_task/auto_loan_payment_servicing/1.md`, section
  `policy_self_consistency`.
- *Affected artifact.* `auto.extended.yaml`: `policies[auto_evt_payoff_and_lien].rule`,
  `policies[auto_evt_gap_refund].rule`, `extended_policies[auto_ext_payoff_settlement].overwrite`
  and `.prerequisite[0]`. Bears on **task 1**.

---

**F-C2 — SOURCE-POLICY RED — undeclared override of the base GAP pro-rata formula.**

- *Symptom.* Base and extended give different refunds in the same situation.
- *Root cause.* The extended policy inserts a `refundable_share` multiplier and re-specifies the
  months-remaining anchor and the rounding, while `overwrite` names only two other base sentences.
- *Evidence.* `auto_evt_gap_refund.rule`: "After that window the refund is gap_premium times the
  number of whole months remaining to the scheduled maturity_date divided by term_months, rounded
  half-up to the cent, minus gap_cancellation_fee, and no refund is made when that is zero or less."
  vs. `auto_ext_gap_cancellation_refund.compute` bindings `refundable_share`, `refundable_premium`,
  `months_remaining`, `unearned_share`, `rounded_refund`; and
  `auto_ext_gap_cancellation_refund.overwrite`, whose two entries name the full-refund-window
  sentence and the payment-destination sentence and nothing else.
- *Demonstrated consequence.* Demonstrated on task 1's world in `1.md`.
- *Affected artifact.* `extended_policies[auto_ext_gap_cancellation_refund].overwrite`. Bears on
  **task 1**.

---

**F-C3 — SOURCE-POLICY RED — undeclared override of the base accrued-interest measure by the
call-payment policy.**

- *Symptom.* Base and extended give different interest, and therefore a different amount to collect,
  in the same situation.
- *Root cause.* `auto_ext_call_payment_amount.overwrite` is `[]` while the policy re-specifies the
  rate, the anchor, the day count and the rounding point of the interest a payment must cover.
- *Evidence.* `auto_evt_payment_allocation.rule`: "interest owed at any moment is
  auto_msr_accrued_interest, computed on the principal balance from last_payment_date"; `measures` →
  `auto_msr_accrued_interest`: "From last_payment_date (exclusive) through the measurement date
  (inclusive) … rounded half-up to the cent." vs. `auto_ext_call_payment_amount.compute` bindings
  `payment_rate`, `accrual_span`, `accrual_days`, `interest_before_rounding`, `interest_owed`, and
  `auto_ext_call_payment_amount.overwrite: []`.
- *Demonstrated consequence.* Demonstrated on task 0's world in `0.md`.
- *Affected artifact.* `extended_policies[auto_ext_call_payment_amount].overwrite`. Bears on
  **task 0**.

---

**F-C4 — SOURCE-POLICY RED — undeclared override of the autopay-cancellation APR step.**

- *Symptom.* Base fixes the size of the APR change on an autopay change; extended produces a
  different one.
- *Root cause.* `auto_ext_autopay_rate_restatement.overwrite` names only `auto_evt_autopay`'s timing
  sentence, leaving `auto_agg_relationship_discount`'s magnitude sentence in force.
- *Evidence.* `auto_agg_relationship_discount.rule`: "When autopay is cancelled and
  autopay_discount_removed_on_cancel is true, the APR rises by the autopay discount actually applied,
  and re-enrolling later restores it"; `variants[*].parameters.autopay_discount_pct` = 0.25 and
  `autopay_discount_removed_on_cancel` = true throughout. vs.
  `auto_ext_autopay_rate_restatement.compute` binding
  `raised_rate: recorded_rate + restored_reduction + arrears_adjustment + manual_payment_step`, and
  `auto_ext_autopay_rate_restatement.overwrite`, whose single entry names
  `auto_evt_autopay`'s "Enrolling adds the autopay discount … on the same schedule" sentence.
- *Demonstrated consequence.* Demonstrated on task 0's world in `0.md`.
- *Affected artifact.* `extended_policies[auto_ext_autopay_rate_restatement].overwrite`. Bears on
  **task 0**.

---

**F-C5 — SOURCE-POLICY RED — the consent/owner boundary of GAP cancellation and payoff posting is
reversed without declaration.**

- *Symptom.* The charter says GAP cancellation is the borrower's own instruction and payoff posting
  is an agent service action; the tool module makes GAP cancellation agent-owned and payoff posting
  user-owned.
- *Root cause.* No `overwrite` entry names `auto_evt_gap_refund`'s consent sentence, and
  `blueprint.yaml`'s own allocation for this difficulty is not restated or superseded anywhere in
  the extended charter.
- *Evidence.*
  - `auto_evt_gap_refund.rule`: "cancelling is the borrower's own decision recorded through an
    auto_requests row of request_type gap_cancellation that the borrower confirms."
  - `blueprint.yaml` → `difficulties[auto_loan_payment_servicing].summary`: "Waivers, due date
    changes, **payoff posting** and lien releases are **agent service actions**, while a payment
    extension is the borrower's signed modification of terms and autopay enrollment and **GAP
    cancellation are the borrower's own instructions, all completed by the borrower**."
  - `task_tools.py`: `@tool(owner="agent", rw="write") def post_gap_refund_16f4decd(...)`;
    `@tool(owner="user", rw="write") def post_loan_payoff_a84c6454(...)`.
  - `post_gap_refund_16f4decd` writes only `auto_transactions` and `auto_loans`; no tool in
    `task_tools.py` or `share_tools.py` writes `auto_requests`, and neither task seeds that table,
    so the base sentence cannot be satisfied at all.
- *Demonstrated consequence.* Demonstrated on task 1's world in `1.md`.
- *Affected artifact.* `extended_policies[auto_ext_gap_cancellation_refund].overwrite`;
  `task_tools.py` owners of `post_gap_refund_16f4decd` and `post_loan_payoff_a84c6454`;
  `blueprint.yaml` difficulty summary. Bears on **task 1**.

---

**F-C6 — SOURCE-POLICY RED — undeclared override of the base payoff formula.**

- *Symptom.* Base and extended give different payoff amounts in the same situation.
- *Root cause.* `auto_ext_payoff_settlement.overwrite` is `[]` while the policy re-specifies the
  rate, clock anchor, day count and rounding of the interest component, and adds a transit allowance
  the base does not have.
- *Evidence.* `auto_evt_payoff_and_lien.rule`: "The payoff amount on a date is principal_balance plus
  auto_msr_accrued_interest through that date plus fees_due"; `formula.payoff_amount:
  principal_balance + auto_msr_accrued_interest + fees_due`. vs.
  `auto_ext_payoff_settlement.compute` bindings `settlement_rate`, `settlement_span`,
  `transit_allowance`, `settlement_days`, `interest_owed`, and
  `auto_ext_payoff_settlement.overwrite: []`. The extended `baseline.rule` itself states "the transit
  allowance is transit_days_standard days", i.e. 3 days of interest base does not charge.
- *Demonstrated consequence.* Demonstrated on task 1's world in `1.md`.
- *Affected artifact.* `extended_policies[auto_ext_payoff_settlement].overwrite`. Bears on **task 1**.

---

**F-C7 — observation — `compute_basis` quotes a parameter the charter never defines.**

In `auto_ext_fee_overcharge_correction`, `auto_ext_call_payment_amount`,
`auto_ext_autopay_rate_restatement` and `auto_ext_due_day_realignment`, the entry
`compute_basis.recurring_deposits_3m` reads "at least **deposits_deep** recurring deposits have
posted to that account in the last three months". No `params` block defines `deposits_deep`; the
`rule`, the ladder and the `compute` all use `deposits_mid`. The quotation is therefore not verbatim
from the rule it is supposed to quote. No computed quantity moves, so this is an observation.
Bears on **tasks 0 and 1** (task 0 through all four policies; task 1 through none, since its two
policies quote `deposits_mid` correctly).

---

**F-C8 — observation — a duplicated clause in a rule tier.**

`auto_ext_call_payment_amount.rule`: "… where more than charge_entries_few but **more than
charge_entries_few but** no more than charge_entries_some charges have been assessed on the loan in
the last twelve months". The clause is repeated. `factors[charges_cleared_window].ladder[1].when` and
the `compute` both state the intended band, so the semantics are unaffected, but the ladder tier is
consequently not verbatim in the rule. Bears on **task 0**.

---

**F-C9 — observation — the realigned due day is not clamped to the base's 1–28 range.**

`auto_due_date_change.rule`: "A borrower may move the monthly due day to another day from 1 to 28."
`auto_ext_due_day_realignment.compute` ends `result: float(int(current_due_day + realignment_shift))`
with no upper clamp, and `realignment_shift` may reach 15; `overwrite` is `[]`. The tool's own Args
contract repeats the base bound ("given as an integer 1-28"), so a computed day above 28 would be
both out of policy and out of contract. No task in this difficulty reaches that region, so no
consequence is demonstrable and this is an observation, not a red light. Bears on **task 0**.

---

**F-C10 — observation — argument-sourcing docstrings carry an ordering phrase.**

`correct_loan_fee_ab5fa380`, `change_payment_due_day_9dcc583e` and `post_gap_refund_16f4decd` each
say "read it from the loan record returned by the auto loan lookup **before the call**". The phrase
orders a read against the same call rather than ordering two business actions, and names no tool, so
it discloses nothing about the problem tree. Bears on **tasks 0 and 1**.

---

**F-C11 — observation — one marginal multi-source tier.**

`auto_ext_due_day_realignment.factors[realignment_base_shift]` draws both of its tier conditions from
`card_transactions` — a 12-month sum and a 3-month count. They are two conditions over different row
sets of one table rather than over two tables. Counted as multi-source here; noted because the
policy's multi-source count is exactly at the floor of 2 and would fall below it under a stricter
reading. Bears on **task 0**.

---

**F-C12 — the author's own note confirms F-C6 was a known deviation.**

Recorded post-reveal, and appended here rather than in `charter_global_frozen` because it rests on a
field that is masked before the freeze. `tasks/1.json` → `design_rationale`, BASE-INVARIANT CARD,
says of `auto_evt_payoff_and_lien`: "**The payoff figure it defines, principal plus accrued interest
plus fees due, is the shape the extended policy refines**; the allocation order, fees then interest
then principal, is inherited and is what the three portions passed to the tool follow." The author
states in terms that the extended policy alters the base payoff figure, and distinguishes that from
the allocation order, which is "inherited". A known deviation that is named nowhere in
`auto_ext_payoff_settlement.overwrite` (`[]`) is the definition of an undeclared override. This does
not add a new defect; it removes any reading of F-C6 as an oversight about what the base sentence
governs. Bears on **task 1**.

---

**F-C13 — observation — seeded late charges do not follow the base late-charge formula.**

Recorded post-reveal. In task 1, `auto_transactions` carries two `auto_fee` / `late_charge` rows of
**22.00** each (2026-07-31 for the installment due 2026-07-15, and 2026-08-31 for 2026-08-15) on a
New Vehicle Loan whose borrower resides in **NC**. `auto_evt_late_charge` fixes the charge at
`late_charge_pct_by_state` of `monthly_payment` capped at `late_charge_cap_by_state`: 4.0 % of 694.07
= 27.76, capped at 25.00, so the charter amount is **25.00**, not 22.00. (The grace timing is
correct: NC grace is 15 days, 2026-07-15 + 15 = 2026-07-30, and the charge is posted the first day
after grace.) No policy in task 1's scope recomputes a late charge, and
`auto_ext_payoff_settlement.rule` asks only for "the charges standing unpaid on the loan", which is
`fees_due` = 44.00 unambiguously, so no second answer follows and this is an observation rather than
a red light. It is recorded because the seeded history is not one the charter's own fee rule could
have produced. Bears on **task 1**.

## closing_checklist

**The difficulty does not close.** Step 4's checklist is written only when all four relationships
PASS on all M tasks; two of the four fail on both tasks. The state of each item is recorded below so
that a rework has the list in front of it.

- **Per-task files correspond one-to-one with the tasks.** Met. `0.md` and `1.md` sit alongside this
  file, each with a `source_derivation_frozen` written before any reveal and a `source_gt_comparison`
  written after. This is revision 1, so there are no older revisions to preserve; any re-audit must
  append under `## revision_2` and leave revision 1's text untouched.
- **Every comparison section carries a PASS.** **Not met.** `0.md` → `source_gt_comparison` →
  `verdict` carries SOURCE-POLICY RED, SOURCE-FACTOR RED and SOURCE-TASK RED; `1.md` carries
  SOURCE-POLICY RED and SOURCE-TASK RED.
- **Extended policies fully covered, scopes pairwise disjoint, tools and GT closed.** Met.
  `tasks/0.json.charter_scope` claims `auto_ext_fee_overcharge_correction`,
  `auto_ext_call_payment_amount`, `auto_ext_autopay_rate_restatement`, `auto_ext_due_day_realignment`
  with the four matching tools; `tasks/1.json.charter_scope` claims
  `auto_ext_gap_cancellation_refund` and `auto_ext_payoff_settlement` with the two remaining tools.
  The two sets are disjoint in policies and in tools, their union is all six extended policies and
  all six task tools, and each scope spans a whole connected component of the `prerequisite` graph —
  the root and all of its prerequisite problems.
- **Each task tool uses an independently generated, frozen uuid8.** Met — see
  `action_binding_and_uuids`.
- **Problem trees within bounds.** Met. Task 0: 3 prerequisite problems, 4 edges, 3 `value_input`
  (floor 2), one problem resolved by an `owner=user` tool
  (`post_installment_payment_1d25a699`, and `set_loan_autopay_8313b066` is a second), no cycle.
  Task 1: 1 prerequisite problem, 1 edge, 1 `value_input` (floor 1), the root itself resolved by an
  `owner=user` tool (`post_loan_payoff_a84c6454`), no cycle. The union of all four declared edges
  across the difficulty is a directed acyclic graph of two disconnected components, so no cycle is
  created by any cross-task reference.
- **Self-sufficient baselines and 4–6 weight-bearing factors per computation.** Met on the numbers,
  with one caveat. All six computations declare 4–6 factors with at least 2 `parameter`, 2 `method`,
  2 multi-source and 2 cross-difficulty, every ladder has three disjoint tiers stated in full in its
  own rule, every factor was shown to bear weight against an honest baseline on its task's world, and
  every baseline yields a definite number different from gold (15.85, 758.34, 8.84, 12.0, 295.82,
  20429.92). The caveat is `factor_ladders`' note on `realignment_base_shift`, whose two tier
  conditions both read `card_transactions`, leaving that policy's multi-source count at the floor
  under a stricter reading.
- **Instantiation-stage gates re-run on the final form.** **Not applicable at this revision.** No
  artifact was edited by this audit, so the supplied gate snapshot still describes the current form;
  the re-run belongs to whoever reworks the charter after these findings.

### verdict roll-up

| relationship | task 0 | task 1 |
| --- | --- | --- |
| policy self-consistency | SOURCE-POLICY RED (F-C3, F-C4) | SOURCE-POLICY RED (F-C1, F-C2, F-C5, F-C6) |
| the problem tree holds | PASS | PASS |
| factors bear weight | SOURCE-FACTOR RED (T0-F3, T0-F4) | PASS |
| policy ↔ task unique solution | SOURCE-TASK RED (T0-F5) | SOURCE-TASK RED (T1-F2) |

Six red-light findings are charter-global (F-C1 … F-C6) and are defects of the structured policy, not
of any solving agent; three are per-task consequences or proof defects (T0-F3, T0-F4, T0-F5, T1-F2).
This auditor's independent derivation reproduced **every** scored value, parameter, owner, order and
terminal field of both tasks, so none of these findings is a disagreement about what the answer is.
They are all about whether the artifacts prove that it is the only answer.

---

# revision_2

Revision 1 above is unaltered. This round is **not blind**: both tasks' GT was revealed in revision 1,
so what follows is a verification pass — each revision-1 RED checked for substantive closure, the
rework checked for new defects, and the closed items checked for regression.

## revision_2 / charter_global_frozen

- auditor: the same independent source-layer auditor; round 2.
- freeze time: 2026-09-16 (repo clock), after the rework.
- hashes, round 1 → round 2:
  - `auto.extended.yaml` `f1f7344d…48e2ab1a` → **`f59bf851c8455a119e35f589c7e894f7cbf18ff0f4ec8e63acdbd146c54868f2`** — changed
  - `task_tools.py` `f31b4354…6da85938`… → **`cd8967187c9e3f63a3552261d5e0e65250eb5f4917e3fc5597f67c7e6da85938`** — changed
  - `tasks/0.json` → `aef3874d4cdc3c68b043b8b20348e593870df3ca5466a99ad2f1ccb8495772aa`
  - `tasks/1.json` → `5be8282d10835b20a37d22eded63cf148d5c32ad08c14c3bfa06e5a41afec543`
- masked views: task 0 `757aedc9…461d6f` — **byte-identical to round 1**, so that task's world, clock
  and persona did not move; task 1 `deaa17c1b8028201d2559436235a03c9e464317bec6cd799723995f9cfef4475`
  — changed. I re-read task 1's view rather than carrying revision 1's reading forward, and
  established that its `initial_state` is materially unchanged (see `regression_check`); the byte
  difference is confined to `user_scenario`.
- Both shared inputs moved, so every charter-global section is re-derived in full below rather than
  carried forward by reference.
- entry condition: the post-rework gate snapshot (all seven blocks OK, base-gate and seed-row counts
  unchanged on both tasks) was supplied with the brief and is cited, not re-run.

### revision_2 / policy_conflict_scan

**Base copy still verbatim.** A key-by-key JSON comparison of `blueprint/products/auto.yaml` against
the base section of the reworked `auto.extended.yaml` returns an empty diff; `extended_policies`
remains the only extra key. **No regression.**

**What actually changed in the charter**, established by diffing each of the six extended policies
against the round-1 copies frozen in my own scratch directory:

| policy | fields changed | fields untouched |
| --- | --- | --- |
| auto_ext_fee_overcharge_correction | `compute_basis` | everything else |
| auto_ext_call_payment_amount | `overwrite`, one `rule` tier's wording, `compute_basis` | everything else |
| auto_ext_autopay_rate_restatement | `overwrite`, `compute_basis` | everything else |
| auto_ext_due_day_realignment | `compute_basis` | everything else |
| auto_ext_gap_cancellation_refund | `overwrite` | everything else |
| auto_ext_payoff_settlement | `base_policy_refs`, `overwrite` | everything else |

**No `compute`, `factors`, `baseline`, `params`, `inputs`, `cross_category`, `target_tool`,
`computes`, `subject` or `trigger` block changed in any of the six policies, and no `prerequisite`
block changed.** That is the structural reason no scored value could move, and it is confirmed
against GT in `regression_check` below.

**Overwrite integrity — the check that matters most this round.** All eleven `superseded_clause`
strings in the charter were tested for verbatim containment in the `rule` of the base policy each
one names:

- 11 of 11 locate verbatim. None relies on normalisation.
- Every `base_policy` named in an `overwrite` entry is also present in that policy's
  `base_policy_refs` — including the two newly added refs (`auto_evt_gap_refund` on
  `auto_ext_payoff_settlement`).
- **No base sentence is claimed by two extended policies.** `auto_evt_gap_refund` is now overwritten
  from two directions — three sentences by `auto_ext_gap_cancellation_refund` and one by
  `auto_ext_payoff_settlement` — but the four sentences are disjoint, so no base sentence has two
  competing replacements. This was the sharpest new-conflict risk the rework created and it is not
  realised.

Overwrite counts are now 2 / 1 / 2 / 0 / 3 / 3 across the six policies (`auto_ext_due_day_realignment`
is still `[]`, correctly — its only unfollowed base sentence is F-C9, deliberately not acted on).

**Task scopes** are unchanged and still pairwise disjoint and jointly complete over the six extended
policies and the six task tools.

### revision_2 / rule_compute_equivalence

Re-derived. Both round-1 quotation defects are gone and nothing regressed:

- `compute_basis.recurring_deposits_3m` now reads "at least **deposits_mid** recurring deposits…" in
  all four policies that carried `deposits_deep`; the string `deposits_deep` no longer occurs
  anywhere in the charter or in either task file. **F-C7 closed.**
- The duplicated clause in `auto_ext_call_payment_amount.rule` is gone: the middle tier now reads
  "where more than charge_entries_few but no more than charge_entries_some charges have been assessed
  on the loan in the last twelve months", which is byte-identical to
  `factors[charges_cleared_window].ladder[1].when`. **F-C8 closed.**

Substance is unchanged: every binding still has a `compute_basis` entry, every ladder tier is still a
branch of its `decides` binding and vice versa.

### revision_2 / action_binding_and_uuids

- `(target_tool, computes)` pairs unchanged; each still claimed by exactly one policy.
- **uuid8s unchanged and unreused**: `ab5fa380`, `1d25a699`, `8313b066`, `9dcc583e`, `16f4decd`,
  `a84c6454`. The rework swapped two owners without churning a uuid, which is the right outcome — a
  reissued uuid would have been a regression.
- **Owners changed on two tools** (the F-C5 rework): `post_gap_refund_16f4decd` `agent` → **`user`**,
  `post_loan_payoff_a84c6454` `user` → **`agent`**. Owners of the other four are unchanged.
- Tool bodies re-read in full. Still no conditional that judges a prerequisite; the only branch in any
  body remains the `if rows:` / `if ctx.find(...)` guard against a missing holding row. The new
  `auto_requests` write in `post_gap_refund_16f4decd` is unconditional. **No regression.**

### revision_2 / prerequisite_graph and prerequisite_sentences

Re-derived from the reworked charter. All five edges are unchanged in `problem`, `kind`, `gate`,
`form`, `condition`, `policy_source`, `resolved_by` and `effect`. Re-tested mechanically:

- all five `policy_source` strings still locate **verbatim** in the blocked policy's own `rule`;
- all five are `form: state`, and no `fallback_reason` is present on any of them, which is correct;
- no `policy_source` is restated in the depended-on policy's `rule`;
- the graph is still acyclic, still two disconnected components.

`resolved_by` still makes `effect` hold on every edge, re-checked against the reworked tool bodies —
including `post_gap_refund_16f4decd`, whose principal reduction is untouched by the owner change.

### revision_2 / override_declarations

Re-derived sentence by sentence. The five undeclared overrides of revision 1 are now declared, and
for each I established that the competing reading is actually retired rather than merely labelled —
see `revision_2 / findings`. No new undeclared override was introduced: the only base sentence still
handled differently without a naming entry is the 1–28 range sentence of `auto_due_date_change`
(F-C9), which the reworker states it deliberately did not act on and which revision 1 recorded as an
observation, not a red.

### revision_2 / factor_ladders

Unchanged — no `factors` or `baseline` block moved in any policy. The counts, effect labels, tier
structure and cross-difficulty categories recorded in revision 1 stand without re-derivation, and
that carry-forward is justified by the field-level diff above rather than by the file hash, which did
move for unrelated reasons.

## revision_2 / regression_check

**Task 0.** Masked view byte-identical to round 1; no `compute`, `factors`, `baseline` or `params`
block changed. Confirmed against GT: `correction_amount` **14.25**, `payment_amount` **621.30**,
`restated_apr` **8.15**, `realigned_due_day` **16.0**; baselines **15.85 / 758.34 / 8.84 / 12.0**; all
19 `factor_sensitivity` figures identical to round 1. Write order, owners (agent / user / user /
agent), every tool argument, both dates and both channels identical. `prerequisite_closure` unchanged.

**Task 1.** `initial_state` re-read and checked field by field against what revision 1 recorded —
loan (principal 20443.37, fees 44.00, rate 6.24, installment 694.07, last payment 2026-06-14, next
due 2026-07-15, funded 2024-02-09, maturity 2029-02-15, term 60, GAP true / 795.00, dpd 63,
delinquent, New Vehicle Loan, due day 15), Premier Checking 3167.25 opened 2021-05-20, Travel Rewards
Visa Signature 14000 / 3120 / 9800 — all unchanged, and the derived aggregates likewise
(`card_year_spend` 6950.00, `card_purchases_3m` 7, `scheduled_paid_12m` 9, `recurring_deposits_3m` 3,
`months_on_book` 31, `checking_months` 63, months remaining 31). `frozen_time` unchanged at
2026-09-16 14:05 EDT. I recomputed both values from the reworked charter: **390.00** and
**20308.37**, matching GT and matching revision 1. Baselines **295.82 / 20429.92** and all nine
`factor_sensitivity` figures identical to round 1. The tree, its single edge and its order are
unchanged.

**The reworker's claim that no scored value moved on either task is correct.** Nothing that was
closed has regressed.

## revision_2 / findings

Verdict per item id. "CLOSED" means I established the substance myself from the artifacts, not that
an entry exists and the gate parses it.

---

**F-C1 — CLOSED.** `auto_ext_payoff_settlement.overwrite` now carries two entries naming, verbatim,
both base sentences that put the refund after the payoff: `auto_evt_payoff_and_lien`'s "A loan that is
paid off with GAP coverage in force earns a GAP refund under auto_evt_gap_refund." and
`auto_evt_gap_refund`'s "Paying the loan off early with GAP in force is treated as a cancellation on
the payoff date." Both are replaced by the policy's own prerequisite sentence.
*Is the competing reading actually retired?* Yes. Those two sentences were the **only** places in the
charter putting the refund after the settlement — I re-read both base rules end to end to confirm
there is no third. With both superseded, the single surviving ordering rule is the prerequisite
sentence, which puts the refund first. The merged semantics are unique. I also checked that retiring
them leaves no hole: the *entitlement* to a refund survives in `auto_evt_gap_refund`'s "GAP waiver
coverage … may be cancelled by the borrower at any time while the loan is open", and the cancellation
*date* survives as the day the instruction is given, which `post_gap_refund_16f4decd` writes to
`gap_cancellation_date` and which the extended rule's "the day of the cancellation" reads.

---

**F-C2 — CLOSED.** `auto_ext_gap_cancellation_refund.overwrite` gains a third entry naming, verbatim,
`auto_evt_gap_refund`'s "After that window the refund is gap_premium times the number of whole months
remaining to the scheduled maturity_date divided by term_months, rounded half-up to the cent, minus
gap_cancellation_fee, and no refund is made when that is zero or less."
*Retired?* Yes. That sentence was the sole base statement of the pro-rata amount, so the 321.00
reading demonstrated in revision 1 no longer rests on anything in force, and 390.00 stands alone.

---

**F-C3 — CLOSED.** `auto_ext_call_payment_amount.overwrite` moves from `[]` to one entry naming,
verbatim, `auto_evt_payment_allocation`'s "interest owed at any moment is auto_msr_accrued_interest,
computed on the principal balance from last_payment_date".
*Retired?* Yes — that clause was the only base statement of the interest a payment must cover, so the
769.61 reading is retired and 621.30 stands alone. One observation on how it was worded: see R2-O2.

---

**F-C4 — CLOSED.** `auto_ext_autopay_rate_restatement.overwrite` gains an entry naming, verbatim,
`auto_agg_relationship_discount`'s "When autopay is cancelled and autopay_discount_removed_on_cancel
is true, the APR rises by the autopay discount actually applied, and re-enrolling later restores it".
*Retired?* Yes. I re-read `auto_evt_autopay` and `auto_agg_relationship_discount` in full: with the
timing sentence (declared in round 1) and this magnitude sentence both superseded, no base sentence
still fixes the size of the APR step on an autopay change. The 8.24 reading is retired and 8.15 stands
alone. The base sentences that survive and are still honoured — the `max_total_discount_pct` cap, the
`apr_floor` floor, and "the relationship discount is unaffected by autopay changes" — do not bear on
the magnitude.

---

**F-C5 — CLOSED, and closed the right way.** The reworker's account is accurate and I verified each
limb:
- **Owners follow the blueprint now.** `post_gap_refund_16f4decd` is `owner="user"` and
  `post_loan_payoff_a84c6454` is `owner="agent"`, which is exactly what
  `blueprint.yaml` → `difficulties[auto_loan_payment_servicing].summary` prescribes: "payoff posting
  … [is an] agent service action" and "GAP cancellation [is] the borrower's own instruction …
  completed by the borrower". The inversion revision 1 found is gone.
- **The base consent sentence is satisfied, not superseded.** `post_gap_refund_16f4decd` now opens by
  creating an `auto_requests` row with `request_type="gap_cancellation"` and
  `request_status="confirmed"`, and the tool is the borrower's own call. That is precisely what
  `auto_evt_gap_refund` asks: "cancelling is the borrower's own decision recorded through an
  auto_requests row of request_type gap_cancellation that the borrower confirms." I confirmed no
  `overwrite` entry anywhere names that sentence, so it is still in force — and it is now met.
- **The row is schema-valid.** All nine `auto_requests` columns of `db_schema.json` are written and no
  extra key is passed; `gap_cancellation` is a legal `request_type` value and `confirmed` a legal
  `request_status` value; `created_at` is `ctx.now()`, matching the declared format.
- **Permission boundary.** Task 1's wrappers were swapped to match:
  `unlock_user_discoverable_tool` + `call_user_discoverable_tool` for the GAP write at step 9,
  `unlock_agent_discoverable_tool` + `call_agent_discoverable_tool` for the payoff at step 11, with
  `owner` on each criterion matching. The objectives were rewritten to match. No write is attempted
  under an owner the tool does not declare.
- **The tree still holds.** Task 1 still has one prerequisite problem, one `value_input` edge (floor
  1) and no cycle, and it still carries a customer's own write — now at the prerequisite problem
  rather than at the root, which the requirement permits ("at least one problem of the tree").
  The persona hands it over passively and only on the agent's prompt: "When the representative tells
  him that cancelling it is his own instruction to give and hands it to him, he gives it himself for
  the figure he is told."
- **The persona's authorisation now matches the owners.** It gained "he is content for the
  representative to take that money and post it to the loan for him" and "leaves the posting to the
  representative" for the agent-owned payoff, and the hand-over line above for the user-owned GAP
  write. Both new owners are covered by an explicit authorisation, so the boundary is derivable.
- **No prerequisite leaked into the persona.** The GAP paragraph is still conditioned on the agent
  raising it first, and "if the representative never mentions the protection product he does not
  mention it either" is retained. The persona still closes where the last write lands, and still asks
  for nothing beyond the settlement.

---

**F-C6 — CLOSED.** `auto_ext_payoff_settlement.overwrite` moves from `[]` to three entries, the first
naming, verbatim, `auto_evt_payoff_and_lien`'s "The payoff amount on a date is principal_balance plus
auto_msr_accrued_interest through that date plus fees_due."
*Retired?* Yes at the sentence level — the 20419.63 reading no longer rests on a sentence in force,
and 20308.37 stands alone. One residue is recorded as R2-O1.

---

**F-C12 — CLOSED, as a consequence rather than by edit.** F-C12 was never an independent defect; it
recorded that the author's own note showed F-C6 was a *known* deviation. The note still stands in
task 1's `design_rationale` ("The payoff figure it defines … is the shape the extended policy
refines"), and it is now an accurate description of a **declared** refinement rather than evidence of
an undeclared one. Closed by F-C6's closure. See R2-O4 for a small staleness in the same paragraph.

---

**F-C7 — CLOSED (observation acted on).** See `revision_2 / rule_compute_equivalence`.

**F-C8 — CLOSED (observation acted on).** See `revision_2 / rule_compute_equivalence`.

**F-C13 — ANSWERED by argument, nothing changed, and the argument checks out — with one caveat.**
The reworker argues that `auto_evt_late_charge`'s amount sentence is superseded charter-wide by
`auto_ext_fee_overcharge_correction`'s declared override, and that under that method the charge the
charter fixes for task 1's loan is 22.00, exactly what the two seeded rows carry. I recomputed it:
`correction_rate` is `correction_pct_mid` 4.0 (card spend 6950.00 ≥ `card_spend_mid` 2500, 9
scheduled installments ≥ `installments_mid` 6, and 9 < `installments_deep` 10 supplies the shortfall);
`acting_base` is the installment alone, 694.07, since exactly one checking limb holds;
694.07 × 4.0 / 100 = 27.7628; `charge_ceiling` is `correction_ceiling_mid` 22.0 on two late charges in
twenty-four months; min(27.7628, 22.0) = 22.0; at 31 months on book the figure rounds half-up to the
whole dollar, giving **22.00**. The seeded history is one the charter does produce.
*Caveat.* The ceiling tier is reached by counting **both** seeded charges, i.e. by evaluating "the
amount this charter fixes" at today's date. Evaluated instead at the first charge's own posting date
of 2026-07-31, when no earlier late charge stood, the ceiling would be `correction_ceiling_standard`
15.4 and the charter amount 15.00, not 22.00. The policy defines the quantity at correction time, so
the reworker's reading is the right one; but the argument is not date-independent, and that is worth
recording. F-C13 was an observation in revision 1 and remains one.

---

**F-C9, F-C10, F-C11 — NOT ACTED ON, as claimed; verified unchanged and still observations.**
F-C9: `auto_ext_due_day_realignment.compute`'s `result: float(int(current_due_day +
realignment_shift))` is byte-identical and `overwrite` is still `[]`, so the 1–28 clamp is still
absent and still latent — no task reaches the region where it bites. F-C10: the "read it … before the
call" argument-sourcing phrase is still in the docstrings of `correct_loan_fee_ab5fa380`,
`change_payment_due_day_9dcc583e` and now `post_loan_payoff_a84c6454`. F-C11:
`auto_ext_due_day_realignment.factors[realignment_base_shift]` still draws both tier conditions from
`card_transactions`. None is a red light; declining them is a legitimate choice.

## revision_2 / new observations

**R2-O1 — the base `formula` blocks still restate two superseded sentences.**
`overwrite` operates on *sentences of a rule*. Two base policies carry a separate `formula` key whose
expressions are the machine form of sentences now superseded:
`auto_evt_payoff_and_lien.formula.payoff_amount` = `principal_balance + auto_msr_accrued_interest +
fees_due`, and `auto_evt_payment_allocation.formula.interest_due` = `auto_msr_accrued_interest`.
No `overwrite` entry reaches a `formula` key, and `auto_msr_accrued_interest` remains defined in
`measures`. At the source layer check 1 is satisfied, because the criterion is sentence-level and both
sentences are now named. But if the renderer emits those `formula` expressions into the published
documents, the competing readings F-C3 and F-C6 retired would return in machine form. **This is a
matter for the KB-document audit of this difficulty, not a reopening of F-C3 or F-C6**; recorded here
so that audit has it by path.

**R2-O2 — one `replaced_by` quotes the baseline clause rather than the governing sentence.**
`auto_ext_call_payment_amount.overwrite[0].replaced_by` is "the interest is worked out on the unpaid
principal **at the rate recorded on the loan** divided by the product's day count basis and multiplied
by the days the clock runs, and the interest is **rounded half-up to the cent**" — a clause of the
*standard-method* sentence, which pins the rate and the rounding at exactly the two defaults that the
`payment_interest_rate` and `payment_interest_rounding` factors vary. The parallel entries elsewhere
quote the governing sentence instead (`auto_ext_payoff_settlement`'s first entry quotes "The amount
required to settle an auto loan in full is …", which delegates to the settlement clock and rate). No
second answer follows at the source layer, because the extended rule states the ladders and they
govern within the policy. Recorded as an observation and flagged for the KB audit, since a reader who
meets the replacement text alone would take the baseline for the method.

**R2-O3 — a prerequisite sentence now appears three times in one policy.**
`auto_ext_payoff_settlement` uses its own prerequisite sentence as the `replaced_by` of **both**
ordering overwrites, so the sentence occurs once in `rule` and twice in `overwrite`. The check-6
requirement ("the rule carries nothing else about that dependency: no second wording") is met — it is
the same wording, not a second one, and the `rule` carries it exactly once. Recorded because, if the
renderer emits `replaced_by` prose, the blocked policy's documents would state the dependency three
times; that is a KB-audit question.

**R2-O4 — one paragraph of task 1's `design_rationale` was not updated with the rework.**
Its BASE-INVARIANT CARD says of `auto_evt_payoff_and_lien` that it "fixes no gate reaching the payment
itself … and enters as **policy_scope**", and describes its payoff figure as "the shape the extended
policy refines" — neither sentence mentions that two of that policy's sentences are now superseded by
this policy's own `overwrite`. The parallel GAP bullet was updated and does say "this policy's
declared overwrite". Nothing asserted is false — `auto_evt_payoff_and_lien` does still fix no
eligibility gate on the payment — so this is an observation about a stale proof note, not a defect of
the charter.

**R2-O5 — payments are user-owned in task 0 and agent-owned in task 1; this is licensed, not an
inconsistency.** After the rework, `post_installment_payment_1d25a699` is `owner="user"` while
`post_loan_payoff_a84c6454` is `owner="agent"`, though both post a payment to a loan. The blueprint
distinguishes them by name: "payoff posting" is listed among the agent service actions, and an
ordinary installment payment is named in neither list, so it falls to the borrower paying their own
loan. Recorded so that a later round does not mistake the asymmetry for a regression.

## revision_2 / closing_checklist

All four relationships now PASS on both tasks, so the difficulty **closes out**.

- **Per-task files correspond one-to-one with the tasks; old revisions traceable.** Met. `0.md` and
  `1.md` each carry revision 1 intact with its pre-reveal freeze, and a `revision_2` appended below
  it. No revision-1 text was edited.
- **Every comparison section carries a PASS.** Met at revision 2: `0.md` → `revision_2` and `1.md` →
  `revision_2` each record PASS on all four relationships.
- **Extended policies fully covered, scopes pairwise disjoint, tools and GT closed.** Met and
  unchanged: task 0 claims four policies and four tools, task 1 the remaining two and two; each scope
  still spans a whole connected component of the `prerequisite` graph.
- **Each task tool uses an independently generated, frozen uuid8.** Met — all six uuid8s survived the
  owner swap unchanged.
- **Problem trees within bounds.** Met. Task 0: 3 prerequisite problems, 4 edges, 3 `value_input`,
  two `owner=user` writes, no cycle. Task 1: 1 prerequisite problem, 1 edge, 1 `value_input`, one
  `owner=user` write (now at the prerequisite problem), no cycle. The union across the difficulty is
  still a DAG of two disconnected components.
- **Self-sufficient baselines and 4–6 weight-bearing factors per computation.** Met and unchanged; no
  `factors` or `baseline` block moved, and every baseline still yields a definite number different
  from gold (15.85, 758.34, 8.84, 12.0, 295.82, 20429.92). The F-C11 caveat on
  `realignment_base_shift` stands as an observation.
- **Instantiation-stage gates re-run on the final form.** Met — the coordinator re-ran the full block
  after the rework and all seven are green, with base-gate and seed-row counts unchanged on both
  tasks. `check_traceability.py` remains correctly deferred to the render stage.

### revision_2 / verdict roll-up

| relationship | task 0 | task 1 |
| --- | --- | --- |
| policy self-consistency | **PASS** (F-C3, F-C4 closed) | **PASS** (F-C1, F-C2, F-C5, F-C6 closed) |
| the problem tree holds | **PASS** (unchanged) | **PASS** (re-derived after the owner change) |
| factors bear weight | **PASS** (T0-F3, T0-F4 closed) | **PASS** (unchanged) |
| policy ↔ task unique solution | **PASS** (T0-F5 closed) | **PASS** (T1-F2 closed) |

Eleven of eleven claimed closures verified in substance. No new defect was found; five new
observations are recorded, of which three (R2-O1, R2-O2, R2-O3) are handed to the KB-document audit
of this difficulty rather than left against the source layer. No previously closed item regressed, and
no scored value, tree, order or terminal state moved on either task.
