# Policy-task audit — employee_meal_account_desk / charter-global

## charter_global_frozen

- auditor: independent source-layer auditor (not the instantiating agent)
- freeze time (charter-global section): 2026-09-22, written **before** any task's GT was revealed
- freeze hashes of the shared sources:
  - `sha256 906597034a8ba149054b2ab8723795870824d8e02c3ce5ab1340ea3f4dd2f9a4  tasks/employee_meal_account_desk/meal.extended.yaml`
  - `sha256 2fd04d28ab652a00769f609c21c81ad0ef25697c575c7f6af2c09f1f32aaa250  tasks/employee_meal_account_desk/task_tools.py`
- masked task views used for every blind derivation (constructed by the coordinator; only `frozen_time`, `user_scenario`, `initial_state` retained):
  - `0.masked.json` `sha256 82f9982c8729a980b98ce85ed11f1fd4f8a84c7d991d04b4757ad8c72b40e29e`
  - `1.masked.json` `sha256 a061341cfabc5f0a3dc5b81cb3b37f99060d3f7979930fd4c93f3f84e56c6401`
- fields permitted while this section was written: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`,
  `blueprint/share_tools.py`, `blueprint/products/*.yaml`, `tasks/employee_meal_account_desk/meal.extended.yaml`,
  `tasks/employee_meal_account_desk/task_tools.py`, `erlbench/`, and the two masked views.
- fields explicitly masked and not read while this section was written: every `evaluation_criteria`,
  `computations`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `charter_scope`,
  `required_documents`, `db_closure*` of `tasks/0.json` and `tasks/1.json`; no sibling difficulty's
  `tasks/` directory and no other scenario under `env/` was read at any point.
- entry conditions (Step 0): the coordinator supplied the gate snapshot with actual output lines for
  `check_extended.py`, `check_task_tools.py`, `replay_tasks.py --check`, `check_solvability.py`,
  `check_compute.py`, `check_grounding.py`, `check_cross_fire.py`, all green, plus the two masked views and
  their hashes. `check_traceability.py` is absent by design (the KB has not been rendered). **Entry
  conditions complete**; the gates were cited, not re-run, and a machine green light is only the
  qualification to enter this audit.

### policy_conflict_scan

Complete structured policy in force for category `meal`: the verbatim base section copied into
`meal.extended.yaml` (12 base policies, lines 373–1647 of the charter, identical in id, rule text,
eligibility contracts and `params.per_tier` to `blueprint/products/meal.yaml`) plus 6 extended policies.

| extended policy | trigger | subject | computes | target tool | base refs |
| --- | --- | --- | --- | --- | --- |
| `meal_ext_period_recovery_amount` | state_due | meal_payroll_deduction_posted | recovered_amount_usd | `post_payroll_recovery_c9e76aa9` | meal_payroll_recovery_terms |
| `meal_ext_reinstatement_paydown` | on_request | meal_account_load_posted | paydown_amount_usd | `load_arrears_paydown_ff1c695b` (owner=user) | meal_load_and_refund_terms, meal_restriction_terms |
| `meal_ext_restriction_lift_balance` | on_request | meal_account_reinstated | arrears_carried_usd | `lift_meal_account_restriction_a306574a` | meal_restriction_terms, meal_payroll_recovery_terms |
| `meal_ext_daily_allowance_grant` | state_due | meal_subsidy_granted | granted_amount_usd | `grant_daily_allowance_lot_ed948b99` | meal_subsidy_grant_rules |
| `meal_ext_ticket_allowance_application` | state_due | meal_subsidy_applied | applied_amount_usd | `apply_allowance_to_ticket_3fbfdeca` | meal_subsidy_application_rules, meal_combination_employer_program_interaction |
| `meal_ext_payroll_charge_consent` | on_request | meal_charge_accrued | accrued_amount_usd | `confirm_payroll_charge_accrual_6d54e4b8` (owner=user) | meal_payroll_recovery_terms |

Subjects are pairwise disjoint; no two extended policies compute the same quantity or write the same
event family. The `prerequisite` graph splits the six into exactly two connected components, which are
the two tasks' problem trees:

- tree A — root `meal_ext_restriction_lift_balance`; prerequisite problems `meal_ext_reinstatement_paydown`
  and `meal_ext_period_recovery_amount`; internal edge paydown → period_recovery.
- tree B — root `meal_ext_payroll_charge_consent`; prerequisite problem `meal_ext_ticket_allowance_application`;
  its prerequisite `meal_ext_daily_allowance_grant`.

The two component vertex sets are disjoint and jointly exhaust the six extended policies, so the M=2
claimed scopes are mutually exclusive and jointly complete **at the policy level** (verified against the
charter alone; the tasks' own `charter_scope` was masked and is compared in each task file).

Overlapping subjects, eligibility, time anchors and terminal states across base and extended were checked
policy by policy. Three conflicts survive and are written up under `findings` below (CG-1, CG-3, CG-4);
cross-category read boundaries are declared consistently (each extended policy's `cross_category` block
names exactly the categories its `compute` reaches through `CFIELD`/`CPARAM`: cafe for
`meal_ext_period_recovery_amount` and `meal_ext_daily_allowance_grant`, cafe + market for
`meal_ext_ticket_allowance_application`, none elsewhere).

### rule_compute_equivalence

Check 2 was run binding by binding over all six extended policies (105 compute bindings in total). Every
quantity, window (`within_months=1/2/3/12`), tier, branch, cross-category read, acting base, cap/floor
(`MX(0.0, …)`, `MN(…)`), rounding mode and rounding point carries a verbatim `compute_basis` quotation
that is a sentence or clause of that policy's own `rule`, and the sweep back from each rule sentence finds
a binding, **with one exception**, recorded as **CG-1** below: `meal_ext_payroll_charge_consent`'s
`balance_refunds_1m` and `balance_refunds_3m` filter `payment_channel='badge_tap'`, a restriction that
appears in neither the rule nor the quoted basis.

Every declared factor's ladder was matched both ways against rule and compute: for each of the 30 factors,
each `ladder[].when` is a clause of the `rule` and a branch of the `decides` binding, and each branch of
that binding is a stated tier. No tier lives only in `compute`; no rule sentence promises a tier the
compute does not implement.

Rounding: every policy rounds once at the end (`RND(…, 2)`) and names any intermediate rounding explicitly
("rounded to two decimal places at that step" for `gross_paydown_usd`, `ticket_share_usd`,
`base_grant_usd`'s availability step, `applications_netted_usd`, `employer_met_usd`, `kiosk_trim_usd`,
`refund_offset_usd`'s twelve-month branch, `applied_from_value_usd`'s halved branch). Each such sentence is
present in the corresponding `rule`.

### action_binding_and_uuids

Each `(target_tool, computes)` pair is claimed by exactly one policy (table above); no pair repeats. Each
policy's subject, base refs, target tool, docstring and terminal state admit one business reading, and no
tool docstring adds a confirmation, review or wait outside its policy.

uuid8 tails, read individually from `task_tools.py`:

| tool | uuid8 |
| --- | --- |
| `post_payroll_recovery_` | `c9e76aa9` |
| `load_arrears_paydown_` | `ff1c695b` |
| `lift_meal_account_restriction_` | `a306574a` |
| `grant_daily_allowance_lot_` | `ed948b99` |
| `apply_allowance_to_ticket_` | `3fbfdeca` |
| `confirm_payroll_charge_accrual_` | `6d54e4b8` |

All six are distinct, share no prefix of length ≥ 2, are not sequential, and show no sign of batch
derivation from a common stem. PASS.

Docstring ordering language: every one of the six carries a phrase with the word *before* — four agent
tools say "read it from the meal account lookup **before** this call", the two user tools say "as the
dining services desk reads it out to you **before** you make the payment / **before** you give your
consent". These locate an argument's provenance against a *read*; none names another task tool, none
states this write's position among the other writes, and none grounds any prerequisite edge. Recorded as
observation **CG-8**, not as a red light: no second reading of any task's write order follows from them.

### prerequisite_graph

Check 7 over the whole graph.

| blocked policy | problem | kind | gate | form | resolved_by |
| --- | --- | --- | --- | --- | --- |
| `meal_ext_reinstatement_paydown` | `meal_ext_period_recovery_amount` | value_input | `measured_balance_usd` | state | `post_payroll_recovery_c9e76aa9` |
| `meal_ext_restriction_lift_balance` | `meal_ext_period_recovery_amount` | value_input | `balance_standing_usd` | state | `post_payroll_recovery_c9e76aa9` |
| `meal_ext_restriction_lift_balance` | `meal_ext_reinstatement_paydown` | value_input | `applied_from_value_usd` | state | `load_arrears_paydown_ff1c695b` |
| `meal_ext_ticket_allowance_application` | `meal_ext_daily_allowance_grant` | value_input | `lots_in_window_usd` | state | `grant_daily_allowance_lot_ed948b99` |
| `meal_ext_payroll_charge_consent` | `meal_ext_ticket_allowance_application` | value_input | `allowance_credited_usd` | state | `apply_allowance_to_ticket_3fbfdeca` |

- `prerequisite` is filled in on every extended policy (`[]` on `meal_ext_period_recovery_amount` and
  `meal_ext_daily_allowance_grant`, the two roots of the two chains). PASS.
- Every `problem` names another extended policy id in this file; none names a base policy and none names
  itself. PASS.
- The graph is acyclic: the two components are the DAGs
  `lift → {paydown, recovery}`, `paydown → recovery`, and `consent → ticket → grant`. PASS.
- Every `policy_source` is verbatim locatable in the **blocked** policy's own `rule` (quoted in
  `prerequisite_sentences` below). PASS.
- `form` is `state` on all five edges; no edge is action-form, so no `fallback_reason` is required and none
  is present. PASS.
- Every `gate` names a binding that genuinely exists in the blocked policy's `compute`:
  `measured_balance_usd`, `balance_standing_usd`, `applied_from_value_usd`, `lots_in_window_usd`,
  `allowance_credited_usd` — each is a binding key of its policy's compute list. PASS; `kind: value_input`
  matches in every case (none is a status flip).
- `resolved_by` is the depended-on policy's own `target_tool` in all five cases. PASS.
- No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") appears in any
  `prerequisite` block. PASS.
- `condition` strength: **fails on three of the five edges** — see **CG-3**.

### prerequisite_sentences

Check 6, edge by edge. All five sentences are quoted here verbatim from the blocked policy's `rule`.

1. `meal_ext_reinstatement_paydown` → `meal_ext_period_recovery_amount`
   > "The paydown the employee is asked for is not worked out before the charges awaiting recovery on the account stand net of the recovery entry owed for every closed payroll period."
   Ordering connective "not … before" ✓; the thing waited on is a record-visible state ("the charges
   awaiting recovery … stand net of the recovery entry") in table words, with no performer and no tool ✓;
   no tool name, policy id, snake_case token or row id ✓. Strength: **see CG-3**.
2. `meal_ext_restriction_lift_balance` → `meal_ext_period_recovery_amount`
   > "The charges an account carries forward at reinstatement are fixed only after the charges awaiting recovery stand net of the recovery entry due for each closed payroll period."
   Connective "only after" ✓; state form ✓; no tool/id ✓. Strength: **see CG-3**.
3. `meal_ext_restriction_lift_balance` → `meal_ext_reinstatement_paydown`
   > "The charges carried forward are worked out only once the stored value standing on the account has been raised by the paydown the plan calls for."
   Connective "only once" ✓; state form ("the stored value standing … has been raised by the paydown") ✓;
   no tool/id ✓; strength matches the `condition` ("a load entry for the paydown stands on the account's
   ledger and the stored value standing has risen by it") ✓. Derivation to a single resolving action:
   `meal_ext_reinstatement_paydown`'s own rule is the only rule in this charter that says what "the paydown
   the plan calls for" is and ends "The employee makes this payment in person from a card they hold";
   `load_arrears_paydown_ff1c695b` is the only write that raises `meal_balance_usd` by a paid-in amount.
   One reading. PASS.
4. `meal_ext_ticket_allowance_application` → `meal_ext_daily_allowance_grant`
   > "The allowance applied to a till transaction is not settled before the allowance lots the account is owed for the grant period stand on its ledger."
   Connective "not … before" ✓; state form ✓; no tool/id ✓. Strength: **see CG-3**.
5. `meal_ext_payroll_charge_consent` → `meal_ext_ticket_allowance_application`
   > "The charge carried to payroll is fixed only after each eligible till transaction of the period carries the allowance application it is owed."
   Connective "only after" ✓; state form ✓; no tool/id ✓. Strength: **see CG-3**.

State-form priority is honoured on all five (no action-form edge exists, so no `fallback_reason` needs
testing). No rule carries a second wording of its own dependency, names another problem's tool, or states a
route or an aggregated chain; no depended-on rule restates the blocked rule's sentence. No base rule
sentence states a cross-problem order that grounds any of these edges.

**One write per waited-on state** — one caveat, recorded as observation **CG-9**:
`lift_meal_account_restriction_a306574a` creates a `meal_transactions` row with
`event_type="meal_payroll_deduction_posted"`, i.e. the same event family from which "the recovery entry"
of sentences 1 and 2 is read. It is separated only by `transaction_code="balance_adjustment"` and by its
docstring calling it "a settlement entry … for the movement that restatement makes". A reader who
identifies the waited-on state by event family alone could see two candidate writes; a reader who uses
`transaction_code` (the schema's own words: "the transaction subtype … what separates two rows that
differ only in why the money moved") sees one. Not a red light, because the tie is broken inside the
records; recorded so a re-audit can re-check it.

### override_declarations

Check 1's finding half, sentence by sentence against each `base_policy_refs` entry.

`meal_ext_period_recovery_amount` vs `meal_payroll_recovery_terms` (7 sentences):
declares the deduction-ceiling sentence ("no more than the deduction ceiling printed against the same plan
is recovered in one period" → held to the recovery ceiling worked out above). Sentences on charge/period
matching, payroll-tender availability and the arrears ceiling, recoverable state, leaver's final pay,
error reversal and leave are followed or untouched — **except** the remittance-timing sentence, which is
**CG-4**.

`meal_ext_reinstatement_paydown` vs `meal_restriction_terms` and `meal_load_and_refund_terms`:
declares the reinstatement-share sentence. The load sentences (min/max single load, balance ceiling) are
followed — the compute's final step is `MX(…, P('min_load_usd'))` then `MN(…, P('max_load_usd'))`. No
undeclared conflict found.

`meal_ext_restriction_lift_balance` vs `meal_restriction_terms`, `meal_payroll_recovery_terms`:
declares `meal_payroll_recovery_terms`' accrual sentence. **CG-5** records an undeclared conflict with the
base charter's own `meal_overdraft_fee_posted` event binding, and **CG-6** records that two of this
policy's tier outcomes are not treatments any business in this line publishes.

`meal_ext_daily_allowance_grant` vs `meal_subsidy_grant_rules`: declares the per-period grant-ceiling
sentence. Lot-by-lot recording, lapse/rollover, grantable state, proration, taxable ceiling and refund
restoration are followed. No undeclared conflict found.

`meal_ext_ticket_allowance_application` vs `meal_subsidy_application_rules`,
`meal_combination_employer_program_interaction`: declares the "allowance applied is the plan's share …
held to the per transaction ceiling … and to what is left in the employee's lots for the day" sentence,
which legitimately removes the day-scoping of the lots. Two residues are recorded as observations
**CG-10** (base: "producing one application row per lot touched" vs a single-row tool) and **CG-11**
(base has the employer's subsidy funding *meet the drawdown behind* the allowance, while
`employer_counter_topup` *adds* the cafe's per-employee daily cap into the employee's pot).

`meal_ext_payroll_charge_consent` vs `meal_payroll_recovery_terms`: declares the accrual sentence. The
arrears-ceiling, recoverable-state and leave sentences are inherited and unbroken.

No anonymous intermediate factor, 0/1 multiplier or dropped branch was found: every extended selector's
fall-through reproduces the base/baseline value, and no existence condition is multiplied onto a settled
base.

### factor_ladders

30 factors over 6 policies. Structure per policy:

| policy | factors | parameter | method | multi-source factors (every non-fall-through tier a conjunction over ≥2 distinct records) | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| `meal_ext_period_recovery_amount` | 4 | 3 | 1 | 3 of 4 (`recovery_ceiling_band`, `recoverable_window_basis`, `short_tender_deferral`) | `employer_programme_share` → cafe |
| `meal_ext_reinstatement_paydown` | 5 | 4 | 1 | 5 of 5 | — |
| `meal_ext_restriction_lift_balance` | 4 | 3 | 1 | 3 of 4 (`stored_tender_meal_restoration` reads two row sets of one table) | — |
| `meal_ext_daily_allowance_grant` | 5 | 4 | 1 | 4 of 5 (`grant_period_ceiling_band` reads two row sets of one table) | `employer_funded_base` → cafe |
| `meal_ext_ticket_allowance_application` | 6 | 5 | 1 | 4 of 6 (`lot_window_basis` and `employer_counter_topup` read one record each) | `employer_counter_topup` → cafe, `second_counter_trim` → market |
| `meal_ext_payroll_charge_consent` | 6 | 5 | 1 | 5 of 6 (`prior_accrual_netting` reads two row sets of one table) | — |

Records counted as distinct: the `meal_accounts` holding row, the `meal_transactions` ledger, the
`meal_closure_requests` request log, the meal plan's own parameter column, and each other category's
holding row. `employer_programme_share`, `employer_counter_topup` and `lot_window_basis` take both halves
of their compound conditions from a single record (the cafe contract row, and the meal plan's parameter
column respectively) and are therefore **not** counted as multi-source.

Counts: every policy carries 4–6 factors, at least 2 `parameter` and at least 1 `method`. Per tree,
tree A's computations carry one cross-difficulty factor (cafe, in `meal_ext_period_recovery_amount`) and
tree B's carry three (cafe ×2, market ×1). Each tree therefore meets the ≥1 multi-source and ≥1
cross-difficulty floors **on the charter's face** (whether the cross-difficulty rows are actually seeded is
a per-task fact and lives in each task's `factor_weight`).

Bindings: within each policy, the `bindings` sets of the factors are pairwise disjoint (checked set by
set), and every `decides` names an intermediate input, never `result`.

Ladders: each of the 30 has exactly 3 tiers, the fall-through counted, stated in full in the `rule`
(condition **and** value/method) and implemented in the `decides` branch. Tier conditions are pairwise
disjoint as stated in all 30.

Label honesty: the 6 `method` factors (`recoverable_window_basis`, `measured_balance_basis`,
`value_application_basis`, `standing_allowance_basis`, `lot_window_basis`, `charge_window_basis`) each
change which rows are aggregated or which expression computes the quantity, not merely a number; the 24
`parameter` factors each substitute a figure into an unchanged expression. No `method` tier names a
computation rule the charter does not state. PASS.

Distinct outcomes: **fails on three ladders** — `guest_meal_pot_exclusion`, `guest_surcharge_addition`
and `prior_accrual_netting` — see **CG-2**.

Conditions and outcomes the business actually holds: **fails on two tiers of
`meal_ext_restriction_lift_balance`** — see **CG-6** — and one fall-through tier of that policy is
unreachable at its own write — see **CG-7**.

### findings

---

#### CG-1 — `SOURCE-POLICY RED` — compute filters refund rows on a channel the rule never states

- **symptom** `meal_ext_payroll_charge_consent` computes the refund credit from
  `badge_tap` refunds only, while its rule and its own `compute_basis` quote say only "a refund has been
  returned on the account".
- **root cause** an extra equality filter in the compute expression with no counterpart in the rule:
  compute invents a basis of its own (check 2).
- **evidence**
  - compute: `balance_refunds_1m: SUM('meal_transactions','amount_usd', within_months=1, date_field='posted_date', transaction_code='refund', payment_channel='badge_tap')` (likewise `balance_refunds_3m`).
  - `compute_basis.balance_refunds_1m`: "Where the plan returns refunds to stored value and a refund has been returned on the account in the last calendar month, the refund credited is the whole of those refunds" — the plan's `refund_method` is the only channel-like test in the sentence; nothing restricts the **row's** `payment_channel`.
  - contrast within the same charter: `meal_ext_restriction_lift_balance.payroll_refunds_3m` reads `transaction_code='refund'` with **no** channel filter under a rule of exactly the same shape ("the plan returns refunds through payroll and a refund has been returned on the account…"). The same concept is filtered in one policy and not the other.
- **demonstrated consequence** two defensible readings with different numbers — demonstrated against task 1's world in `1.md` (`64.50` as compute reads it, `60.30` as the rule reads it).
- **affected artifact** `tasks/employee_meal_account_desk/meal.extended.yaml`, `meal_ext_payroll_charge_consent.compute` bindings `balance_refunds_1m`, `balance_refunds_3m`, and the `stored_value_refund_credit` factor that rests on them. Bears on: **task 1**.

---

#### CG-2 — `SOURCE-FACTOR RED` — three ladders state one rule as two tiers

- **symptom** in three ladders, tier 2 is tier 1's own formula restricted to a smaller count; no evidence in
  any world can make the two tiers disagree, so the ladder carries two distinct rules, not three.
- **root cause** the tier split is on a count, while the value is already a function of that count
  (or of the very quantity the second tier subtracts).
- **evidence**
  1. `meal_ext_ticket_allowance_application.guest_meal_pot_exclusion` —
     tier 1 "…two or more guest meals… → the guest surcharge printed against the plan **counted once for each of them**";
     tier 2 "…exactly one guest meal… → that printed guest surcharge **once**".
     compute: `RND(P('guest_meal_surcharge_usd') * guest_count_1m, 2) if (… guest_count_1m >= 2) else (P('guest_meal_surcharge_usd') if (… guest_count_1m == 1) else 0.0)` — the single expression `surcharge × guest_count_1m` reproduces both branches exactly.
  2. `meal_ext_payroll_charge_consent.guest_surcharge_addition` — identical shape, on `guest_count_3m`.
  3. `meal_ext_payroll_charge_consent.prior_accrual_netting` —
     tier 1 "…and **no recovery** has been remitted in that month → the whole of those charges";
     tier 2 "…and a recovery has been remitted in that month → those charges **less that recovery**".
     compute: `charges_1m if (charges_1m_count >= 2 and recoveries_1m <= 0) else (MX(0.0, charges_1m - recoveries_1m) if (charges_1m_count >= 2 and recoveries_1m > 0) else 0.0)` — the single expression `MX(0.0, charges_1m - recoveries_1m)` reproduces tier 1 too, because `recoveries_1m` is 0 on tier 1's domain by construction.
  Compare the same author's honest use of the pattern elsewhere: `meal_ext_reinstatement_paydown.guest_meal_surcharge_due` tier 2 subtracts `single_guest_relief_usd`, and `meal_ext_ticket_allowance_application.unfunded_period_exclusion` tier 2 subtracts `single_dinner_relief_usd` — those two genuinely differ from their tier 1.
- **demonstrated consequence** each of the three ladders has fewer than three tiers that a world can tell
  apart: an agent who applies tier 1's stated rule to every count, never reading tier 2, scores the same
  number on every world. The three-tier floor is met only on paper.
- **affected artifact** `meal.extended.yaml`, factors `guest_meal_pot_exclusion`,
  `guest_surcharge_addition`, `prior_accrual_netting`. Bears on: **task 1** (all three sit in tree B).

---

#### CG-3 — `SOURCE-POLICY RED` — four prerequisite sentences are quantified over a set the single resolving write cannot close

- **symptom** four of the five edges wait on a state stated over **every / each** member of a set, while the
  depended-on policy's own rule performs exactly **one** write for **one** member of that set. After the
  resolving action the declared `condition` is still false.
- **root cause** the prerequisite sentence and `condition` are written at a strength broader than the
  depended-on rule's singular result.
- **evidence**
  - edges 1 and 2 wait on "the recovery entry owed for **every** closed payroll period" / "the recovery entry
    due for **each** closed payroll period", `condition`: "**every** closed payroll period on the account
    carries its own recovery entry on the ledger, so the charges awaiting recovery stand net of it".
  - the depended-on rule, `meal_ext_period_recovery_amount`: "The payroll period a remittance is made for is
    **the** period carried by **the most recent** charge accrued on the account." — one remittance, one
    period, fixed singular.
  - the tool books one row: `post_payroll_recovery_c9e76aa9(… pay_period)` creates a single
    `transaction_code="payroll_deduction"` row (task_tools.py, lines of `ctx.create` in that function).
  - edge 4 waits on "the allowance lots the account is owed for the grant period stand on its ledger"
    (plural "lots"), while `grant_daily_allowance_lot_ed948b99` mints exactly one lot reference per call.
  - edge 5 waits on "**each** eligible till transaction of the period carries the allowance application it
    is owed", `condition`: "**every** eligible till transaction of the period carries an allowance
    application entry", while `meal_ext_ticket_allowance_application`'s rule fixes a single object — "The
    ticket is **the largest** meal rung against payroll on the account" — and its tool takes one
    `original_pos_reference`.
- **demonstrated consequence** two readings of the resolving action, with different downstream numbers.
  Demonstrated on task 0 in `0.md` (five closed pay periods carry charges, only two carry a recovery entry;
  the single prescribed write closes one of the remaining three, leaving the declared condition false) and
  on task 1 in `1.md` (six payroll meals stand in the period, none of them carries an allowance application;
  the single prescribed write covers one).
- **affected artifact** `meal.extended.yaml`, `prerequisite` blocks of `meal_ext_reinstatement_paydown`,
  `meal_ext_restriction_lift_balance` (edge on `meal_ext_period_recovery_amount`),
  `meal_ext_ticket_allowance_application`, `meal_ext_payroll_charge_consent`, and the corresponding rule
  sentences. Bears on: **task 0** and **task 1**. Edge 3 (lift → paydown) is not affected: its sentence is
  singular and the write closes it.

---

#### CG-4 — `SOURCE-POLICY RED` — the inherited remittance-timing sentence is neither honoured nor overridden

- **symptom** `meal_ext_period_recovery_amount` fires on `trigger: state_due` and states no time gate at
  all, while the base policy it extends fixes the day a period's charges are remitted, and its `overwrite`
  names only the deduction-ceiling sentence.
- **root cause** an inherited base provision governing *when* the write is due was left in force but not
  implemented, and the extended rule supplies a different due-ness test ("the period carried by the most
  recent charge accrued").
- **evidence**
  - base `meal_payroll_recovery_terms` (verbatim in `meal.extended.yaml`): "A payroll period's charges are
    remitted the number of days after the period closes printed against the plan, and no more than the
    deduction ceiling printed against the same plan is recovered in one period; what is left over rolls
    into the next period." The second half of that sentence is superseded; the first half is not.
  - `meal_ext_period_recovery_amount.overwrite` names only `superseded_clause: "no more than the deduction
    ceiling printed against the same plan is recovered in one period"`.
  - the parameter the base sentence points at is `payroll_deduction_lag_days` (`parameter_schema`:
    "calendar days between a pay period closing and its deduction being remitted"); it appears in no
    extended rule, no `compute` binding and no `baseline.params` anywhere in the charter.
- **demonstrated consequence** base entails *wait*, extended entails *act now*, on the same world —
  demonstrated with dates and the plan's lag value against task 0's world in `0.md`.
- **affected artifact** `meal.extended.yaml`, `meal_ext_period_recovery_amount.rule` /`.overwrite`.
  Bears on: **task 0**.

---

#### CG-5 — `SOURCE-POLICY RED` — overdraft charges are carried into payroll arrears against an undeclared base binding

- **symptom** `meal_ext_restriction_lift_balance` increases the charges awaiting **payroll** recovery by
  overdraft charges that the base charter books against **stored value**, and no `overwrite` names the base
  provision it displaces.
- **root cause** the extended policy's carry-forward formula reaches a quantity governed by a base policy
  that is not in its `base_policy_refs` at all.
- **evidence**
  - base event declaration `meal_overdraft_fee_posted` (charter `events`): `target: meal_transactions`,
    `account: meal_balance`, `direction: out`, "a charge is raised because a till transaction took the
    stored value below zero".
  - base `meal_purchase_and_tender_rules`: "Where stored value is short, the plan's overdraft limit carries
    the transaction down to that limit and the overdraft charge printed against the plan is raised".
  - extended rule: "Where the account has stood restricted for longer than the grace days printed against
    the plan and two or more overdraft charges have been raised on it in the last three calendar months,
    the overdraft charges carried are the whole of those charges"; compute
    `overdraft_carry_usd`, added into `result` with a `+`.
  - `meal_ext_restriction_lift_balance.base_policy_refs` = `[meal_restriction_terms,
    meal_payroll_recovery_terms]`; `overwrite` names one sentence of `meal_payroll_recovery_terms`.
    `meal_purchase_and_tender_rules` and the event binding are named nowhere.
- **demonstrated consequence** demonstrated on task 0's world in `0.md`: the same two overdraft charges have
  already been taken out of stored value under the base binding and are added again to payroll arrears,
  moving the scored figure by 6.00.
- **affected artifact** `meal.extended.yaml`, `meal_ext_restriction_lift_balance.overwrite` /
  `factors.overdraft_charge_carry` / `compute.overdraft_carry_usd`. Bears on: **task 0**.

---

#### CG-6 — `SOURCE-FACTOR RED` — two tier outcomes of `meal_ext_restriction_lift_balance` are not treatments this line of business publishes

- **symptom** `stored_tender_meal_restoration` adds back into payroll arrears the full value of meals the
  employee has **already paid for out of their own stored value**, with no offsetting credit to that stored
  value; `overdraft_charge_carry` does the same for overdraft charges already taken out of stored value.
  The employee is charged twice for the same items.
- **root cause** the ladder's outcomes are written as pure additions to the carry-forward figure, with no
  corresponding movement on the `meal_balance` account that the base charter binds those rows to.
- **evidence**
  - base event `meal_purchase_posted`: `account: meal_balance`, `direction: out` — a `badge_tap` meal has
    already reduced stored value when it is rung.
  - extended rule: "Where charges still stand awaiting recovery on the account and two or more meals have
    been rung against stored value on it in the last calendar month, the meals restored to payroll recovery
    are **the whole value of those meals**"; `result` adds `declined_meal_restoration_usd`.
  - nothing anywhere in the charter returns that value to `meal_balance_usd`; the target tool
    `lift_meal_account_restriction_a306574a` updates only `status`, `restriction_start_date` and
    `payroll_arrears_usd`.
  - the base charter's own account meanings are explicit that these are different pockets of the employee's
    money: `meal_balance` = "spendable stored value the employee has"; `payroll_arrears` = "meal charges the
    employee has run up that payroll has not yet recovered".
- **demonstrated consequence** demonstrated on task 0's world in `0.md`: 33.45 of meals already paid from
  stored value, plus 6.00 of overdraft charges already taken from stored value, are added to what payroll
  will recover, so the employee pays 39.45 twice. No workplace dining operator publishes that as its
  reinstatement treatment; the fall-through tiers ("nothing is restored", "no overdraft charge is carried")
  are what the business does.
- **affected artifact** `meal.extended.yaml`, `meal_ext_restriction_lift_balance` factors
  `stored_tender_meal_restoration` and `overdraft_charge_carry`, their rule sentences and the `result`
  binding. Bears on: **task 0**.

---

#### CG-7 — observation — `value_application_basis`' fall-through tier is unreachable at its own write

- **symptom** the ladder's tiers 1 and 2 both begin "the account stands restricted", and the fall-through
  "where neither holds, the whole of the stored value standing is applied" can only be reached by an account
  that does **not** stand restricted.
- **evidence** `meal_ext_restriction_lift_balance.subject` is `[meal_account_reinstated]`; the base event
  declares `mutation: {transition: {from: restricted, to: active}}`; the tool sets `status="active"` from a
  restricted account. Every account that reaches this write stands restricted.
- **consequence** the clause "the account stands restricted", taken on its own, holds of every customer who
  reaches this write and so divides no one; the ladder effectively has two reachable tiers
  (value loaded in the month, or not). It is recorded as an observation rather than a red light because the
  two reachable tiers still select different values and the factor still bears weight on task 0's world
  (shown in `0.md`).
- **affected artifact** `meal_ext_restriction_lift_balance.factors.value_application_basis`. Bears on: **task 0**.

---

#### CG-8 — observation — every tool docstring carries the word "before"

Four agent tools: "read it from the meal account lookup **before** this call"; the two user tools: "as the
dining services desk reads it out to you **before** you make the payment / give your consent". These place
an argument against a *read*, name no task tool and state no write's position among the others, so no
second reading of any order follows. Recorded for re-audit. Affects all six tools in `task_tools.py`.

---

#### CG-9 — observation — the reinstatement tool writes into the event family the "recovery entry" state is read from

`lift_meal_account_restriction_a306574a` creates a row with `event_type="meal_payroll_deduction_posted"`
and `transaction_code="balance_adjustment"`. See `prerequisite_sentences` above for why this does not
defeat the single-reading test. Affects `task_tools.py` and edges 1–2 of the graph.

---

#### CG-10 — observation — base "one application row per lot touched" vs a single-row tool

Base `meal_subsidy_application_rules`: "Lots are drawn oldest first … producing one application row per lot
touched." `apply_allowance_to_ticket_3fbfdeca` books exactly one row and leaves
`subsidy_lot_reference=""`. No `overwrite` names the sentence. No consequence is demonstrable on either
task's world (in task 1 exactly one unlapsed lot is available at handling time), so it is not a red light.
Affects `meal_ext_ticket_allowance_application`, `task_tools.py`.

---

#### CG-11 — observation — the cafe's per-employee daily cap is added to the employee's allowance pot

Base `meal_combination_employer_program_interaction`: "allowance is spendable at the cafe counter, and the
employer's own subsidy funding **meets the drawdown behind it**" — the cafe's funding stands behind the
allowance rather than beside it. `employer_counter_topup` adds
`CPARAM('cafe','subsidy_cap_per_employee_per_day_usd')` into `allowance_pot_usd`. The base sentence governs
who pays rather than how much the employee may draw, so the conflict is not demonstrable as two readings of
a scored number; recorded for re-audit. Affects `meal_ext_ticket_allowance_application`. Bears on: **task 1**.

---

#### CG-12 — observation — `stored_tender_meals_1m` reads only `badge_tap`, but `mobile_order` is also stored value

The rule says "meals … rung against stored value"; the compute reads `payment_channel='badge_tap'` only,
while the charter's `mobile_order_enabled` plan parameter and the schema's `mobile_order` channel are also
stored-value tenders. No `mobile_order` row exists in either task's seed, so no consequence is demonstrable.
Affects `meal_ext_restriction_lift_balance`.

---

#### CG-13 — observation — "meals rung on the account" is computed as `meal_purchase` only

`meal_ext_daily_allowance_grant.meals_1m_count` and `meal_ext_reinstatement_paydown.purchase_count_1m`
read `transaction_code='meal_purchase'` under rule sentences that say "meals have been rung on the
account"; the schema's `guest_meal` rows are also meals rung on the account. On both tasks' worlds the tier
is the same either way (task 0: 3 vs 4, both ≥ 1; task 1: 5 vs 6, both ≥ 4), so no consequence is
demonstrable. Affects two policies.

---

#### CG-14 — observation — the other products' holdings are seeded against the employee's own profile

`cafe_contracts.customer_id` and `market_agreements.customer_id` in both tasks carry the **employee's**
`customer_id`, although `db_schema.json` defines them as "client organisation holding the contract /
agreement" and `blueprint.yaml` says the clients "are employers … who hold a contract site by site". This
is forced by the compute DSL: `CFIELD`/`CPARAM` scope every cross-category read by
`eq["customer_id"] = CUST` (`skills/erl-task-instantiate/scripts/check_compute.py`, `_cross`). The read
still lands on exactly one row per task and `find_cafe_contracts(customer_id=…)` reaches it, so no second
reading follows; recorded because the seeded world contradicts the scenario's own ontology.
Bears on: **task 0**, **task 1**.

---

#### CG-15 — observation — seeded `original_pos_reference` values point at till transactions that are not in the ledger

Task 0's `charge_accrual` rows carry `original_pos_reference` `POS-30000000`…`POS-30001688`; task 1's
`charge_accrual` and `subsidy_application` rows carry `POS-52001345`…`POS-52007532`. No
`meal_transactions` row in either seed has any of those as its `pos_reference` (task 0's purchases are
`POS-2000xxxx`, task 1's are `POS-5100xxxx`). The schema defines the field as "the till transaction this row
reverses, adjusts or funds". Consequence: the record chain a reader needs to test edge 5's condition
("each eligible till transaction of the period carries the allowance application it is owed") cannot be
walked at all — this is the world half of **CG-3** for task 1. Affects `tasks/0.json` and `tasks/1.json`
`initial_state.meal_transactions`.

---

#### CG-16 — observation — a biweekly account's ledger is labelled in half-month pay periods

Task 0's account carries `payroll_cycle: "biweekly"` while every `pay_period` on its own rows is
`YYYY-MM-P1`/`P2`, which `post_payroll_recovery_c9e76aa9`'s docstring defines as "one digit for the **half
of the month**" — a semimonthly labelling. The field is load-bearing:
`recoverable_window_basis` takes its tier from `F('payroll_cycle')`. The clash originates in
`db_schema.json` (one `pay_period` format for all four cycles), not in this difficulty's authoring; the
alternative number it would give is recorded in `0.md`. Bears on: **task 0**.

---

#### CG-17 — observation — the ticket an allowance lot is spent on carries no recency window

`meal_ext_ticket_allowance_application`: "The ticket is the largest meal rung against payroll on the
account" — `MAX('meal_transactions','amount_usd', …)` with no `within_months`. On a plan whose
`subsidy_expiry_days` is 1, today's lot can therefore be spent against an arbitrarily old till transaction.
The base day-scoping ("what is left in the employee's lots for the day") is legitimately superseded, so this
is not an undeclared override; recorded as a realism observation. Bears on: **task 1**.


---

## closing_checklist

Written **after** both tasks' `source_derivation_frozen` and `source_gt_comparison` sections were on disk,
so it sits below the pre-reveal charter-global section rather than inside it.

**This difficulty does not close out.** Step 4's checklist is answered honestly below; four of its items
fail, and both tasks carry a red light on all four relationships.

| item | state |
| --- | --- |
| per-task audit files correspond one-to-one with the tasks, `_difficulty.md` alongside them | ✓ `0.md`, `1.md`, `_difficulty.md` in `env/env_0013_workplace_dining_and_catering_provider/audits/policy_task/employee_meal_account_desk/` |
| old revisions traceable | ✓ first revision; nothing overwritten |
| every comparison section carries a PASS | ✗ — `0.md` carries SOURCE-POLICY / SOURCE-CHAIN / SOURCE-FACTOR / SOURCE-TASK RED; `1.md` the same four |
| this difficulty's extended policies fully covered | ✓ all 6, three per task |
| the M tasks' scopes pairwise disjoint, each spanning its whole problem tree | ✓ `{period_recovery, reinstatement_paydown, restriction_lift_balance}` vs `{daily_allowance_grant, ticket_allowance_application, payroll_charge_consent}`; both `charter_scope` blocks match the trees derived blind |
| task tools and GT closed | ✓ 6 tools, 3 per task, every gold argument derivable from reachable records |
| each task tool uses an independently generated, frozen uuid8 | ✓ see `### action_binding_and_uuids` |
| every tree has 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 `owner=user` write, no cycle | ✓ task 0: n=2, 3 `value_input` edges, `load_arrears_paydown_ff1c695b`; task 1: n=2, 2 `value_input` edges, `confirm_payroll_charge_accrual_6d54e4b8` |
| the difficulty's `prerequisite` edges together are still a DAG, no cycle from cross-task references | ✓ two disjoint DAGs, no edge crosses the trees |
| every computation declares a self-sufficient baseline, 4–6 factors (2 `parameter`, 1 `method`), ≥1 multi-source and ≥1 cross-difficulty per task, every ladder ≥3 tiers stated in full in its rule | ✓ on counts; 30/30 factors bear weight on their tasks' worlds against honest baselines, and every whole-baseline fall-back is definite and differs from gold |
| every ladder's **tiers distinct in outcome** | ✗ — **CG-2**: `guest_meal_pot_exclusion`, `guest_surcharge_addition`, `prior_accrual_netting` each carry one rule written as two tiers |
| every ladder's **conditions and outcomes ones that line of business actually holds** | ✗ — **CG-6**: `stored_tender_meal_restoration` and `overdraft_charge_carry` re-bill money the employee has already paid; **CG-7**: one fall-through tier is unreachable at its own write |
| policy self-consistent, every prerequisite stated by a prerequisite sentence in the blocked rule in the state form | ✗ on self-consistency — **CG-1**, **CG-3**, **CG-4**, **CG-5** — though all five prerequisite sentences are verbatim, state-form and structurally sound |
| instantiation-stage gates re-run once on the final form | ✓ see below |

### gate re-run on the final form (2026-09-22)

```
$ .venv/bin/python skills/erl-task-instantiate/scripts/check_extended.py "$DIFF"
🔎 EXTENDED gate  (category=meal, extended_policies=6, cross-cat=3, task_tools=6, tasks=2, no_handoff=True)
  [PASS] compatible charter; cross-category reads declared exactly; every task has a multi-source and a cross-difficulty factor; every prerequisite is stated by a prerequisite sentence; every task calls a customer's own tool; all policies are covered across the suite with disjoint scopes
EXTENDED OK

$ .venv/bin/python skills/erl-task-instantiate/scripts/check_task_tools.py "$DIFF"
TASK TOOL CONTRACT OK

$ .venv/bin/python skills/erl-task-instantiate/scripts/check_solvability.py "$DIFF"
0.json         True     3          3         22 True
1.json         True     3          4         30 True
SOLVABILITY OK

$ .venv/bin/python skills/erl-task-instantiate/scripts/check_compute.py "$DIFF"
suite depth:  history_rows_max=51(>= 8)   branches_max=51(>= 5)
COMPUTE OK

$ .venv/bin/python skills/erl-task-instantiate/scripts/check_grounding.py "$DIFF"
0.json                   2        3       3     9  True
1.json                   2        3       3     7  True
GROUNDING OK

$ .venv/bin/python skills/erl-task-instantiate/scripts/check_cross_fire.py "$DIFF"
SCOPE OK

$ .venv/bin/python skills/erl-task-instantiate/scripts/replay_tasks.py "$DIFF" --check
0.json                         11 True    True    0    24    24   True
1.json                         13 True    True    0    35    35   True
REPLAY OK
```

All seven gates are green on the final form, and the two shared sources still hash to
`906597034a8ba149054b2ab8723795870824d8e02c3ce5ab1340ea3f4dd2f9a4` (`meal.extended.yaml`) and
`2fd04d28ab652a00769f609c21c81ad0ef25697c575c7f6af2c09f1f32aaa250` (`task_tools.py`), and each task's
`frozen_time` / `user_scenario` / `initial_state` are byte-identical to the masked views the blind
derivations were built from. **Every defect reported here is one no gate in this suite inspects**: rule↔compute
equivalence on an equality filter (CG-1), tier outcomes that collapse into one rule (CG-2), a prerequisite
quantifier a single resolving write cannot close (CG-3), an inherited base time anchor (CG-4), an
undeclared conflict with a base *event binding* rather than a base policy (CG-5), and whether a tier's
outcome is a treatment the business actually publishes (CG-6). A machine green light remains the
qualification to enter this audit, not a proof of correctness.

### per-task verdicts

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | SOURCE-POLICY RED (F-2, F-3, F-5) | SOURCE-CHAIN RED (F-1, F-6, F-7) | SOURCE-FACTOR RED (F-4) | SOURCE-TASK RED |
| 1 | SOURCE-POLICY RED (F-1) | SOURCE-CHAIN RED (F-3) | SOURCE-FACTOR RED (F-2) | SOURCE-TASK RED |

In both tasks the independent blind derivation reproduced **every** gold value, owner, order and terminal
field — 17 of 17 figures on task 0, 23 of 23 on task 1, including every `factor_sensitivity` and
`baseline_result`. The red lights are therefore not arithmetic disagreements with GT; they are places where
a second reading of the artifacts is equally defensible, where a declared prerequisite state is never
reached, where a tier is not a tier, or where a tier's outcome is not what the business does.

---

# revision_2

## charter_global_frozen (round 2)

- auditor: same independent source-layer auditor; round-1 text above is untouched
- freeze time (charter-global section): 2026-09-22, written **before** either task's round-2 GT was revealed
- re-derivation grounds, per the carry-forward rule:

  | shared source | round 1 | round 2 | action |
  | --- | --- | --- | --- |
  | `meal.extended.yaml` | `9065970…f2f9a4` | `13ceddd1…2f7c36` | **CHANGED → charter-global section re-derived in full** |
  | `task_tools.py` | `2fd04d28…f32aaa250` | `2fd04d28…f32aaa250` | **UNCHANGED → `### action_binding_and_uuids` and findings CG-8, CG-9 carried forward by reference** |

- rebuilt masked views: `0.masked.json` `sha256 735e0725c09d6ebc91ea6392cc91db9529726ebbe8a4e3115d78e688f001a4d2`,
  `1.masked.json` `sha256 8639fbba2643e2ba64f025c41fbf5867df895079325a55c0ffa7fb8224a42982`
- **this round is not blind.** Round 1's GT has been seen, so the round-2 derivation is an independent
  recomputation, not a blind one. It was still frozen to disk before the round-2 GT was opened, so the
  comparison remains a comparison rather than a transcription.
- fields masked until the freeze: as in round 1.
- entry conditions: the coordinator supplied the seven gate outputs on the reworked form, all green, plus
  the rebuilt views and hashes. Complete.

**Base was not touched — verified independently rather than accepted.** Every top-level section of the base
copy inside `meal.extended.yaml` (`binding`, `lifecycle`, `accounts`, `parameter_schema`, `variants`,
`events`, `measures`, `policies`) is object-identical to `blueprint/products/meal.yaml`. The coordinator's
`git diff --stat` claim is not usable on its own here, because the whole scenario directory is still
untracked; the identity check above is what carries the conclusion.

### what moved

| policy | changed keys |
| --- | --- |
| `meal_ext_period_recovery_amount` | `rule`, `overwrite` |
| `meal_ext_reinstatement_paydown` | `rule`, `compute`, `compute_basis`, `factors`, `prerequisite` |
| `meal_ext_restriction_lift_balance` | `rule`, `overwrite`, `prerequisite`, `params`, `inputs`, `cross_category`, `compute`, `compute_basis`, `baseline`, `factors` |
| `meal_ext_daily_allowance_grant` | `rule`, `compute_basis`, `factors` |
| `meal_ext_ticket_allowance_application` | `rule`, `overwrite`, `prerequisite`, `compute`, `compute_basis`, `factors` |
| `meal_ext_payroll_charge_consent` | `rule`, `prerequisite`, `compute`, `compute_basis`, `factors` |

Both worlds were reseeded: task 0's `payroll_cycle` moved `biweekly → semimonthly`, its
`meal_balance_usd` `8.75 → 18.40`, a `market_agreements` row was added at `CS-517`, the refund row was
removed and the two `guest_meal` rows were re-tendered to `payroll_deduction`; task 1's accrual amounts
were rebuilt so that each equals its meal less the allowance already applied to it
(18.35 − 9.50 − 4.05 = 4.80; 16.80 − 9.50 = 7.30; 21.40 − 0 = 21.40), its `payroll_arrears_usd` moved
`8.20 → 26.20`, and the 2026-05-06 grant/application pair was dropped.

### policy_conflict_scan (round 2)

The six extended policies, their subjects, computes and target tools are unchanged; the two-component
`prerequisite` graph is unchanged in shape:

- tree A — root `meal_ext_restriction_lift_balance`; prerequisite problems `meal_ext_reinstatement_paydown`
  and `meal_ext_period_recovery_amount`; internal edge paydown → period_recovery. 3 edges, all `value_input`.
- tree B — root `meal_ext_payroll_charge_consent` → `meal_ext_ticket_allowance_application` →
  `meal_ext_daily_allowance_grant`. 2 edges, both `value_input`.

Vertex sets disjoint, union exhaustive: scopes still mutually exclusive and jointly complete. Acyclic; no
edge crosses the trees.

Cross-category reads are declared exactly: cafe for `meal_ext_period_recovery_amount` and
`meal_ext_daily_allowance_grant`; cafe + market for `meal_ext_ticket_allowance_application`; **market + cafe
newly declared** for `meal_ext_restriction_lift_balance`, matching its new
`CFIELD('market','status', …)`, `CFIELD('cafe','status', …)` and
`CPARAM('cafe','meal_periods_served', …)`. `meal_periods_served` exists in `cafe.yaml`'s
`parameter_schema` and is populated on all six cafe variants (1, 1, 2, 3, 2, 3), so neither cross read
returns absent.

### rule_compute_equivalence (round 2)

Re-run binding by binding over all six policies. Every quantity, window, tier, branch, cross-category read,
cap/floor and rounding point carries a verbatim `compute_basis` quotation drawn from its own `rule`, and
the sweep back finds a binding for every rule sentence, **with one exception recorded as N-4** (the ticket
policy's new sentence "allowance reaches any meal rung against payroll **that still carries none**", which
`payroll_meals_max_usd` does not implement).

Round 1's **CG-1 is closed**: `balance_refunds_1m`/`_3m` no longer carry a bare `payment_channel='badge_tap'`
filter. They now read
`MX(0.0, SUM(…, transaction_code='refund') − SUM(…, transaction_code='refund', payment_channel='subsidy'))`,
and the rule now states the exclusion outright — "A refund that restores employer allowance is never
credited here, because it returns the employer's own funding rather than the employee's money" — with
`compute_basis` quoting the matching tier sentence. Rule and compute agree in both directions.

Four ladder `when` strings are paraphrases of their rule sentences rather than literal substrings
("the subsidy **it** publishes" vs "the subsidy **that programme** publishes"; "the grant amount printed
against the plan" vs "**that** printed grant amount"), in `employer_programme_share` and
`employer_funded_base`. Both were present in round 1 and judged equivalent then; the judgement stands —
same condition, same tier, same branch.

### action_binding_and_uuids (round 2)

`task_tools.py` is byte-identical to round 1 (`2fd04d28ab652a00769f609c21c81ad0ef25697c575c7f6af2c09f1f32aaa250`).
Carried forward by reference from `revision_1 / ### action_binding_and_uuids`: six distinct uuid8s, none
batch-derived; each `(target_tool, computes)` claimed by one policy. Re-checked that the six `computes`
names are unchanged in the reworked charter — they are.

### prerequisite_graph and prerequisite_sentences (round 2)

All five edges re-tested mechanically and by reading:

| blocked policy | policy_source verbatim in its **own** rule | absent from the depended-on rule | form | gate is a real binding | `resolved_by` = depended-on `target_tool` |
| --- | --- | --- | --- | --- | --- |
| `meal_ext_reinstatement_paydown` | ✓ | ✓ | state | `measured_balance_usd` ✓ | ✓ |
| `meal_ext_restriction_lift_balance` (→ recovery) | ✓ | ✓ | state | `balance_standing_usd` ✓ | ✓ |
| `meal_ext_restriction_lift_balance` (→ paydown) | ✓ | ✓ | state | `applied_from_value_usd` ✓ | ✓ |
| `meal_ext_ticket_allowance_application` | ✓ | ✓ | state | `lots_in_window_usd` ✓ | ✓ |
| `meal_ext_payroll_charge_consent` | ✓ | ✓ | state | `allowance_credited_usd` ✓ | ✓ |

**CG-3 is closed.** All four over-quantified sentences were narrowed to the single object the single
resolving write actually settles, and each now matches the depended-on policy's own singular result:

| edge | round 1 | round 2 | the depended-on rule's singular result |
| --- | --- | --- | --- |
| paydown → recovery | "the recovery entry owed for **every closed payroll period**" | "the recovery entry owed for **the payroll period the account's most recent accrued charge carries**" | "The payroll period a remittance is made for is the period carried by the most recent charge accrued on the account." |
| lift → recovery | "the recovery entry due for **each closed payroll period**" | "the recovery entry due for **the payroll period the account's latest accrued charge belongs to**" | same |
| ticket → grant | "the allowance **lots** the account is owed for the grant period **stand**" | "the allowance **lot** the account is owed for the **current** grant period **stands**" | one lot per call (`grant_daily_allowance_lot_ed948b99` mints one `subsidy_lot_reference`) |
| consent → ticket | "**each eligible till transaction of the period** carries the allowance application it is owed" | "**the largest till transaction rung against payroll on the account** carries the allowance application it is owed" | "The ticket is the largest meal rung against payroll on the account" |

Each `condition` now mirrors its sentence at the same strength, and each is a state one write makes true.
The four-point test passes on all five; state form throughout, so no `fallback_reason` is required and
none is present.

CG-9 is carried forward unchanged (the tool module did not move), and its risk is now **lower**, not
higher: the waited-on state names a **payroll period**, and the `balance_adjustment` row
`lift_meal_account_restriction_a306574a` books carries `pay_period=""`, so it cannot be read as the
recovery entry any period is owed.

### override_declarations (round 2)

Nine `overwrite` entries, up from six. All nine pass the three-part soundness test mechanically:
`superseded_clause` is a verbatim substring of the named base policy's `rule`; `replaced_by` is a verbatim
substring of the extending policy's own `rule`; and the named base policy is in that policy's
`base_policy_refs`.

| policy | base policy | superseded clause | new this round |
| --- | --- | --- | --- |
| `meal_ext_period_recovery_amount` | `meal_payroll_recovery_terms` | "no more than the deduction ceiling printed against the same plan is recovered in one period" | |
| `meal_ext_period_recovery_amount` | `meal_payroll_recovery_terms` | "A payroll period's charges are remitted the number of days after the period closes printed against the plan" | **yes — closes CG-4** |
| `meal_ext_reinstatement_paydown` | `meal_restriction_terms` | the reinstatement-share sentence | |
| `meal_ext_restriction_lift_balance` | `meal_payroll_recovery_terms` | "A meal tendered against payroll is added to the charges awaiting recovery" | replaced_by rewritten |
| `meal_ext_daily_allowance_grant` | `meal_subsidy_grant_rules` | the per-period grant-ceiling sentence | |
| `meal_ext_ticket_allowance_application` | `meal_subsidy_application_rules` | the "held … to what is left in the employee's lots for the day" sentence | |
| `meal_ext_ticket_allowance_application` | `meal_subsidy_application_rules` | "producing one application row per lot touched" | **yes — closes CG-10** |
| `meal_ext_ticket_allowance_application` | `meal_combination_employer_program_interaction` | "the employer's own subsidy funding meets the drawdown behind it" | **yes — closes CG-11** |
| `meal_ext_payroll_charge_consent` | `meal_payroll_recovery_terms` | the accrual sentence | |

**CG-5 and CG-6 were closed by deletion, and the deletion is sound.** Three factors of
`meal_ext_restriction_lift_balance` were removed — `payroll_refund_offset`, `overdraft_charge_carry`,
`stored_tender_meal_restoration` — together with their bindings (`payroll_refunds_3m`,
`payroll_refunds_12m`, `overdraft_count_3m`, `overdraft_total_3m`, `overdraft_carry_usd`,
`stored_tender_meals_1m`, `stored_tender_meal_count_1m`, `declined_meal_restoration_usd`) and the params
`half_value_credit_pct`, `single_overdraft_relief_usd`, `single_meal_relief_usd`. Checked for the two
hazards a deletion carries:
- **no stranded binding** — no surviving `compute` expression, `factors[].bindings` entry, `inputs` entry
  or `compute_basis` key references any deleted name; `params` now holds exactly the two keys the surviving
  ladders use (`broad_pickup_share_pct`, `narrow_pickup_share_pct`), and `inputs.history` was rewritten to
  the three aggregates the new compute actually takes.
- **no floor breach** — the policy still declares 4 factors (1 `method`, 3 `parameter`), because two
  replacements were added: `working_float_left` and the cross-difficulty pair `employer_pickup_base`
  (market) / `employer_pickup_share` (cafe). The `result` no longer **adds** anything to the balance
  standing: it is `balance_standing − value_settled − employer_pickup`, floored at nothing, so nothing
  already met from the employee's stored value is added back. The rule says so in terms —
  "Nothing already met from the employee's stored value is carried into the charges awaiting payroll
  recovery, since stored value and payroll arrears are separate pockets of the employee's money."
  **CG-5 closed; CG-6 closed.** A new defect in the replacement material is recorded as **N-2**.

**CG-12 lapses**, as claimed: its binding (`stored_tender_meals_1m`, `payment_channel='badge_tap'` under a
"rung against stored value" rule) lived in the deleted material and no longer exists.

### factor_ladders (round 2)

30 factors over 6 policies, unchanged in count.

| policy | factors | `parameter` | `method` | cross_difficulty |
| --- | --- | --- | --- | --- |
| `meal_ext_period_recovery_amount` | 4 | 3 | 1 | `employer_programme_share` → cafe |
| `meal_ext_reinstatement_paydown` | 5 | 4 | 1 | — |
| `meal_ext_restriction_lift_balance` | 4 | 3 | 1 | `employer_pickup_base` → **market**, `employer_pickup_share` → **cafe** |
| `meal_ext_daily_allowance_grant` | 5 | 4 | 1 | `employer_funded_base` → cafe |
| `meal_ext_ticket_allowance_application` | 6 | 5 | 1 | `employer_counter_topup` → cafe, `second_counter_trim` → market |
| `meal_ext_payroll_charge_consent` | 6 | 5 | 1 | — |

Per tree: tree A now carries three cross-difficulty factors (was one), tree B three. Bindings remain
pairwise disjoint within each policy; every `decides` names an input, never `result`. Every ladder has
three tiers, conditions pairwise disjoint as stated, every tier in the `rule` and in the `decides` branch.

**CG-2 is closed.** All three collapsed ladders now carry three rules a world can tell apart:

| factor | round 1 tier 1 / tier 2 | round 2 tier 1 / tier 2 |
| --- | --- | --- |
| `guest_meal_pot_exclusion` | surcharge × count / surcharge × 1 | **the whole value of those guest meals** / the printed surcharge, once |
| `guest_surcharge_addition` | surcharge × count / surcharge × 1 | surcharge × count **together with the whole value of those guest meals** / surcharge × count |
| `prior_accrual_netting` | the month's charges / the month's charges − the month's recovery | **every charge accrued in the last three calendar months** / the month's charges − the month's recovery |

In each case tier 1's expression can no longer reproduce tier 2 on tier 2's domain: `guest_value_1m`,
`guest_value_3m` and `charges_3m` are new bindings with values independent of the count the tiers split on.

**CG-7 is closed.** `value_application_basis` no longer conditions any tier on "the account stands
restricted", a clause that held of every customer reaching a restricted → active write. Its ladder now
splits on whether value was loaded in the calendar month and on how long the restriction has stood against
the plan's grace days, and its fall-through ("the whole of the stored value standing") is reachable by any
account with no load in the month.

**CG-13 is closed.** The three rules that said "meals … rung on the account" while their compute counted
`transaction_code='meal_purchase'` alone now say "meals **of the employee's own**"
(`meal_ext_daily_allowance_grant.grant_period_ceiling_band`,
`meal_ext_reinstatement_paydown.working_balance_restoration`,
`meal_ext_restriction_lift_balance.working_float_left`), which is exactly the `meal_purchase` /
`guest_meal` distinction the schema draws.

Distinct-outcome and business-reality sweep over the six replaced or new ladders: `working_float_left`
(reload amount / smallest single load / nothing — three distinct figures, and the rule states outright
that the float is "neither charged to them again nor recovered from their pay"), `employer_pickup_base`
(one month / three months / nothing), `employer_pickup_share` (broad 12 % / narrow 6 % / nothing),
`value_application_basis` (the month's loads / the standing value less the smallest single load / the whole
standing value). All distinct; all conditions divide customers rather than restating the policy's scope.
Two new defects are recorded as **N-1** (two of these are labelled `parameter` while selecting a history
window) and **N-5** (a three-month count tested against a one-month allowance).

### findings (round 2)

Round-1 items are dispositioned in `## round_1_item_disposition` below. New findings this round:

---

#### N-1 — `SOURCE-FACTOR RED` — two factors labelled `parameter` select a history window, which this same charter labels `method`

- **symptom** `meal_ext_payroll_charge_consent.prior_accrual_netting` and
  `meal_ext_restriction_lift_balance.employer_pickup_base` are declared `effect: parameter`, but their
  tiers choose which rows are aggregated, not which number is substituted.
- **root cause** both ladders were rewritten this round to break CG-2's collapse, and the fix was made by
  swapping the aggregation window rather than the figure — without moving the label.
- **evidence**
  - `prior_accrual_netting`, tier 1 → `charges_3m` = `SUM(…, within_months=3, transaction_code='charge_accrual')`;
    tier 2 → `MX(0.0, charges_1m − recoveries_1m)` with `charges_1m` over `within_months=1`. Different row
    sets, different expression.
  - `employer_pickup_base`, tier 1 → `charges_accrued_1m`; tier 2 → `charges_accrued_3m`. Pure window swap.
  - the charter's own convention, applied four times elsewhere and **once in the very same policy**:
    `charge_window_basis` (`meal_ext_payroll_charge_consent`, `effect: method`) selects between
    `payroll_meals_1m`, `payroll_meals_3m` and `payroll_meals_all`; likewise `recoverable_window_basis`,
    `measured_balance_basis` and `lot_window_basis`, all `method`.
- **demonstrated consequence** the label is dishonest against the charter's own usage: within
  `meal_ext_payroll_charge_consent`, a one-month-versus-three-month choice is `method` in one factor and
  `parameter` in the next. The per-policy counts survive reclassification (consent would read 2 `method` /
  4 `parameter`, the lift 2 / 2, both still ≥ 2 `parameter` and ≥ 1 `method`), so this is a labelling
  defect rather than a floor breach — but a reader told a `parameter` tier substitutes a number and a
  `method` tier changes the algorithm is misdirected on two of thirty factors.
- **affected artifact** `meal.extended.yaml`, `meal_ext_payroll_charge_consent.factors.prior_accrual_netting.effect`
  and `meal_ext_restriction_lift_balance.factors.employer_pickup_base.effect`.
- **relation to previous revisions** new in round 2; introduced by the CG-2 and CG-5/CG-6 rework.

---

#### N-2 — `SOURCE-POLICY RED` — the value "settled from the account" never leaves the account

- **symptom** `meal_ext_restriction_lift_balance` reduces the charges carried forward by
  `value_settled_usd`, and states in terms that the **float** stays on the account — implying the settled
  part does not. No write in this difficulty reduces `meal_balance_usd` by anything.
- **root cause** the rework added the sentence that makes the two halves explicit, while the write layer
  (frozen this round) books only a status change, an arrears figure and a `balance_adjustment` row.
- **evidence**
  - rule, new this round: "The value settled from the account is the value applied less the working float
    left, and it is never read as less than nothing; **the float stays on the account as the employee's own
    spendable value and is neither charged to them again nor recovered from their pay**."
  - `compute.result`: `RND(MX(0.0, balance_standing_usd − value_settled_usd − employer_pickup_usd), 2)`.
  - `task_tools.py`, `lift_meal_account_restriction_a306574a`: the only `ctx.update` is
    `ctx.update("meal_accounts", meal_account_id, status="active", restriction_start_date="", payroll_arrears_usd=carried)`.
    `meal_balance_usd` is not among the fields, and the `ctx.create` row is
    `event_type="meal_payroll_deduction_posted"`, which `blueprint/products/meal.yaml` binds to the
    `payroll_arrears` account, not to `meal_balance`.
  - `db_schema.json`, `meal_accounts.meal_balance_usd`: "current spendable stored value on the account;
    **identically the sum of the meal_balance account deltas**".
- **demonstrated consequence** demonstrated on task 0's world in `0.md` (revision_2): 92.85 is settled
  against the arrears while the whole 136.25 stays spendable, so the employee's payment reduces the arrears
  and stays in their pocket. The same shape, smaller, appears in task 1 (`stored_value_applied_usd` 8.60
  against a `meal_balance_usd` that does not move). Two passages of the artifacts reach different
  conclusions about the post-write world.
- **affected artifact** `meal.extended.yaml`, `meal_ext_restriction_lift_balance.rule` /
  `compute.value_settled_usd` / `compute.result`, and `meal_ext_payroll_charge_consent.compute.stored_value_applied_usd`;
  `task_tools.py`, `lift_meal_account_restriction_a306574a`. Bears on: **task 0** (primary), **task 1**.
- **relation to previous revisions** the netting term existed in round 1 and this audit did not flag it
  then; the sentence that makes the contradiction explicit is new in round 2. Reported now as a defect
  found this round, not as a regression caused by the rework.

---

#### N-3 — observation — `meal_ext_restriction_lift_balance.baseline.rule` refers to a base it never defines

The baseline keeps "The part the employer's dining programme picks up is **that base** taken at **that
share**" but drops the sentence that says what the base is (the only definition sits in the tiered rule).
A definite number still follows — "The employer's dining programme picks up nothing of the balance" and
"The share the employer's programme picks up is nothing" both stand, so the pickup is nothing — so a reader
of the computation document alone still reaches a definite, wrong figure (19.15 against a gold of 39.98 on
task 0's world). Recorded as an observation, not a red light. Affects
`meal_ext_restriction_lift_balance.baseline.rule`.

---

#### N-4 — observation — the ticket policy's new sentence states a filter the compute does not apply

New this round: "No window limits which till transaction the ticket may be, because allowance reaches any
meal rung against payroll **that still carries none**." The compute is unchanged —
`payroll_meals_max_usd = MAX('meal_transactions','amount_usd', transaction_code='meal_purchase', payment_channel='payroll_deduction')`
— with no test for whether an allowance application already names the row, and
`compute_basis.payroll_meals_max_usd` still quotes only the "largest meal rung against payroll" sentence.
The rule therefore makes a promise the compute does not keep. No consequence on task 1's world: the largest
payroll meal (`POS-51002076`, 21.40) is also the largest that carries no application, so both readings pick
the same ticket. Recorded as an observation; it would bite on any world where the largest payroll meal is
already met. Affects `meal_ext_ticket_allowance_application`. Bears on: **task 1**.

---

#### N-5 — observation — a three-month guest count is tested against a one-month allowance

`meal_ext_payroll_charge_consent.guest_surcharge_addition` tier 1: "more guest meals have been rung on the
account in the **last three calendar months** than the **guest meal allowance** printed against the plan";
compute `guest_count_3m > P('guest_meals_per_month')`. `parameter_schema` defines
`guest_meals_per_month` as "guest meals the plan allows in **one calendar month**". A three-month count
tested against a one-month allowance is not a comparison this line of business weighs. Not load-bearing on
task 1 (`guest_count_3m` = 2 against an allowance of 2, so the tier is not taken), so it is recorded as an
observation. Affects `meal_ext_payroll_charge_consent`. Bears on: **task 1**.

---

#### N-6 — observation — CG-15 was closed by repair in task 1 and by emptying the field in task 0

Task 1's pointers are genuinely repaired: every `subsidy_application`, `charge_accrual` and `refund` row now
names an `original_pos_reference` that exists as a `pos_reference` in the same ledger, and the accrual
amounts reconcile against their tickets net of the allowance already applied. Task 0 instead **emptied**
`original_pos_reference` on all nine `charge_accrual` rows. That removes the dangling pointers, but the base
event `meal_charge_accrued` declares the field as "the till transaction the charge answers" and its grain as
"one row per till transaction charged to payroll", so the accruals now answer nothing. Relatedly, task 0's
two `guest_meal` rows are tendered `payment_channel="payroll_deduction"` while base `meal_purchase_posted`
declares `triggers: [{event: meal:meal_charge_accrued, when: {payment_channel: payroll_deduction}}]`, and no
accrual matches either amount (27.50, 24.90). Nothing in either task's tree reads these fields, so no second
reading of a scored value follows; recorded as an observation. Affects `tasks/0.json`
`initial_state.meal_transactions`.

---

#### CG-14 — carried forward unchanged, accepted upstream

`cafe_contracts` and `market_agreements` are still seeded with the employee's `customer_id` in both tasks
(task 0 now carries a market row as well). This is the `CFIELD`/`CPARAM` scoping constraint recorded in
round 1 and accepted by the coordinator; confirmed unchanged and not re-litigated.

#### CG-8 — carried forward unchanged

`task_tools.py` did not move; all six docstrings still carry "before". Not a red light, for the reason given
in `revision_1 / ### action_binding_and_uuids`.

## round_1_item_disposition

| item | round-1 verdict | claim | this audit's finding |
| --- | --- | --- | --- |
| CG-1 | SOURCE-POLICY RED | fixed | **CLOSED** — channel filter replaced by an explicit exclusion stated in the rule and mirrored in compute |
| CG-2 | SOURCE-FACTOR RED | fixed | **CLOSED** — all three ladders now carry three distinguishable rules |
| CG-3 | SOURCE-POLICY RED | fixed | **CLOSED** — all four sentences narrowed to the single object the single write settles |
| CG-4 | SOURCE-POLICY RED | fixed | **CLOSED** — new `overwrite` on the remittance-lag clause, sound on all three parts |
| CG-5 | SOURCE-POLICY RED | fixed by deletion | **CLOSED** — factor and all its bindings removed; no stranded reference, no floor breach |
| CG-6 | SOURCE-FACTOR RED | fixed by deletion | **CLOSED** — both offending factors removed; `result` no longer adds anything back |
| CG-7 | observation | fixed | **CLOSED** — fall-through tier now reachable |
| CG-8 | observation | no change | unchanged, as claimed |
| CG-9 | observation | no change | unchanged, and its risk is lower under the new sentence |
| CG-10 | observation | fixed | **CLOSED** — new `overwrite`, sound |
| CG-11 | observation | fixed | **CLOSED** — new `overwrite`, sound |
| CG-12 | observation | lapses | **LAPSED**, as claimed |
| CG-13 | observation | fixed | **CLOSED** — "meals of the employee's own" in all three rules |
| CG-14 | observation | accepted | unchanged, as claimed; not re-litigated |
| CG-15 | observation | fixed | **CLOSED with a residue** — see N-6 |
| CG-16 | observation | fixed | **CLOSED** — task 0's `payroll_cycle` is now `semimonthly`, matching its half-month `pay_period` labels |
| CG-17 | observation | fixed | **CLOSED with a residue** — see N-4 |
| new | — | — | **N-1** SOURCE-FACTOR RED, **N-2** SOURCE-POLICY RED, N-3…N-6 observations |


## closing_checklist (round 2)

**The difficulty still does not close out**, but the gap is much narrower: round 1 carried twelve red
lights across the two tasks and all four relationships failed on both; round 2 carries three, and the
unique-solution relationship now passes on both tasks.

| item | state |
| --- | --- |
| per-task audit files one-to-one with the tasks; old revisions traceable | ✓ `revision_1` text untouched; `revision_2` appended to all three files |
| every comparison section carries a PASS | ✗ — `0.md` carries SOURCE-POLICY (N-2), SOURCE-CHAIN (R2-F-1) and SOURCE-FACTOR (N-1) RED; `1.md` carries SOURCE-FACTOR (N-1) RED |
| extended policies fully covered; scopes pairwise disjoint, each spanning its whole tree | ✓ unchanged; `charter_scope` on both tasks matches the trees derived this round |
| task tools and GT closed; each uuid8 independently generated and frozen | ✓ `task_tools.py` byte-identical to round 1 |
| every tree: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 `owner=user` write, no cycle; the difficulty's edges together a DAG | ✓ task 0: n=2, 3 edges, `load_arrears_paydown_ff1c695b`; task 1: n=2, 2 edges, `confirm_payroll_charge_accrual_6d54e4b8` |
| every prerequisite stated by a prerequisite sentence in the blocked rule, state form, at the strength of its condition | ✓ **newly satisfied** — all five sentences narrowed to the single object the single write settles, verified verbatim and against each world |
| every computation: self-sufficient baseline, 4–6 factors, 2 `parameter` + 1 `method`, ≥1 multi-source and ≥1 cross-difficulty per task, ladders of 3 tiers stated in full | ✓ on counts and structure; 30/30 factors bear weight on their worlds; every whole-baseline fall-back definite and different from gold |
| every ladder's tiers distinct in outcome | ✓ **newly satisfied** — CG-2's three collapsed ladders rebuilt |
| every ladder's conditions and outcomes ones that line of business holds | ✓ **newly satisfied** — CG-6's two re-billing outcomes deleted; CG-7's unreachable clause removed |
| each factor's `effect` label honest | ✗ — **N-1**: `prior_accrual_netting` and `employer_pickup_base` |
| policy self-consistent; no undeclared override; no inherited clause left unimplemented | ✗ — **N-2**; CG-1, CG-3, CG-4, CG-5, CG-10, CG-11 all closed, nine `overwrite` entries all sound on all three parts, base verified byte-identical to the blueprint |
| proof texts assert only what recomputation confirms | ✗ — **R2-F-1** (task 0's third `edge_load_bearing` entry) |
| instantiation-stage gates re-run on the final form | ✓ below |

### gate re-run on the reworked form (2026-09-22)

```
EXTENDED OK          (extended_policies=6, cross-cat=4, task_tools=6, tasks=2)
TASK TOOL CONTRACT OK (6 tools)
SOLVABILITY OK       0.json / 1.json  True  3  3|4  22|29 True
COMPUTE OK           history_rows_max=48(>= 8)   branches_max=53(>= 5)
GROUNDING OK         0.json 2 3 3 9 True / 1.json 2 3 3 7 True
SCOPE OK             hard-fails=0
REPLAY OK            0.json 12 acts / 1.json 13 acts, det, nonvac, 0 errs, closure matches
```

Hashes on the final form: `meal.extended.yaml`
`13ceddd10d7e28c8ecedcfaceb019dcce92c53d5fcd3dd8ca97e4e34532f7c36`, `task_tools.py`
`2fd04d28ab652a00769f609c21c81ad0ef25697c575c7f6af2c09f1f32aaa250`, and each task's `frozen_time` /
`user_scenario` / `initial_state` byte-identical to the rebuilt masked views. All seven gates green — and
the three surviving defects are again ones no gate in this suite inspects: an `effect` label against the
charter's own usage, a settled quantity no write moves, and a proof sentence whose intermediates the
ladder contradicts.

### per-task verdicts (round 2)

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | SOURCE-POLICY RED (N-2) | SOURCE-CHAIN RED (R2-F-1) | SOURCE-FACTOR RED (N-1) | **PASS** |
| 1 | **PASS** | **PASS** | SOURCE-FACTOR RED (N-1) | **PASS** |

Both round-2 recomputations reproduced every gold figure — 19 of 19 on task 0, 23 of 23 on task 1,
including every `factor_sensitivity` and `baseline_result` — so no red light this round is an arithmetic
disagreement with GT.

### regression check

Nothing this audit closed in round 1 has regressed. Every round-1 item is dispositioned in
`## round_1_item_disposition` above; fourteen are closed, one lapsed, three carried forward unchanged as
observations, and two are closed with a residue recorded (N-4, N-6). The three surviving red lights are
all **new**: two introduced by the rework itself (N-1 by the CG-2/CG-5/CG-6 ladder rebuilds, R2-F-1 by the
sentence written to replace F-6's) and one (N-2) present in substance in round 1 but made explicit — and
so demonstrable — by the sentence added this round.

---

# revision_3

## charter_global_frozen (round 3)

- auditor: same; the text of `revision_1` and `revision_2` is untouched
- freeze time (charter-global section): 2026-09-22, before either task's round-3 GT was opened
- re-derivation grounds:

  | shared source | round 2 | round 3 | action |
  | --- | --- | --- | --- |
  | `meal.extended.yaml` | `13ceddd1…2f7c36` | `a8f898ff…ad9e88` | **CHANGED → re-derived in full** |
  | `task_tools.py` | `2fd04d28…aaa250` | `2fd04d28…aaa250` | **UNCHANGED (all three rounds) → `action_binding_and_uuids`, CG-8, CG-9 carried forward by reference** |
  | `0.masked.json` | `735e0725…15dc03` | `3e5fc56e…15dc03`* | **CHANGED → task 0 re-derived from scratch** |
  | `1.masked.json` | `8639fbba…a42982` | `8639fbba…a42982` | **UNCHANGED → task 1 is a stability check** |

  \* `3e5fc56e7c1985cd42f6da973e5c4150fdb2a34d94a38847bd3c38f62315dc03`, verified on disk.
- **not blind**, as in round 2; the round-3 figures were recomputed independently from the reworked charter
  and the rebuilt world and frozen before the GT was opened.
- **base frozen — verified independently.** All eight top-level sections of the base copy inside
  `meal.extended.yaml` are object-identical to `blueprint/products/meal.yaml`. The coordinator's
  `check_base_frozen` result is corroborated rather than accepted.

### what moved

| policy | changed keys |
| --- | --- |
| `meal_ext_period_recovery_amount` | — unchanged |
| `meal_ext_daily_allowance_grant` | — unchanged |
| `meal_ext_reinstatement_paydown` | `rule` (one sentence added) |
| `meal_ext_ticket_allowance_application` | `rule` (one sentence replaced) |
| `meal_ext_payroll_charge_consent` | `rule`, `overwrite`, `compute`, `compute_basis`, `baseline`, `factors` |
| `meal_ext_restriction_lift_balance` | everything but `subject` / `computes` / `target_tool` / `trigger` / `base_policy_refs` |

Task 0's world was rebuilt wholesale — 35 `meal_transactions` rows against 20 — so **every** history
aggregate in that task necessarily moved; its scored values are re-derived below rather than compared for
stability. Task 1's world is byte-identical to round 2.

### N-2 — closed, and the closure verified rather than accepted

The defect was that `arrears_carried_usd` was reduced by a stored-value quantity no write ever moved, so a
payment cleared the arrears while the employee kept the money. The root policy has been redesigned around
the one quantity that does move:

- the formula is now `result = RND(MX(0.0, balance_standing_usd − employer_pickup_usd), 2)`. Stored value
  appears nowhere in it; `value_loaded_1m` survives only as the **trigger** of a percentage uplift, never
  as an amount subtracted.
- the rule says so outright: "Nothing the employee holds as stored value is taken off the balance standing
  at reinstatement: stored value is spendable money of the employee's own, the charges awaiting recovery
  are met from pay, and the two are never set against each other by this restatement."
- **formula, tool field and ledger row agree.** On task 0's world the account's
  `payroll_arrears_usd` stands at 154.75 when the write is made and the write sets it to 123.71 — a
  movement of **31.04**, which is exactly `employer_pickup_usd`. `lift_meal_account_restriction_a306574a`
  books its `balance_adjustment` row at `round(abs(standing − carried), 2)` = **31.04**, and updates
  `status`, `restriction_start_date` and `payroll_arrears_usd` — every field the policy's own sentences
  claim to move, and no other. The employer's pickup is stated as "met from the employer's own funding
  rather than by the employee", so no employee-side movement is claimed. Nothing is left unrecorded.
- the task-1 instance is closed the other way, by restating the quantity instead of moving it: "No account
  is taken of the stored value the employee already holds … **The stored value taken into account is never
  moved from the account: it stays spendable, the meals it will meet are never charged to payroll, and
  that is why the charge carried is net of it.**" The binding is unchanged; what changed is that the rule
  now says why netting is not a movement. That is a complete answer to the finding as written.

**Does the root policy still compute something the business would do?** Yes, on its own terms: the balance
standing less the part the employer's dining programme picks up, where the pickup is a share of recent
charges, uplifted for the employee's own payment and for length of service. A residual naming tension is
recorded as **N3-3**.

**Do the prerequisite edges still bear weight now that the quantity has changed?** Yes — see
`0.md` `# revision_3 / problem_chain`; both edges into the root move the scored value (207.56 and 133.64
against a gold of 123.71), and the paydown edge's gate was correctly re-pointed from
`applied_from_value_usd` to `paydown_uplift_pct`, a binding that exists in the new compute. A weakening in
how that edge couples is recorded as **N3-2**.

### R2-F-1 — closed, and the class swept; the sweep spot-checked by recomputation

Round 2's defect was a proof sentence naming intermediates the ladder cannot produce. The claim this round
is that every counterfactual was produced by the harness before the prose was written. That claim is about
process, so it was tested the only way it can be — by recomputing the figures. **Eleven of eleven
independently reproduced**, intermediates included:

| field | assertion | recomputation |
| --- | --- | --- |
| `edge_load_bearing[0]` (T0) | paydown 150.00; `recoveries_remitted_1m` 0.00; twelve-month basis 238.60 vs 124.75 | 150.00 ✓ · 0.00 ✓ · 238.60 / 124.75 ✓ |
| `edge_load_bearing[1]` (T0) | `balance_standing_usd` 238.60 vs 154.75; pickup **unchanged** at 31.04; result 207.56 | 238.60 ✓ · 31.04 ✓ · **207.56** ✓ |
| `edge_load_bearing[2]` (T0) | `value_loaded_1m` 0.00; `paydown_uplift_pct` 8 → 0; `standing_share_pct` stays 12; `service_uplift_pct` stays 5; pickup 31.04 → 21.11; result 133.64 | every one ✓ — `RND(124.15 × 0.17, 2)` = 21.11, `154.75 − 21.11` = **133.64** |
| `flips_to_true_by` ×3 (T0) | 83.85 / 124.75 · 154.75 vs 238.60 · `value_loaded_1m` 134.16, uplift 8, pickup 21.11 → 31.04, result 133.64 → 123.71 | all ✓ |
| `order_uniqueness` (T0) | paydown 150.00 on the opening world; recovery **unchanged** at 83.85; reinstatement **coincides** at 123.71; stored value ends 168.40 vs 152.56 | all ✓ — and the coincidence is real and correctly explained (below) |
| `edge_load_bearing` ×2 + `order_uniqueness` (T1) | 19.00 vs 27.10 → 0.00 · 16.75 vs 23.10 → 57.65 | ✓ |

**The non-obvious `order_uniqueness` result is correct.** Under the swap the reinstatement figure genuinely
coincides at 123.71, because `paydown_uplift_pct` turns on `value_loaded_1m > 0` — the fact of a payment,
not its size — so a 150.00 load and a 134.16 load both select the 8 % rung. The orders are still
distinguishable: the scored argument of the user write differs (150.00 against 134.16) and the terminal
ledger differs (stored value 168.40 against 152.56). Recomputed independently: `18.40 + 150.00 = 168.40`,
`18.40 + 134.16 = 152.56`. The reworker reported an inconvenient result accurately instead of rounding it
into a cleaner claim, which is the behaviour the round-2 finding was asking for.

### N-1 — closed, and the reclassification is not label-shopping

Two factors moved from `parameter` to `method`:

| factor | rung 1 | rung 2 | fall-through | genuinely a method? |
| --- | --- | --- | --- | --- |
| `meal_ext_payroll_charge_consent.prior_accrual_netting` | `charges_3m` — a sum over three calendar months | `MX(0.0, charges_1m − recoveries_1m)` — a one-month sum net of that month's recovery | nothing | **yes** — different rows aggregated **and** a different expression |
| `meal_ext_restriction_lift_balance.employer_pickup_base` | `charges_accrued_1m` | `charges_accrued_3m` | nothing | **yes** — a window swap, which is exactly what this charter labels `method` in `charge_window_basis`, `recoverable_window_basis`, `measured_balance_basis` and `lot_window_basis` |

Neither is a different **rate** in one formula: no rung of either substitutes a figure into an unchanged
expression. **The change was not made to satisfy a count.** The per-policy floors held *before* the
reclassification and hold after it, so nothing was gained by moving the label:

| policy | before | after | floor (≥2 `parameter`, ≥1 `method`, 4–6 factors) |
| --- | --- | --- | --- |
| `meal_ext_payroll_charge_consent` | 5 par / 1 meth | **4 par / 2 meth** | ✓ both ways |
| `meal_ext_restriction_lift_balance` | 3 par / 1 meth | **3 par / 1 meth** (one `parameter` was deleted and one added, see below) | ✓ both ways |

Per-task floors re-checked on the reworked charter: every policy carries 4–6 factors; each task's
computations carry at least one multi-source factor and at least one cross-difficulty factor — task 0 now
three (`employer_programme_share` → cafe, `employer_pickup_base` → market, `standing_pickup_share` → cafe),
task 1 three. Both reclassified factors take "nothing" as their fall-through, which is their declared
`baseline`, as required.

`meal_ext_restriction_lift_balance`'s factor set was replaced again this round —
`value_application_basis` and `working_float_left` out (both read stored value, the quantity N-2 removed),
`standing_pickup_share`, `paydown_matching_uplift` and `length_of_service_uplift` in, with
`employer_pickup_base` retained and relabelled. Checked for the two deletion hazards: no surviving
`compute`, `bindings`, `inputs` or `compute_basis` entry references a deleted binding; `params` holds
exactly the seven keys the four surviving ladders use; the factor count is 4 and the labels 3/1.

### rule_compute_equivalence, prerequisite sentences, overrides (round 3)

Re-run in full over all six policies.

- **rule ↔ compute**: every binding carries a verbatim `compute_basis` quotation from its own rule, and the
  sweep back finds a binding for every rule sentence. **N-4 is closed**: the ticket policy's sentence now
  reads "No window limits which till transaction the ticket may be: the largest meal rung against payroll
  on the account is taken however long ago it was rung" — which is exactly what `MAX(…, transaction_code='meal_purchase', payment_channel='payroll_deduction')`
  does, with the unimplemented "that still carries none" clause removed. No rule sentence now promises what
  no binding delivers.
- **N-5 is closed**: `guest_surcharge_addition` rung 1 now reads "more guest meals … in the last three
  calendar months than **three times** the guest meal allowance printed against the plan, one month's
  allowance for each of those three months", and the compute is
  `guest_count_3m > P('guest_meals_per_month') * 3`. The three-month count is tested against a three-month
  allowance; the unit mismatch is gone.
- **N-3 is closed**: `meal_ext_restriction_lift_balance.baseline.rule` now defines every referent it uses —
  "The employer's dining programme picks up part of the balance standing, and that part is the base it
  picks up from taken at the share it picks up. The base … is nothing. The standing share … is nothing.
  The uplift … is nothing. The uplift … is nothing." — and yields a definite figure with no factor applied
  (the balance standing itself). `baseline.params` is `[]` and the baseline rule names no plan parameter,
  so the keys agree.
- **prerequisite sentences**: all five `policy_source` strings are verbatim in the blocked policy's own
  rule, absent from the depended-on rule, state-form, tool-free and id-free; every `gate` names a binding
  that exists in that policy's compute (`paydown_uplift_pct` newly, in place of the deleted
  `applied_from_value_usd`); every `resolved_by` is the depended-on policy's `target_tool`; the graph is
  the same two acyclic components. Verified mechanically and by reading.
- **overrides**: nine `overwrite` entries; all nine pass verbatim-in-base, verbatim-in-extending-rule and
  base-policy-in-`base_policy_refs`. The two rewritten `replaced_by` strings
  (`meal_ext_restriction_lift_balance`, `meal_ext_payroll_charge_consent`) match their policies' new result
  sentences.

### findings (round 3)

No red light. Three observations.

---

#### N3-1 — observation — a tree-A policy states how a guest meal accrues to payroll, a subject it does not cite

`meal_ext_reinstatement_paydown`'s rule gains: "A guest meal is charged to payroll net of the guest
surcharge printed against the plan, so that surcharge stands to be settled by the employee rather than
recovered from their pay." The seed follows it — task 0's guest meals of 24.60 and 22.70 accrue at 20.10
and 18.20, each net of the plan's 4.50 surcharge — and the sentence does real work: it is what makes the
paydown's `guest_surcharge_due_usd` of 9.00 non-duplicative, answering round-1 **F-4** head on.

Two things sit awkwardly, neither with a demonstrable consequence:
- base's `meal_purchase_posted` event declares `triggers: [{event: meal:meal_charge_accrued, when: {payment_channel: payroll_deduction}, map: {… amount_usd: amount_usd …}}]`,
  i.e. the accrual carries the meal's own amount. The seed carries the meal net of the surcharge.
- the base **policy** that governs accrual, `meal_payroll_recovery_terms`, is named and superseded on this
  point in `meal_ext_payroll_charge_consent.overwrite` — a **tree B** policy — while the sentence asserting
  the variation sits in a **tree A** policy whose `base_policy_refs` are `meal_load_and_refund_terms` and
  `meal_restriction_terms`, neither of which governs accrual.

Recorded as an observation rather than a red light, on the same standard applied to CG-10 and CG-11 in
round 1: no scored value differs for a solving agent, because the accrual rows are facts it reads off the
ledger rather than a quantity it computes, and task 1 — whose scope owns the accrual subject — has no
payroll-tendered guest meal. Affects `meal.extended.yaml`
`meal_ext_reinstatement_paydown.rule` and `tasks/0.json` `initial_state.meal_transactions`.

---

#### N3-2 — observation — the root now reads the fact of the paydown, not its amount

The lift → paydown edge's gate moved from `applied_from_value_usd` (which carried the paydown's magnitude
into the root) to `paydown_uplift_pct`, whose compute is
`K('matched_paydown_uplift_pct') if (value_loaded_1m > 0 and restriction_days_standing > P('arrears_restriction_grace_days')) else …`.
The binding's value does change when the write lands (0 → 8), so the edge is a genuine `value_input` and it
bears weight (133.64 against a gold of 123.71). But the root is now insensitive to **how much** the
employee pays: a 134.16 load and a 150.00 load both select the 8 % rung and both give 123.71, which is
precisely why `order_uniqueness` has to fall back on the terminal ledger. The paydown's own five-factor
computation is therefore load-bearing as its own scored parameter and not as an input to the root.
Recorded because it is a real weakening of the tree's coupling against round 2, not because a floor is
breached: the task carries three `value_input` edges against a floor of one, and the two edges into
`meal_ext_period_recovery_amount` still carry magnitude. Affects
`meal_ext_restriction_lift_balance.prerequisite[1]` and `compute.paydown_uplift_pct`.

---

#### N3-3 — observation — a "paydown" that pays nothing down

Base `meal_restriction_terms` says the restriction lifts "once the employee has **paid down** at least the
share of the **outstanding arrears**"; that sentence is named and superseded in
`meal_ext_reinstatement_paydown.overwrite`, replaced by "A restriction is lifted once the employee has
**paid in** at least the paydown worked out here". After this round's redesign the money paid in reduces no
arrears at all: it lands as stored value the employee keeps and spends, and its only effect on what they
owe is an 8-point uplift in the employer's pickup. The charter is self-consistent about this — the override
is declared, and the lift rule states the separation of the two pockets outright — and the arrangement is
one a prepaid operator could publish, so it is not a red light. Recorded because the quantity's name and
the base language it replaces both still say "pay down arrears", which is not what it now does. Affects
`meal_ext_reinstatement_paydown` (`computes: paydown_amount_usd`).

---

#### carried forward unchanged

- **CG-8**, **CG-9** — `task_tools.py` is byte-identical across all three rounds; both stand as recorded in
  `revision_1`. CG-9's disambiguation remains sound: the waited-on state names a payroll period and the
  lift's `balance_adjustment` row carries `pay_period=""`.
- **CG-14** — the cross-category rows still carry the employee's `customer_id` in both tasks; confirmed
  unchanged and not re-litigated, as the accepted runtime-layer constraint.

## revision_2_item_disposition

| item | round-2 verdict | claim | this audit's finding |
| --- | --- | --- | --- |
| N-2 | SOURCE-POLICY RED | closed by redesign | **CLOSED** — stored value removed from the root formula; the arrears movement equals the employer pickup exactly, and the tool books that same figure. Task-1 instance closed by restating the netting as "taken into account … never moved" |
| R2-F-1 | SOURCE-CHAIN RED | closed, class swept | **CLOSED** — 11 of 11 counterfactual figures and intermediates reproduced, including the non-obvious `order_uniqueness` coincidence |
| N-1 | SOURCE-FACTOR RED | closed by reclassification | **CLOSED** — both rungs of each factor select a different way of arriving at the quantity, not a different rate; floors held before and after, so the move was not count-driven |
| N-6 | observation | closed by repair | **CLOSED** — zero dangling `original_pos_reference` in either task; every payroll-tendered meal in task 0 now carries its accrual |
| N-4 | observation | closed | **CLOSED** — the unimplemented clause removed; rule and compute now agree |
| N-3 | observation | closed | **CLOSED** — every referent of the baseline rule is defined in it |
| N-5 | observation | closed | **CLOSED** — a three-month count against a three-month allowance |
| CG-8, CG-9 | observations | no change | unchanged, as claimed |
| CG-14 | observation | accepted | unchanged, as claimed; not re-litigated |
| new | — | — | **N3-1**, **N3-2**, **N3-3** — observations, no red light |


## closing_checklist (round 3)

**This difficulty closes out.** All four relationships hold on both tasks, so the source-layer audit passes.

| item | state |
| --- | --- |
| per-task audit files one-to-one with the tasks; old revisions traceable | ✓ `revision_1` and `revision_2` untouched; `revision_3` appended to all three files |
| every comparison section carries a PASS | ✓ — `0.md` and `1.md` both carry PASS on all four relationships |
| extended policies fully covered; scopes pairwise disjoint, each spanning its whole tree | ✓ six policies, three per task; both `charter_scope` blocks match the trees derived this round |
| task tools and GT closed; each uuid8 independently generated and frozen | ✓ `task_tools.py` byte-identical across all three rounds |
| every tree: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 `owner=user` write, no cycle; the difficulty's edges together a DAG | ✓ task 0: n=2, 3 edges, `load_arrears_paydown_ff1c695b`; task 1: n=2, 2 edges, `confirm_payroll_charge_accrual_6d54e4b8`; two disjoint acyclic components |
| every prerequisite stated by a prerequisite sentence in the blocked rule, state form, at the strength of its condition | ✓ all five verified verbatim and against both worlds; each false at the opening and true after the one prescribed write |
| every computation: self-sufficient baseline, 4–6 factors, ≥2 `parameter` + ≥1 `method`, ≥1 multi-source and ≥1 cross-difficulty per task, ladders of three tiers stated in full | ✓ 30 factors; task 0 carries three cross-difficulty factors, task 1 three |
| every ladder's tiers distinct in outcome; conditions and outcomes ones the business holds | ✓ |
| each factor's `effect` label honest | ✓ **newly satisfied** — both reclassifications verified as genuine method choices, not label-shopping |
| every factor bears weight against an honest baseline; the baseline alone gives a definite number different from gold | ✓ 30/30; whole-baseline fall-backs 125.00 · 77.38 · 154.75 · 9.50 · 9.50 · 116.50 against golds 83.85 · 134.16 · 123.71 · 8.10 · 6.35 · 51.30 |
| policy self-consistent; no undeclared override; base frozen | ✓ nine `overwrite` entries all sound on all three parts; base verified object-identical to `blueprint/products/meal.yaml` |
| every write's stated effect matches the movement it makes | ✓ **newly satisfied** — see `### N-2 — closed` |
| proof texts assert only what recomputation confirms | ✓ **newly satisfied** — 11 of 11 counterfactual figures and intermediates reproduced |
| instantiation-stage gates re-run on the final form | ✓ below |

### gate re-run on the round-3 form (2026-09-22)

```
EXTENDED OK · TASK TOOL CONTRACT OK · SOLVABILITY OK · COMPUTE OK · GROUNDING OK · SCOPE OK
REPLAY OK    0.json 12 acts, det, nonvac, 0 errs, closure 39/39 match
             1.json 13 acts, det, nonvac, 0 errs, closure 34/34 match
```

Hashes on the final form: `meal.extended.yaml`
`a8f898ffaa1e6a3c7b3023702d73669535d01a6ee34a9eaffcfbba5a31ad9e88`, `task_tools.py`
`2fd04d28ab652a00769f609c21c81ad0ef25697c575c7f6af2c09f1f32aaa250`; each task's `frozen_time` /
`user_scenario` / `initial_state` byte-identical to the rebuilt masked views; the base section
object-identical to the blueprint.

### per-task verdicts (round 3)

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | **PASS** | **PASS** | **PASS** | **PASS** |
| 1 | **PASS** | **PASS** | **PASS** | **PASS** |

Both recomputations reproduced every gold figure — 19 of 19 on task 0 (re-derived from scratch on a
rebuilt world) and 23 of 23 on task 1 (unchanged world, edited charter) — including every
`factor_sensitivity` and `baseline_result`.

### regression check

Nothing closed in rounds 1 or 2 has regressed. Every revision_2 item is dispositioned in
`## revision_2_item_disposition`: seven closed, two carried forward unchanged as observations, one
accepted upstream. Round-1 items closed in round 2 were re-tested where the charter or the world moved —
CG-2's rebuilt ladders, CG-3's narrowed sentences, CG-4's override, CG-7's reachable fall-through, CG-13's
"meals of the employee's own", CG-15's pointers and CG-16's payroll cycle all still hold on the round-3
artifacts, and CG-5/CG-6's deleted material has not returned in any form. Task 1's figures came through a
charter edit entirely unchanged.

### trajectory across the three rounds

| round | red lights | relationships failing (of 8) |
| --- | --- | --- |
| 1 | 12 across both tasks | 8 |
| 2 | 3 | 4 |
| 3 | **0** | **0** |

Three observations remain on record — **N3-1** (a tree-A rule sentence about a tree-B subject), **N3-2**
(the root reads the fact of the paydown, not its size) and **N3-3** (a "paydown" that pays nothing down) —
together with the carried-forward CG-8, CG-9 and the accepted CG-14. None demonstrates a consequence under
any of the four relationships, so none is grounds for rework.

---

# revision_4

## charter_global_frozen (round 4)

- auditor: same; the text of `revision_1` … `revision_3` is untouched
- freeze time: 2026-09-22, before either task's round-4 GT was opened
- re-derivation grounds:

  | shared source | round 3 | round 4 | action |
  | --- | --- | --- | --- |
  | `meal.extended.yaml` | `a8f898ff…ad9e88` | `5e5926ed…cb4e64` | **CHANGED → re-derived** |
  | `task_tools.py` | `2fd04d28…aaa250` | `2fd04d28…aaa250` | UNCHANGED in all four rounds |
  | `0.masked.json` | `3e5fc56e…15dc03` | `3e5fc56e…15dc03` | **UNCHANGED** — verified on disk |
  | `1.masked.json` | `8639fbba…a42982` | `8639fbba…a42982` | **UNCHANGED** — verified on disk |

- base frozen: all eight top-level sections of the base copy are object-identical to
  `blueprint/products/meal.yaml`. Verified independently, as in rounds 2 and 3.
- scope of this round: the single item **N-e**, returned from the render layer. Everything the render-layer
  auditor endorsed as settled is left alone.

### what moved

Exactly five keys on each of the six extended policies: `temporal_basis` (new), `rule`, `baseline.rule`,
`compute_basis`, `factors`. Verified object-identical across the round: `compute`, `params`, `inputs`,
`cross_category`, `prerequisite`, `overwrite`, `subject`, `computes`, `target_tool`, `trigger`,
`base_policy_refs` — **all six policies, every one of those keys**. No extended policy has an
`eligibility` key, before or after. **No eligibility and no gate moved**, and because `compute` and
`params` are byte-identical, no figure *can* have moved; that is a structural fact, not an observation
about this world.

### N-e — the openness was real and outcome-determining; confirmed before checking the fix

Before judging the repair I reproduced the premise on both worlds. Taking the two factors whose tier turns
on a month window and reading that window three ways:

| task / factor | trailing window from the clock | completed named month(s) | current named month(s) |
| --- | --- | --- | --- |
| **1** / `grant_period_ceiling_band` (NOW 2026-06-11) | applications 2, meals 5 → **rung 1, heavy 150 %** | May 2026: applications 0, meals 2 → **fall-through, 100 %** | June 2026: applications 2, meals 3 → **fall-through, 100 %** |
| **0** / `short_tender_deferral` (NOW 2026-03-17) | overdrafts 2 → **rung 1, deep 45.00** | Dec–Feb: overdrafts 1 → **rung 2, light 20.00** | Jan–Mar: overdrafts 2 → rung 1 |

Three readings, three different ceilings on task 1 and two different deferral amounts on task 0 — each
feeding straight into a scored value. The render-layer auditor's classification was right: this was a
unique-entailment defect, not a documentation note, and it belonged at the source layer.

### N-e — the repair, checked face by face

**The qualifier.** Every window phrase now names its own anchor: "the calendar month **running back from
the day the account is worked**", "the three calendar months running back from the day the account is
worked", and so on. Swept mechanically over every face of all six policies — `rule`, `baseline.rule`,
every `compute_basis` value, and every `ladder[].when` and `ladder[].value`/`method`:

- **226 occurrences** of the qualifier across the six policies (30 · 64 · 30 · 39 · 33 · 30);
- **zero** remaining unqualified window phrases ("the last calendar month", "the last two/three/twelve
  calendar months", "in the last month") in any face of any policy.

On the two worlds the qualifier admits only the trailing reading, so both rows of the table above collapse
to their first column. **The ambiguity is gone where it mattered.**

**The `temporal_basis` blocks.** Six added, one per extended policy, all carrying the same eight keys —
`clock`, `anchor_event`, `anchor_source`, `relation`, `duration_source`, `unit`, `counting_rule`,
`boundary` — which is **exactly** the key set of the two base time eligibilities
(`meal_load_and_refund_terms / refund_window` and `meal_leave_and_closure_terms / balance_return_window`).
Contents checked against each policy's own prose: `anchor_source: frozen_time` matches every window's use
of `NOW` in compute and "the day the account is worked" in the rule; `unit: calendar_months` matches;
`boundary: exclusive` matches the sentence's "an entry exactly that many whole months old falls outside
it". No block contradicts its policy's prose. Two shape notes are recorded as **N4-2**.

**Placement of the counting rule.** The sentence is identical across all six policies and appears in both
`rule` and `baseline.rule` of each. That placement is right: `baseline.rule` is what the computation
document must be derivable from on its own, and a reader who reaches only that document still needs the
window basis to compute a definite number — without it the baseline is not self-sufficient, which is the
standard round 3 applied to N-3. Putting it in `rule` as well gives the hub the same locator. It says
nothing a business would not publish: it fixes an anchor and a boundary in the words tills and ledgers
use, names no table, no tool and no code token, and carries no arithmetic notation.

### N-e — is the published basis what the scorer actually does?

This is the claim that matters, and it was tested by recomputation rather than accepted.

The authoritative arithmetic is `skills/erl-task-instantiate/scripts/check_compute.py`: a row is in an
N-month window iff `0 <= MONTHS(d, NOW) < N`, where
`MONTHS(d1,d2) = (y2−y1)*12 + (m2−m1)`, less one when `day2 < day1`. `erlbench/` carries no month
arithmetic of its own, so that function is the whole of it.

The published sentence — "an entry falls inside such a window while fewer than that many whole months have
gone by since the day it was booked, a whole month going by only when the same day of the month comes round
again, so an entry exactly that many whole months old falls outside it, and an entry booked after the day
the account is worked falls outside it too" — was implemented twice, under the two readings its words
admit, and both were compared against the harness:

| | domain | mismatches |
| --- | --- | --- |
| **reading B** — a missing day-of-month (a 31st in a 30-day month) counts when the month's last day passes | 802 dates within 400 days before each of the two clocks | **0** |
| **reading A** — a day that does not exist in a month simply never comes round | same 802 dates | **29** (all day-of-month 29–31) |
| reading B | 392,641 exhaustive (row-date, clock) pairs, every day over 2½ years | 188 (0.048 %) |
| reading A | same | 5,010 (1.28 %) |

Two conclusions, stated separately because they are different:

1. **The reworker's claim is reproduced within the domain it was made for.** Anchored at this difficulty's
   two clocks, reading B matches the harness on every one of the 802 dates — zero mismatches, consistent
   with the reported sweep. And on the rows that actually exist: **33 seeded dates in task 0 and 25 in
   task 1, at every window length the charter uses (1, 2, 3, 12 months), produce not one membership
   disagreement under either reading.** The published basis and the scored figures agree everywhere they
   meet. That is what unique entailment requires, and it holds.
2. **The sentence is not a universal statement of the harness.** Both readings part from it at
   month-length boundaries, and they part from each other on 29 dates within 400 days of these clocks.
   The harness's rule is neither convention: it is the calendar-month difference reduced by one when the
   day of the month has not been reached, which at a 31st-to-February boundary matches neither "the day
   came round" nor "the day never came round". Not reachable here — both clocks fall on the 17th and the
   11th, and no seeded row is dated later than the 31st in a month that lacks it — so it is recorded as
   observation **N4-1** rather than as a red light. Had it been reachable, the policy would be publishing
   a rule the scoring does not follow, which is the worse failure the brief names.

### other charter-global checks (round 4)

- **prerequisite sentences**: none contained a window phrase, so all five are untouched; re-verified all
  the same — `policy_source` verbatim in the blocked rule, absent from the depended-on rule, state form,
  `gate` a real binding, `resolved_by` the depended-on `target_tool`. Unchanged.
- **overrides**: the nine `overwrite` entries are object-identical to round 3 and still verify on all three
  parts (clause verbatim in base, replacement verbatim in the extending rule, base policy in
  `base_policy_refs`).
- **factors**: counts, labels, `decides`, `bindings` and `baseline` bindings are unchanged; only the
  `ladder` prose moved. Every per-policy floor (4–6 factors, ≥2 `parameter`, ≥1 `method`) and every
  per-task floor (≥1 multi-source, ≥1 cross-difficulty) holds as in round 3.
- **rule ↔ compute**: re-swept; every binding still carries a verbatim `compute_basis` quotation from its
  own rule, and no rule sentence promises what no binding delivers. The counting-rule sentence is a basis
  statement rather than a quantity, so it introduces no unmatched promise.

### findings (round 4)

No red light. Two observations.

---

#### N4-1 — observation — the counting sentence is faithful on these worlds but is not the harness's rule in general

Set out in full under `### N-e — is the published basis what the scorer actually does?` above. In short:
the sentence admits two readings; one matches the harness on every date within 400 days of both clocks and
on every seeded row at every window the charter uses, the other diverges on 29 such dates; and neither
matches the harness universally, because the harness's rule is the calendar-month difference reduced by
one when the day of the month has not been reached. Nothing on either world reaches the divergence — both
clocks fall on a day-of-month that exists in every month, so no window edge lands on a 29th, 30th or 31st.
Recorded so that a later difficulty whose `frozen_time` falls on the 29th to the 31st, or whose ledger
carries such dates near a window edge, is checked against this rather than assuming the sentence settles
it. Affects the `counting_rule` of all six extended policies.

---

#### N4-2 — observation — two fields of the new `temporal_basis` blocks do not carry what the base shape carries

- `duration_source` reads "the window of calendar months named in the sentence that uses it", where the two
  base eligibilities name a locatable field (`variants.refund_request_window_days`,
  `variants.balance_return_window_days`). That is honest — each sentence names its own 1, 2, 3 or 12
  months, and no single field holds them — but it means this `duration_source` cannot be resolved
  mechanically the way the base's can.
- `relation: not_before` with `boundary: exclusive` fixes only the far edge of what is a two-sided window;
  the near edge ("an entry booked after the day the account is worked falls outside it too") lives in the
  `counting_rule` prose alone. The base blocks describe one-sided deadlines, where one relation suffices.
  The prose carries the whole statement and the prose is what the KB publishes, so nothing is lost to a
  reader; recorded because the structured face is narrower than the sentence it accompanies.

Neither affects any scored value, any tier or any gate.

---

#### also confirmed unchanged

The day-count windows in these policies — the 45-day recovery recency window, the 90-day recent-load
window, the grace-day comparisons and the 24-month service term — are **not** covered by the new
`temporal_basis`, whose `unit` is `calendar_months`. They fall back on the base charter's calendar-day
convention ("counted as calendar days from the day after …, every day of the week counts, and a request
arriving on the boundary day itself is still in time"), which is stated twice in the base section and
inherited. Checked for reachable ambiguity on both worlds: the thinnest margin is task 0's
`restriction_days_standing` = 21 against the `2 × grace days` = 20 threshold of `measured_balance_basis`.
Counting from the day after the restriction began, as the base convention directs, gives 21; the only
reading that gives 20 excludes both endpoints, which is not how elapsed time is counted anywhere in this
charter. The other margins are wide (39 against 45, 56 against 90, 21 against 10, 34 months against 24).
No second reading is reachable, so no finding is raised — recorded because the round-4 fix covers months
and not days.

**CG-8**, **CG-9**, **CG-14**, **N3-1**, **N3-2**, **N3-3** — carried forward unchanged; `task_tools.py`
is byte-identical across all four rounds and neither world moved.

## revision_3_item_disposition

| item | claim | this audit's finding |
| --- | --- | --- |
| N-e | closed at source | **CLOSED** — the openness was real and outcome-determining on both worlds; the qualifier removes it (226 occurrences, zero unqualified phrases left); the `temporal_basis` blocks match the base key shape and contradict no prose; the counting sentence is faithful to the harness on every date and window either world reaches. Residual recorded as **N4-1**, not reachable here |
| every face swept | — | **CONFIRMED** independently over all six policies' `rule`, `baseline.rule`, `compute_basis` and ladder strings |
| prerequisite sentences untouched; nine overwrites still verify | — | **CONFIRMED** — object-identical and re-verified on all three parts |
| no eligibility or gate moved | — | **CONFIRMED** — `compute`, `params`, `inputs`, `cross_category`, `prerequisite`, `overwrite` object-identical on all six |
| every figure re-derived and none moved | — | **CONFIRMED** by recomputation, and structurally guaranteed: `compute` and `params` are byte-identical |
| new | — | **N4-1**, **N4-2** — observations, no red light |


## closing_checklist (round 4)

**This difficulty closes out again.** All four relationships hold on both tasks, and the one item returned
from the render layer is closed.

| item | state |
| --- | --- |
| per-task audit files one-to-one with the tasks; old revisions traceable | ✓ `revision_1` … `revision_3` untouched; `revision_4` appended to all three files |
| every comparison section carries a PASS | ✓ both tasks, all four relationships |
| **N-e closed at source, and the closure verified rather than accepted** | ✓ the openness reproduced first (two factors, three readings, different tiers on both worlds), then shown removed: 226 qualifier occurrences, **zero** unqualified window phrases in any face of any policy, and **zero** in either task file |
| the published basis is what the scorer does | ✓ on every date and window either world reaches — 33 and 25 seeded dates at N ∈ {1, 2, 3, 12}, zero membership disagreements under either reading of the sentence; 802 dates within 400 days of the two clocks, zero mismatches against the harness under reading B. General residue recorded as **N4-1** |
| the counting rule is well placed, faithful in business words, and publishable | ✓ in both `rule` and `baseline.rule` of all six, which is what keeps the computation document self-sufficient; names no table, tool or code token; states nothing a business would not publish |
| `temporal_basis` matches the base shape, contradicts no prose, moves no eligibility or gate | ✓ same eight keys as the two base time eligibilities; contents agree with each policy's own sentences; no extended policy has an `eligibility` key and none gained one. Two shape notes as **N4-2** |
| nothing else moved | ✓ `compute`, `params`, `inputs`, `cross_category`, `prerequisite`, `overwrite`, `subject`, `computes`, `target_tool`, `base_policy_refs` object-identical on all six policies; both worlds byte-identical |
| prerequisite sentences and overrides | ✓ five sentences untouched and re-verified; nine `overwrite` entries object-identical and still sound on all three parts |
| factors | ✓ 30 factors, counts and labels unchanged, every per-policy and per-task floor holding; all 30 `tier_taken` strings in the task files match a ladder `when` string **exactly**, 30/30 |
| every figure | ✓ recomputed end to end and **none moved** — which is structurally guaranteed here, since `compute` and `params` are byte-identical, and is therefore confirmation rather than evidence |
| instantiation-stage gates re-run on the final form | ✓ below |

### gate re-run on the round-4 form (2026-09-22)

```
EXTENDED OK · TASK TOOL CONTRACT OK · SOLVABILITY OK · COMPUTE OK · GROUNDING OK · SCOPE OK
REPLAY OK    0.json 12 acts, closure 39/39 match · 1.json 13 acts, closure 34/34 match
```

Hashes on the final form: `meal.extended.yaml`
`5e5926ed5ca38e264189e6978eb8067d855e79d538b98c3fa27e33f4b2cb4e64`, `task_tools.py`
`2fd04d28ab652a00769f609c21c81ad0ef25697c575c7f6af2c09f1f32aaa250`; both masked views byte-identical to
round 3; the base section object-identical to the blueprint.

### per-task verdicts (round 4)

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | **PASS** | **PASS** | **PASS** | **PASS** |
| 1 | **PASS** | **PASS** | **PASS** | **PASS** |

### regression check

Nothing regressed. Both worlds are byte-identical to round 3 and every computational face of the charter
is object-identical, so every figure closed in round 3 came through unchanged — 19 of 19 on task 0 and 23
of 23 on task 1, plus all five edge-skip figures and the swapped-order set. The items closed in rounds 1
to 3 were re-tested where this round's edit could have touched them: the five prerequisite sentences
(CG-3, round 2) contained no window phrase and are untouched; the nine `overwrite` entries (CG-4, CG-5,
CG-10, CG-11) still verify on all three parts; the ladders rebuilt for CG-2 and reclassified for N-1 kept
their outcomes and labels through the rewording; N-2's redesigned root formula is untouched; and the
counterfactual prose swept for R2-F-1 still reproduces figure for figure.

### trajectory across the four rounds

| round | red lights | relationships failing (of 8) |
| --- | --- | --- |
| 1 | 12 | 8 |
| 2 | 3 | 4 |
| 3 | 0 | 0 |
| 4 (one item returned from the render layer) | **0** | **0** |

Observations on record, none grounds for rework: **N4-1**, **N4-2** (this round), **N3-1**, **N3-2**,
**N3-3** (round 3), **CG-8**, **CG-9** (round 1, tool module unchanged throughout) and the accepted
**CG-14**. The round-4 item is a useful precedent: a gap that every source-layer gate passed and that this
audit had not caught in three rounds was found by a downstream auditor reading the published sentences,
and it was a genuine unique-entailment defect rather than a matter of documentation.
