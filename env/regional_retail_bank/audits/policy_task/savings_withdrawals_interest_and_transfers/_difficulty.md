# Policy-task audit — savings_withdrawals_interest_and_transfers / charter-global

## charter_global_frozen

- Freeze time: 2026-09-16 09:09 UTC (pre-reveal; nothing in this section is derived from any revealed GT field).
- Auditor: independent policy-task auditor (not the instantiating agent).
- Frozen inputs and their hashes:
  - `env/regional_retail_bank/tasks/savings_withdrawals_interest_and_transfers/savings.extended.yaml`
    sha256 `d1aa0ebcdaf57935623dd8a05a59c874be8945a9b94aab9817fc7cca05b99726`
  - `env/regional_retail_bank/tasks/savings_withdrawals_interest_and_transfers/task_tools.py`
    sha256 `9a91e7f72082afd6aab91cad3024b4cb3fde18bbd83b0b0a453a33040050662a`
- Fields permitted for this section: the whole extended charter (`base` copy, `extended_policies` with
  `rule`, `compute_basis`, `compute`, `overwrite`, `prerequisite`, `factors`, `baseline`, `params`,
  `inputs`, `cross_category`), `task_tools.py` in full, `blueprint/products/savings.yaml`,
  `blueprint/products/{checking,card,cd}.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`,
  and the compute-expression semantics fixed by `skills/erl-task-instantiate/scripts/check_compute.py`.
- Fields explicitly masked and not read while this section was written: every task's
  `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`,
  `solvability_contract`, `prerequisite_closure`, `db_closure`, `db_closure_matches_initial_state`.
- **Relation to the previous revision.** The version of these three files committed at `33d2693` audits a
  **superseded charter**: it records `savings.extended.yaml` = `26300564d03f2e7a00b63b752049cc3c2fba64211efe4d90eee2cf947e9fd163`
  and `task_tools.py` = `0dcd69b75a2da73abf72b39f783f7027648136094347479a1eac25045f9fff46`, and it names six
  extended policies (`savings_ext_certificate_proceeds_transfer`,
  `savings_ext_counted_withdrawal_fee_assessment`, `savings_ext_linked_waiver_maintenance_refund`,
  `savings_ext_certificate_funding_fee_refund`, `savings_ext_best_money_market_conversion`,
  `savings_ext_overdraft_replenishment_transfer`) of which **none** exists in the artifacts audited here.
  Both frozen inputs have therefore changed, so every charter-global section is re-derived in full rather
  than carried forward by reference. The old text was already absent from the working tree when this audit
  began — it was not removed by this auditor — and remains recoverable at
  `git show 33d2693:env/regional_retail_bank/audits/policy_task/savings_withdrawals_interest_and_transfers/_difficulty.md`.
  This audit is revision 1 against the current artifacts; its findings are not comparable item-by-item with
  the superseded ones, because they concern different policies.
- Entry condition: the instantiation gate snapshot supplied with the brief (EXTENDED, TASK-TOOL-CONTRACT,
  REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE — all green) is cited, not re-run.
  `check_traceability.py` is legitimately deferred to the render stage. Input is complete.

### policy_conflict_scan

The base section of `savings.extended.yaml` is byte-for-byte identical to
`blueprint/products/savings.yaml` on every top-level key (`category`, `display_name`, `binding`,
`lifecycle`, `accounts`, `parameter_schema`, `variants`, `events`, `measures`, `policies`) — verified by
canonical-JSON comparison. The base copy has not been rewritten.

Six extended policies, six distinct `target_tool`s, six distinct `computes` names. Overlapping subjects
were checked pairwise:

| subject | policies | verdict |
| --- | --- | --- |
| `savings_interest_credit` | `savings_ext_promotional_interest_correction` (`interest_component=promotional`), `savings_ext_relationship_bonus_correction` (`interest_component=relationship_bonus`) | compatible — the tool bodies stamp different `interest_component`, and each policy deducts only credits of its own component |
| `savings_fee_refund` | `savings_ext_periodic_fee_courtesy_credit` (`adjustment_reason=courtesy_waiver`, booked against the most recent monthly maintenance fee), `savings_ext_excess_fee_review_credit` (`adjustment_reason=bank_error`, booked against the most recent excess withdrawal fee) | compatible — disjoint `adjustment_reason` and disjoint anchor fee |
| `savings_set_automatic_transfer` | `savings_ext_standing_transfer_amount` alone | no overlap |
| `savings_withdrawal` | `savings_ext_surplus_transfer_amount` alone | no overlap |

Triggers, time anchors and cross-category read boundaries are consistent: every policy anchors on
`NOW` = `frozen_time`, every cross-category read is declared in `cross_category` and in `inputs`, and the
categories read (`checking`, `card`, `cd`) all have a blueprint product file.

Claimed scopes of the M tasks, taken as whole problem trees:

- task 0 — `savings_ext_standing_transfer_amount` (root) + `savings_ext_relationship_bonus_correction`
  + `savings_ext_periodic_fee_courtesy_credit` + `savings_ext_promotional_interest_correction`
- task 1 — `savings_ext_surplus_transfer_amount` (root) + `savings_ext_excess_fee_review_credit`

Pairwise disjoint, and jointly they cover all six extended policies. PASS.

One conflict was found and it is real; it is recorded under `override_declarations` as **CG-4**.

### rule_compute_equivalence

Check 2 was run over all six policies: every `compute` binding name has an entry in `compute_basis`, and
every `compute_basis` value is a verbatim substring of that policy's `rule` (mechanically verified). The
sweep back — does every `rule` sentence have an implementation, and does `compute` invent nothing — turned
up three non-equivalences.

**CG-1 — "rounded half up to the whole dollar" is implemented two incompatible ways in the same charter,
and neither of the two is half-up rounding.** `SOURCE-POLICY RED`.

The identical rule phrase appears as the top tier of four rounding factors and is compiled two ways:

| policy | rule sentence | compute |
| --- | --- | --- |
| `savings_ext_promotional_interest_correction` | "the interest owed is rounded half up to the whole dollar" | `RND(raw_shortfall + 0.5, 0)` |
| `savings_ext_periodic_fee_courtesy_credit` | "the courtesy credit is rounded half up to the whole dollar" | `RND(raw_courtesy_credit + 0.5, 0)` |
| `savings_ext_standing_transfer_amount` | "the instalment is rounded half up to the whole dollar" | `RND(paced_instalment, 0)` |
| `savings_ext_surplus_transfer_amount` | "the amount moved is rounded half up to the whole dollar" | `RND(offset_surplus, 0)` |

`RND` is fixed by the runtime as `lambda x, n=2: round(float(x), n)`
(`skills/erl-task-instantiate/scripts/check_compute.py:381`). Half-up rounding of `x` to the whole dollar
is `floor(x + 0.5)`. The first two policies compute `round(x + 0.5)`, which equals `floor(x + 0.5) + 1`
for every `x` whose cents part lies strictly between 0.01 and 0.49 — i.e. on roughly half the domain the
compute is one dollar higher than the sentence it is said to implement. The defect does not depend on how
`RND` breaks ties: for any tie convention, `RND(14.1029 + 0.5, 0)` is 15 while half-up to the whole dollar
of 14.1029 is 14.

At most one of the two implementations can be the stated rule, and the first two are not. Two documents
rendered from this charter will carry the same English sentence and licence two different numbers.

Demonstrated consequence: both of task 0's affected computations land on this tier, giving two defensible
scored values for each. See
`env/regional_retail_bank/audits/policy_task/savings_withdrawals_interest_and_transfers/0.md`,
`### policy_self_consistency (this task only)`. Task 1 lands on `RND(x, 0)` at `rounded_amount` with
`offset_surplus = 16530.095`, where both readings agree, so the defect is latent there.

Affected artifact: `savings.extended.yaml`, `savings_ext_promotional_interest_correction.compute`
binding `rounded_shortfall`; `savings_ext_periodic_fee_courtesy_credit.compute` binding
`rounded_courtesy_credit`.

**CG-2 — `savings_ext_relationship_bonus_correction` defines the bonus balance basis twice, nets
withdrawals twice in its fall-through, and states a top tier its own compute contradicts.**
`SOURCE-POLICY RED`.

Two sentences of the same `rule` define the same named quantity:

> "the bonus balance basis, which is the account's posted total of deposits and interest credited **less
> the withdrawals posted to it**, taken as no less than zero and no more than the tier's relationship
> bonus balance cap."

> "The bonus balance basis is measured net of **the withdrawals posted in the three calendar months
> ending on the review date**."

The compute applies both: `bonus_ledger_basis = MX(0.0, deposits_all + interest_all - withdrawals_all)`
(`compute_basis` cites the first sentence for `deposits_all`, `interest_all` and `withdrawals_all`), and
then the fall-through branch of `bonus_basis` subtracts `withdrawals_three_month` from it again. Every
withdrawal of the last three months is therefore deducted twice.

The contradiction is sharpest at the ladder's top tier. `factors[bonus_basis_netting].ladder[0]` and the
rule both read:

> "Where the card balance owed is no more than 1,500.00 USD and card payments of at least 1,000.00 USD
> posted in the three calendar months ending on the review date, **no withdrawal is netted out and the
> whole posted total stands as the basis.**"

but the compute for that branch is `MN(P('relationship_bonus_balance_cap'), MX(0.0, bonus_ledger_basis))`,
in which `withdrawals_all` is still subtracted. "No withdrawal is netted out" is false of the expression
that implements it, and "the whole posted total" denotes two different quantities depending on which of
the two basis definitions the reader takes.

Demonstrated consequence: task 0's customer sits on exactly this tier; the two readings give
`bonus_basis` of 1,880.28 and 43,330.28, and scored bonus corrections of 4.23 and 107.86. See `0.md`,
`### policy_self_consistency (this task only)`. Task 1 does not use this policy.

Affected artifact: `savings.extended.yaml`, `savings_ext_relationship_bonus_correction` — `rule`
sentences 1 and 2, `compute` bindings `bonus_ledger_basis` and `bonus_basis`,
`factors[bonus_basis_netting].ladder[0]` and its `baseline`.

**CG-3 — `savings_ext_excess_fee_review_credit` top tier of `ceiling_bite_moment` drops the fee-unit
step its own sentence presupposes.** Observation (no consequence demonstrable on either task in this
difficulty).

> "Where four or more withdrawals posted to the account in the three calendar months ending on the review
> date, the review ceiling binds the reviewable fee pool **before the fee units are applied**."

compute: `MN(review_ceiling, reviewable_fee_pool)`. "Before the fee units are applied" entails that they
are then applied, i.e. `MN(MN(review_ceiling, reviewable_fee_pool), unit_entitlement)`; the compute never
applies them. Task 1's customer has three withdrawals in that window and takes tier 2, so the branch is
never exercised in this difficulty and no scored value moves. Recorded as an observation, not a red light.

Affected artifact: `savings.extended.yaml`, `savings_ext_excess_fee_review_credit.compute` binding
`capped_review_credit`, first branch.

**Observation CG-5 — "three calendar months ending on X" is implemented as a whole-month anniversary
window.** `_within` uses `0 <= MONTHS(posted_date, NOW) < within_months`, so for `NOW = 2026-09-16` the
"three calendar months" window is 2026-06-17 … 2026-09-16, not the calendar months June/July/August. The
two readings coincide for a reader who takes "the three calendar months ending on the correction date" as
a period ending on that date, so no second number arises on either task's records; recorded only because
the phrase "calendar months" invites the other reading.

Every other quantity, window, filter, tier, branch, cross-category read, acting base, grouping, cap/floor
and rounding point in the six policies has a verbatim `compute_basis` quotation and a matching restricted
expression, and no `compute` binding introduces a basis absent from its `rule`.

### action_binding_and_uuids

Six `(target_tool, computes)` pairs, each claimed by exactly one policy:

| policy | target_tool | computes |
| --- | --- | --- |
| `savings_ext_promotional_interest_correction` | `post_promotional_interest_correction_acb0ec5b` | `correction_amount` |
| `savings_ext_relationship_bonus_correction` | `post_relationship_bonus_correction_5bb15040` | `bonus_amount` |
| `savings_ext_periodic_fee_courtesy_credit` | `credit_savings_courtesy_refund_0ed102a0` | `refund_amount` |
| `savings_ext_standing_transfer_amount` | `set_savings_standing_transfer_55216172` | `transfer_amount` |
| `savings_ext_excess_fee_review_credit` | `credit_savings_fee_review_ce0a6323` | `review_credit_amount` |
| `savings_ext_surplus_transfer_amount` | `transfer_savings_surplus_c4c79a83` | `transfer_amount` |

`transfer_amount` is claimed twice, but by policies with disjoint subjects
(`savings_set_automatic_transfer` vs `savings_withdrawal`) and different target tools, so the
`(target_tool, computes)` pair is unique in each case. No confirmation, review, wait or procedure outside
the policy is added by any docstring.

uuid8s: `acb0ec5b`, `5bb15040`, `0ed102a0`, `55216172`, `ce0a6323`, `c4c79a83`. Eight hex characters each,
all six distinct, no shared prefix or suffix, no arithmetic or lexical progression between them, none a
re-tailing of another. Independently generated and frozen. PASS.

Docstring ordering scan: the only occurrences of an ordering word are
`set_savings_standing_transfer_55216172` — "replace whatever stood there before" and "takes effect from
the next scheduled run". Both describe the write's own business effect (the prior stored value; the
instruction's effective date), neither states this call's position relative to another call, and no
docstring names another tool. PASS.

Tool-layer prerequisite validation: every one of the six function bodies was read. None raises, returns an
error string, refuses a call, or emits a hint conditioned on any prerequisite state. Each performs its
`ctx.create`/`ctx.update`, recomputes the balance by summing the account's rows, and returns a
confirmation. The prerequisite decision is left entirely to the agent. PASS.

### prerequisite_graph

Check 7 over the whole graph. Every policy has `prerequisite` filled in (`[]` on the three leaves).

```
savings_ext_promotional_interest_correction   []
savings_ext_periodic_fee_courtesy_credit      []
savings_ext_excess_fee_review_credit          []
savings_ext_relationship_bonus_correction     -> promotional_interest_correction  (value_input, gate bonus_ledger_basis, form state)
savings_ext_standing_transfer_amount          -> relationship_bonus_correction    (value_input, gate posted_balance,     form state)
                                              -> periodic_fee_courtesy_credit     (value_input, gate posted_balance,     form state)
savings_ext_surplus_transfer_amount           -> excess_fee_review_credit          (value_input, gate settled_balance,    form state)
```

Every `problem` names another extended policy id in this file; none names a base policy or itself; the
graph is acyclic (two disjoint trees, depths 3 and 2). Every `form` is `state`, so no `fallback_reason` is
required and none is present — correct. Every `resolved_by` is the depended-on policy's own `target_tool`.
Every `kind` is `value_input` and every `gate` names a binding that genuinely exists in the blocked
policy's `compute` (`bonus_ledger_basis`, `posted_balance`, `settled_balance` — all present and all
upstream of `result`). No authoring-viewpoint phrasing ("in this task", "at the opening", "the current
world") appears anywhere in any `prerequisite` block.

One `condition` is defective; it is recorded as **CG-6** under `findings`.

### prerequisite_sentences

Check 6, four-point test on each of the four edges. All four `policy_source` strings were mechanically
confirmed to be verbatim substrings of the **blocked** policy's own `rule`, and mechanically confirmed
**absent** from the depended-on policy's `rule`.

1. `relationship_bonus_correction -> promotional_interest_correction`
   > "The relationship bonus owed for a closed statement cycle is settled only after the promotional
   > interest due on that cycle's new money stands credited on the account."

   Ordering connective "only after"; what is waited on is a record-visible state ("stands credited on the
   account") named in the words of `savings_transactions` interest rows, with no performer and no tool; no
   snake_case, no policy id, no row id. Exactly one write of this difficulty brings that state about —
   `post_promotional_interest_correction_acb0ec5b` is the only write that posts a promotional interest
   credit; `post_relationship_bonus_correction_5bb15040` posts `interest_component=relationship_bonus`,
   and neither fee-credit tool posts an interest row. Derivation, single reading: the sentence says the
   bonus waits on promotional interest due for that cycle standing credited → the records show the closed
   cycle's promotional credit is short of what `savings_ext_promotional_interest_correction`'s own rule
   computes as due → that policy's rule describes posting the shortfall → do that first. PASS.

2. `standing_transfer_amount -> relationship_bonus_correction`
   > "The qualifying recurring amount is worked out only after the account's posted balance carries the
   > relationship bonus owed for every closed statement cycle."

   Ordering connective "only after"; state form; no tool, id or token. The one write that brings a
   relationship bonus credit onto the posted balance is
   `post_relationship_bonus_correction_5bb15040`. PASS.

3. `standing_transfer_amount -> periodic_fee_courtesy_credit`
   > "Before the qualifying recurring amount is fixed, the courtesy credit owed against the periodic fees
   > standing on the account must already appear in its posted balance."

   Ordering connective "Before"; state form; no tool, id or token. Two tools post `savings_fee_refund`
   rows, but only `credit_savings_courtesy_refund_0ed102a0` books a **courtesy** credit **against the
   periodic fees** (its rule: "booked against the most recently posted monthly maintenance fee"), whereas
   `credit_savings_fee_review_ce0a6323` books a bank-error credit against an excess withdrawal fee. The
   hop resolves to one write. PASS.

4. `surplus_transfer_amount -> excess_fee_review_credit`
   > "The surplus available to move out is fixed only after the credit owed for the excess withdrawal fees
   > charged on branch and ATM withdrawals stands on the account."

   Ordering connective "only after"; state form; no tool, id or token. Resolves uniquely to
   `credit_savings_fee_review_ce0a6323`. One scope remark is recorded as observation **CG-7**. PASS.

No rule carries a second wording of any dependency, no rule names another policy's tool or id (mechanically
verified over all six rules against all six tool names and all six policy ids: zero hits), and no
depended-on rule restates the blocked rule's sentence.

Cross-problem orders stated in a **base** rule: none of the four edges rests on one. The base rules cited
(`savings_evt_withdrawal_allowance`, `savings_evt_fee_refund`, `savings_evt_automatic_transfer`,
`savings_evt_deposits`, `savings_evt_closure`, `savings_evt_interest`, `savings_evt_bonus_interest`,
`savings_agg_relationship_bonus_allocation`) contain within-action sequencing only
("Accrued interest … is credited first", "The fee is written … before payout"), all internal to a single
base action and grounding no extended edge. PASS.

### override_declarations

Check 1's finding half, sentence by sentence against each `base_policy_refs` entry.

- `savings_ext_promotional_interest_correction` → `savings_evt_bonus_interest`, `savings_evt_interest`,
  `savings_agg_relationship_bonus_allocation`. Two `overwrite` entries name the promotional-portion
  clause and the daily-accrual clause verbatim. The remaining base sentences (eligibility for interest,
  `minimum_balance_to_earn_interest`, component stacking order) are neither contradicted nor relied on.
  Declared.
- `savings_ext_relationship_bonus_correction` → `savings_agg_relationship_bonus_allocation`,
  `savings_evt_interest`, `savings_evt_bonus_interest`. Two `overwrite` entries name the running-cap
  allocation clause and the daily-accrual clause verbatim. Declared. (The basis defect CG-2 is an
  internal inconsistency of the replacement text, not an undeclared override.)
- `savings_ext_standing_transfer_amount` → `savings_evt_automatic_transfer`, `overwrite: []`. Checked
  sentence by sentence: ownership of the funding account, its active status, the day-of-month range 1–28,
  the minimum amount, the posting behaviour and the stop semantics are all inherited unchanged, and the
  extended policy's `floored_instalment = MX(P('automatic_transfer_min_amount'), rounded_instalment)`
  positively enforces the base minimum rather than weakening it. The base fixes no amount, so computing
  one is an addition, not an override. Empty `overwrite` is correct.
- `savings_ext_surplus_transfer_amount` → `savings_evt_deposits` (declared: availability clause replaced
  by "The available balance is the settled balance"), `savings_evt_withdrawal_allowance`,
  `savings_evt_closure`. The allowance sentences (counted channels, `free_withdrawals_per_cycle`, the
  excess fee, the daily online limit, the balance cover) are inherited; the extended policy caps the move
  at `P('online_transfer_daily_limit')` on its top tier, consistent with base. Nothing weakened.
- `savings_ext_excess_fee_review_credit` → `savings_evt_fee_refund`, one `overwrite` naming
  "A fee is refunded in full, never in part, as one savings_fee_refund row whose source_item_id is the fee
  row." The tool stamps `adjustment_reason="bank_error"`, and base says a bank_error refund "has no time
  limit and does not count toward the courtesy limit", so neither the courtesy window nor the courtesy
  count applies. Declared.
- `savings_ext_periodic_fee_courtesy_credit` → `savings_evt_fee_refund`, one `overwrite` naming the same
  "refunded in full, never in part" sentence. **This is where CG-4 lives.**

**CG-4 — the courtesy pool reaches fees the inherited base courtesy window forbids refunding, and no
`overwrite` declares it.** `SOURCE-POLICY RED`.

`credit_savings_courtesy_refund_0ed102a0` stamps `adjustment_reason="courtesy_waiver"`, so every base
courtesy gate of `savings_evt_fee_refund` is in force. One of them is:

> "The fee must have posted no more than courtesy_refund_window_days calendar days before the courtesy
> refund is granted. Count calendar days with the day after the fee's posted_date as day 1; the refund is
> allowed while the frozen date is on or before the fee's posted_date plus courtesy_refund_window_days."

The extended rule's top pool tier is:

> "…the refundable fee pool is every monthly maintenance fee and every paper statement fee posted to the
> account in **those twelve calendar months**."

and the middle tier reaches three calendar months. `courtesy_refund_window_days` is 60 days on four of the
six savings tiers, 90 on Premier Money Market and 120 on Private Client Money Market — in every case
shorter than twelve months, and on four tiers shorter than three months. The extended policy therefore
pays a courtesy credit computed over fees that base forbids courtesy-refunding at all, and
`savings_ext_periodic_fee_courtesy_credit.overwrite` names only the "refunded in full, never in part"
sentence. The courtesy-window sentence is nowhere named, so it is inherited in full and is contradicted.

Demonstrated consequence: on task 0 the pool is 46.00 under the extended rule and 28.00 under the
inherited base gate, giving scored courtesy credits of 42.00 and 26.00 — and, through the
`posted_balance` prerequisite edge, two different standing-transfer amounts. See `0.md`,
`### policy_self_consistency (this task only)`. Task 1 does not use this policy.

Affected artifact: `savings.extended.yaml`, `savings_ext_periodic_fee_courtesy_credit` — `rule`
paragraph 2, `compute` bindings `maintenance_fees_twelve_month`, `paper_fees_twelve_month`,
`maintenance_fees_three_month`, `refundable_fee_pool`, and the absent `overwrite` entry.

**Observation CG-8 — the courtesy allowance count widens the base tier limit under the same name.**
Base: "The customer's count of savings courtesy refunds in the rolling 365 days must be below the tier's
courtesy_refund_limit_365d." Extended: "the courtesy allowance count is the savings tier's courtesy refund
limit plus two" / "plus one", implemented as
`allowed_refund_count = P('courtesy_refund_limit_365d') + K('extra_high')`. The base sentence gates whether
a refund may be **granted**, and only one refund is granted, so the gate is not literally broken; but the
extended text re-uses the tier limit's name for a larger number that then multiplies into
`allowance_amount`, and no `overwrite` mentions it. Recorded as an observation because the base sentence
constrains a count of grants, not an amount; the numeric effect on task 0 (allowance 48.00 vs 24.00,
credit 42.00 vs 24.00) is set out in `0.md` for completeness.

No anonymous intermediate factor, 0/1 multiplier or dropped base branch was found beyond CG-3 and CG-4,
and no rule, `compute_basis` or note calls a base output a "wrong value" or an "algorithm to avoid".

### factor_ladders

Structure only. Per policy: factor count, effect labels, `decides`, tier count, multi-source tiers,
cross-difficulty categories, and whether every tier is stated in the `rule` and implemented in `compute`.

| policy | factors | parameter | method | multi-source | cross_difficulty | categories |
| --- | --- | --- | --- | --- | --- | --- |
| `promotional_interest_correction` | 6 | 2 | 4 | 3 | 3 | card, checking, cd |
| `relationship_bonus_correction` | 5 | 2 | 3 | 2 | 2 | checking, card |
| `periodic_fee_courtesy_credit` | 5 | 2 | 3 | 3 | 2 | card, checking |
| `standing_transfer_amount` | 6 | 3 | 3 | 2 | 2 | checking, card |
| `excess_fee_review_credit` | 4 | 2 | 2 | 3 | 2 | card, checking |
| `surplus_transfer_amount` | 6 | 3 | 3 | 2 | 2 | card, checking |

Every policy is within the 4–6 bound, has at least 2 of each effect, at least 2 multi-source and at least
2 `cross_difficulty`. Every ladder has exactly three tiers, the fall-through counted. Tier conditions were
checked pairwise for overlap as stated: each ladder's tiers are separated by a strict threshold on the
same measure plus, in the multi-source cases, a conjunct on a second record, and the fall-through is the
negation of the disjunction of the first two — pairwise disjoint as written in all 31 ladders.

Every factor's `bindings` sets are disjoint within its policy (mechanically checked), and every `decides`
names an intermediate input, never `result` — with one qualification recorded as an observation:
`relationship_bonus_correction.bonus_day_count_convention` has `decides: raw_bonus` and
`excess_fee_review_credit.ceiling_bite_moment` has `decides: capped_review_credit`, each the binding
immediately before `result`. Both are genuine inputs to a further step (`result` subtracts
`bonus_already_paid` / applies `MX(0.0, …)`), so neither names the outcome; noted only because the margin
is one binding.

Every tier of every ladder was located in its policy's `rule` prose with its condition and its value or
method — no tier lives only in `compute` — and every branch of each `decides` expression corresponds to a
tier the rule states. Label honesty: the `method` tiers change a window (`new_money_window_convention`,
`refundable_pool_width`, `reviewable_pool_width`, `credited_deduction_scope`, `bonus_deduction_selection`),
a base or set of rows (`withdrawal_offset_basis`, `bonus_basis_netting`, `fresh_deposit_hold`), a rounding
mode (`interest_owed_rounding`, `courtesy_credit_rounding`, `instalment_rounding`, `moved_amount_rounding`),
a day-count convention (`bonus_day_count_convention`), a cap moment (`binding_ceiling_choice`,
`ceiling_bite_moment`) or the presence of an offsetting operation (`recent_deposit_offset`,
`recent_withdrawal_offset`, `instalment_pacing`); the `parameter` tiers substitute a rate, a day count, a
threshold, a count or a ceiling into an unchanged formula. Every `method` tier names a computation the
charter states.

**Observation CG-9 — the multiplier factors are labelled inconsistently across the charter.**
`standing_transfer_amount.instalment_pacing` (×1.25 / ×1.10 / none) is `method`, while
`surplus_transfer_amount.moved_surplus_share` (×0.75 / ×0.90 / ×1.00) and
`periodic_fee_courtesy_credit.goodwill_share_step` (×0.9 / ×0.75 / ×0.5) are `parameter`. All three select
a multiplier. `instalment_pacing` has the stronger claim to `method` because its fall-through removes the
multiplication and the four-decimal-place retention along with it, whereas the other two keep one formula
throughout and vary only the number; on that reading each label is individually defensible and no scored
value turns on the labels, so this is an observation, not a red light. It is recorded because the same
kind of tier carries two different labels within one charter.

### findings

| id | verdict | bears on |
| --- | --- | --- |
| CG-1 | `SOURCE-POLICY RED` — "rounded half up to the whole dollar" compiled two incompatible ways, neither of them half-up | task 0 (demonstrated, twice); latent on task 1 |
| CG-2 | `SOURCE-POLICY RED` — bonus balance basis defined twice, withdrawals netted twice, top tier contradicted by its own compute | task 0 (demonstrated) |
| CG-3 | observation — `ceiling_bite_moment` top tier drops the fee-unit step its sentence presupposes | neither task exercises the branch |
| CG-4 | `SOURCE-POLICY RED` — undeclared override of the inherited base courtesy window by the twelve-month/three-month fee pool | task 0 (demonstrated) |
| CG-5 | observation — "calendar months" implemented as a whole-month anniversary window | both tasks, no second number |
| CG-6 | `SOURCE-POLICY RED` — the promotional edge's `condition` is weaker than its own prerequisite sentence and is already literally true at the opening | task 0 (demonstrated) |
| CG-7 | observation — the surplus edge's prerequisite sentence scopes the credit to branch/ATM fees while the policy it points at scopes it to all uncounted withdrawals | task 1 |
| CG-8 | observation — the courtesy allowance count widens the base tier limit under the same name, undeclared | task 0 |
| CG-9 | observation — multiplier factors labelled inconsistently (`method` vs `parameter`) | both tasks, no scored value turns on it |

**CG-6 in full.** `savings_ext_relationship_bonus_correction.prerequisite[0].condition` reads:

> "The account's ledger carries a promotional interest credit for the closed statement cycle, so that the
> posted total of deposits and interest credited already includes the promotional interest due on that
> cycle's new money."

Its first clause is satisfied by the mere existence of any promotional interest row carrying the closed
cycle, whereas the `policy_source` sentence it is supposed to restate requires the promotional interest
**due** to stand credited. Check 7 requires `condition` to name the handling-time state check 6 derives,
neither strengthened nor weakened; this one is weakened to the point of being true at the opening of
task 0, where `savings_transactions` already carries a `promotional` interest credit stamped
`statement_cycle = 2026-08`. Taken at face value the edge would not be a prerequisite at all. The
`policy_source` sentence — which is what a solver reads — still makes the edge sound, so the task's tree
survives on the rule; the defect is that the declared `condition` no longer describes it. Demonstrated
against task 0's seed in `0.md`, `### problem_chain`.

**CG-7 in full.** The prerequisite sentence of `savings_ext_surplus_transfer_amount` waits on "the credit
owed for the excess withdrawal fees charged on **branch and ATM** withdrawals", while
`savings_ext_excess_fee_review_credit`'s own rule scopes the credit to "the excess withdrawal fees charged
against **withdrawals that never counted toward the allowance**". Base
`savings_evt_withdrawal_allowance` makes branch and ATM withdrawals a proper subset of the uncounted ones
(a withdrawal through a channel outside `excess_withdrawal_counted_channels` also never counts), so the
sentence is narrower than the policy it routes to. On task 1's records every excess withdrawal fee sits on
a branch or ATM withdrawal, so both scopes select the same fees and the same number; recorded as an
observation because no second value arises here.

## closing_checklist

Written after both reveals. The charter-global section above is pre-reveal by construction and has been
left untouched; the two corrections this section records are stated here rather than edited into it.

**The difficulty does not close out.** Task 1 passes all four relationships; task 0 fails two of them, so
Step 4's checklist is answered but the close-out is withheld and the instantiation-stage gates are **not**
re-run on a final form.

| Step 4 item | status |
| --- | --- |
| audit files one-to-one with the tasks, `_difficulty.md` alongside | yes — `0.md`, `1.md`, `_difficulty.md`; this is revision 1, so no old revision to preserve |
| every comparison section carries a PASS | **no** — `0.md` `## source_gt_comparison` carries `SOURCE-POLICY RED`, `SOURCE-FACTOR RED` and `SOURCE-TASK RED`; `1.md` carries PASS on all four |
| extended policies fully covered, task scopes pairwise disjoint | yes — task 0 claims `standing_transfer_amount`, `relationship_bonus_correction`, `periodic_fee_courtesy_credit`, `promotional_interest_correction`; task 1 claims `surplus_transfer_amount`, `excess_fee_review_credit`; the union is all six and the intersection is empty. Both `charter_scope` blocks agree with the trees the auditor derived |
| task tools and GT closed | yes — six tools, each the `target_tool` of exactly one policy, each called exactly once across the two tasks |
| each task tool uses an independently generated, frozen uuid8 | yes — see `### action_binding_and_uuids` |
| every tree: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 `owner=user` write, no cycle | yes — task 0: n=3, 3 `value_input`, root is `owner=user`; task 1: n=1, 1 `value_input`, root is `owner=user` |
| the difficulty's `prerequisite` edges are jointly a DAG, with no cycle from cross-task references | yes — two disjoint trees, no edge crosses between them |
| every computation: a self-sufficient baseline, 4–6 factors (2 of each effect, 2 multi-source, 2 cross-difficulty), ladders of ≥3 tiers stated in the rule, every factor load-bearing against an honest baseline, all-baseline ≠ gold | **all but one** — 32 of 32 factors bear weight and every all-baseline fall-back differs from gold, but `savings_ext_relationship_bonus_correction.factors[bonus_basis_netting].baseline` is dishonest (it double-nets withdrawals and floors at zero, which is why its `baseline_result` is 0.00 rather than a number a reader could reach). See `0.md`, `### factor_weight` |
| instantiation-stage gates re-run on the final form | not run — there is no final form to run them on |

**Correction 1 to the pre-reveal section: CG-6 is downgraded to an observation.** It was frozen above as
`SOURCE-POLICY RED`. Read as a whole, the `condition`
("…carries a promotional interest credit for the closed statement cycle, **so that** the posted total …
already includes the promotional interest due on that cycle's new money") is a conjunction whose second
conjunct is false at the opening, so the edge is not in fact already satisfied and no consequence is
demonstrable. The defect is that the first clause, taken alone, is satisfied by the very seed row
`prerequisite_closure` cites as evidence to the contrary. Recorded in `0.md` as **F0-4**, an observation.
The problem tree of task 0 therefore holds.

**Correction 2 to the pre-reveal section: CG-4 is refined, not withdrawn.** It was frozen above as an
outright undeclared override of the base courtesy window. The more accurate characterisation, set out in
`0.md` as **F0-3**, is that the declared `overwrite` destroys the one-to-one fee→refund mapping the base
gate was written for without saying what the gate now tests, leaving two readings — the gate against each
fee in the pool (28.00 pool, 26.00 credit, 303.00 transfer) or against the anchor fee alone (46.00 pool,
42.00 credit, 293.00 transfer, which is GT). The red light stands and the demonstrated consequence is
unchanged; only the description of the root cause moves.

**Red lights blocking close-out**, all on task 0, all demonstrated in `0.md` against that task's own world
and scored solution:

| id | verdict | one line |
| --- | --- | --- |
| CG-1 / F0-1 | `SOURCE-POLICY RED`, `SOURCE-TASK RED` | `RND(x + 0.5, 0)` is not "rounded half up to the whole dollar"; 10.50 and 42.00 are scored where the rule reads 9.50 and 41.00, closing at 295.00 rather than 293.00 |
| CG-2 / F0-2 | `SOURCE-POLICY RED`, `SOURCE-TASK RED`, `SOURCE-FACTOR RED` | the bonus balance basis is defined twice and netted twice; the tier taken says "no withdrawal is netted out" while its expression nets all of them — 4.23 against 107.86, closing at 293.00 rather than 229.00; the factor's baseline is dishonest |
| CG-4 / F0-3 | `SOURCE-POLICY RED`, `SOURCE-TASK RED` | the inherited base courtesy window is left undetermined against a twelve-month fee pool — 42.00 against 26.00, closing at 293.00 rather than 303.00 |

Observations carried forward and not blocking: CG-3, CG-5, CG-7, CG-8, CG-9, F0-4, F0-5, F0-6, F1-1,
F1-2, F1-3, F1-4.

**Independent-derivation agreement.** Both tasks were derived blind and frozen before any reveal. Against
GT the auditor reproduced, figure for figure: task 1's `review_credit_amount` 24.00 and `transfer_amount`
16,530.00, both `baseline_result` values and all 10 `factor_sensitivity` figures; and task 0's four
`expected` values, four `baseline_result` values, all 22 `factor_sensitivity` figures and all three
`edge_load_bearing` figures — **on the compute-faithful reading**. The three red lights are precisely the
places where the policy's own prose licenses a second number that GT does not score, which is why they are
defects of the artifacts and not of any solving agent.

---

# revision_2

## charter_global_frozen (revision_2)

- Round: 2, re-audit. Freeze time 2026-09-16 10:04 UTC. Same independent auditor as revision 1.
- **Re-derivation basis.** `savings.extended.yaml` moved from
  `d1aa0ebcdaf57935623dd8a05a59c874be8945a9b94aab9817fc7cca05b99726` to
  `65311a04323f22474a9dbbf92c948ceb3b40a438911d06f8c41ab2bce6593296`, so every charter-global section is
  re-derived rather than carried forward. `task_tools.py` is **byte-identical**
  (`9a91e7f72082afd6aab91cad3024b4cb3fde18bbd83b0b0a453a33040050662a`), so
  `### action_binding_and_uuids`'s tool half — the six uuid8s, the docstring ordering scan and the
  function-body reading that showed no tool judges a prerequisite — is carried forward by reference on
  that hash; only the `(target_tool, computes)` pairs were re-checked against the new yaml, and all six
  remain unique. Both task JSONs moved (`0.json` → `3e74a8ea…`, `1.json` → `2f069c27…`).
- **contamination_disclosure.** This round is **not blind and is not claimed to be.** Both tasks' GT was
  revealed in revision 1, so nothing here is an independent blind derivation. What is claimed is narrower
  and is what this round was asked for: every figure below was recomputed by the auditor from the
  **reworked charter** and the unchanged seed before the reworked GT was read, and the reworked GT was
  then compared against it. The masked views are byte-identical to revision 1
  (`6f8d7853…`, `91c5728a…`), so the world, the clock and both personas did not move; revision 1's reading
  of the world stands and was not rebuilt.
- Base section re-checked: still byte-for-byte identical to `blueprint/products/savings.yaml` on all ten
  top-level keys. Same six extended policy ids.
- Entry condition: the coordinator's post-rework gate snapshot is cited, not re-run.
  `check_traceability.py` remains deferred to the render stage.

### what actually moved (established from the artifacts, not from the claims)

Eight sections of the charter changed; `overwrite` gained one entry. Nothing else did.

| policy | section | change |
| --- | --- | --- |
| `promotional_interest_correction` | `compute[rounded_shortfall]` | `RND(x + 0.5, 0)` → `float(int(x + 0.5))` |
| `periodic_fee_courtesy_credit` | `compute[rounded_courtesy_credit]` | `RND(x + 0.5, 0)` → `float(int(x + 0.5))` |
| `standing_transfer_amount` | `compute[rounded_instalment]` | `RND(x, 0)` → `float(int(x + 0.5))` |
| `surplus_transfer_amount` | `compute[rounded_amount]` | `RND(x, 0)` → `float(int(x + 0.5))` |
| `relationship_bonus_correction` | `rule`, `baseline.rule`, `factors[bonus_basis_netting].ladder` | basis rewritten as two named stages; `compute` **unchanged** |
| `periodic_fee_courtesy_credit` | `rule`, `overwrite` | one sentence added; a second `overwrite` entry added |
| `relationship_bonus_correction` | `prerequisite[0].condition` | strengthened |

### rule_compute_equivalence (revision_2)

**CG-1 — CLOSED in substance.** All four tiers reading "rounded half up to the whole dollar" now compile
to the single form `float(int(x + 0.5))`. Under the runtime's semantics `int()` truncates toward zero, so
for `x >= 0` this is exactly `floor(x + 0.5)`, which is half-up rounding to the whole dollar. Three things
make the closure substantive rather than a rename:

1. *It is the same expression in all four places.* Revision 1's finding was that one English sentence had
   two implementations; the charter now has one. The two policies that were already arithmetically
   right (`standing_transfer_amount`, `surplus_transfer_amount`) were changed too, so the fix was applied
   where it cost a number and where it did not.
2. *The identity holds in every reachable world, not just on these two seeds.* Each of the four inputs is
   non-negative by construction: `raw_shortfall` rests on
   `promotional_basis = MN(P('promo_balance_cap'), MX(0.0, …))`; `raw_courtesy_credit` on a `SUM` of fee
   amounts times a share in {0.5, 0.75, 0.9}; `paced_instalment` on `net_shortfall`/`qualifying_shortfall`,
   both `MX(0.0, …)`; `offset_surplus` on `MX(0.0, …)` or `surplus * surplus_share` with
   `surplus = MX(0.0, …)`. So `int()` never truncates toward zero from below.
3. *It is numerically robust at the tie.* Halves are exactly representable in binary floating point, so
   `x + 0.5` is exact when `x` is a tie and lands on the integer; for non-ties the ~1e-16 representation
   error cannot cross an integer boundary. `41.4 + 0.5` evaluates below 41.9 and truncates to 41, which is
   the correct half-up answer.

Verified numerically: `raw_shortfall = 14.102876712328767` → 14.00; `raw_courtesy_credit = 41.40` → 41.00;
`paced_instalment = 294.6812` → 295.00; `offset_surplus = 16530.095` → 16530.00. Sentence and expression
agree in all four.

**CG-2 — CLOSED in substance.** The `compute` was not touched; the `rule` was rewritten to say what the
compute does, which is a legitimate direction for a rule↔compute non-equivalence provided the result is
unambiguous. It is. The basis is now two explicitly named stages:

> "…the bonus balance basis, which starts from **the bonus ledger basis**, being the account's posted
> total of deposits and interest credited less the withdrawals posted to it, taken as no less than zero.
> The bonus ledger basis is then **further reduced** by the withdrawals posted in the three calendar
> months ending on the review date, and the reduced figure, taken as no less than zero and capped at the
> tier's relationship bonus balance cap, is the bonus balance basis."

The two competing definitions of one name are gone: the first stage has its own name, the second is a
"further reduction", and the double subtraction revision 1 found is now the stated intent rather than an
accident. The ladder follows:

> "Where the card balance owed is no more than 1,500.00 USD and card payments of at least 1,000.00 USD
> posted …, **no further reduction is made and the bonus ledger basis itself stands as the figure to be
> capped**."

which is exactly `MN(P('relationship_bonus_balance_cap'), MX(0.0, bonus_ledger_basis))`. Revision 1's
offending phrase "no withdrawal is netted out and the whole posted total stands as the basis" no longer
appears anywhere in the charter. On task 0's world the sentence and the expression both give
`bonus_basis = 1,879.28`; the 43,330.28 second reading is unreachable.

**CG-3 — still standing, as the reworker states.** `savings_ext_excess_fee_review_credit` is byte-identical
to revision 1, so `compute[capped_review_credit]`'s first branch is still `MN(review_ceiling,
reviewable_fee_pool)` against a sentence reading "the review ceiling binds the reviewable fee pool
**before the fee units are applied**". Neither task enters the branch (task 1 has three withdrawals in the
window and takes the middle tier), so it remains an observation, not a red light.

**CG-5 — still standing**, unchanged and still costing neither task a second number.

**Re-swept, sentence by sentence, over all six policies:** every `compute_basis` value is a verbatim
substring of its own policy's `rule`, every `baseline.rule` sentence is in the `rule`, and no `compute`
binding introduces a basis absent from its rule. Two anomalies were found; both are **pre-existing**,
present in revision 1's artifacts and not introduced by this rework, and both are recorded below as
R2-O1 and R2-O2.

### override_declarations (revision_2)

**CG-4 — CLOSED in substance.** `savings_ext_periodic_fee_courtesy_credit.overwrite` gained a second
entry:

```
base_policy:        savings_evt_fee_refund
superseded_clause:  "The fee must have posted no more than courtesy_refund_window_days calendar days
                     before the courtesy refund is granted."
replaced_by:        "Because the courtesy credit is booked as one entry for the whole review rather than
                     one entry for each fee, the courtesy window is tested once, against the fee entry the
                     credit is booked against, and not against each fee in the refundable fee pool."
```

and the same replacement sentence now stands in the policy's `rule`, second sentence. Checked:

- the `superseded_clause` is a **verbatim** substring of `savings_evt_fee_refund.rule` and matches the
  condition of **exactly one** eligibility gate (`courtesy_window`) — not a loose paraphrase that could
  retire a neighbour;
- `retired_gates_of(base, extended)` returns exactly `{('savings_evt_fee_refund', 'courtesy_window')}`.
  The other four gates of that base policy — `eligible_fee_code`, `courtesy_limit`, `account_open`,
  `refund_once` — remain inherited in full;
- the replacement is itself satisfiable and satisfied: the anchor fee is the 2026-08-28 monthly
  maintenance fee, 19 days old against a 60-day tier window.

Revision 1's defect was that the charter left it undetermined whether the window tested each pooled fee or
the anchor fee, and scored 42.00 on the second reading without saying so. The charter now says so, in the
`rule` a solver reads and in the `overwrite` the gate machinery reads. One reading survives.

**The base-gate counts moved for a legitimate reason, and the reason is this retirement.** The counter
`retired_gates_of` (`skills/erl-task-instantiate/scripts/check_solvability.py:55`) iterates every extended
policy's `overwrite` and retires `(base_policy, gate_id)` **charter-globally**, not per task scope. One
gate is retired, so every task in the difficulty loses exactly one inherited base gate: task 0 from 13 to
12, task 1 from 8 to 7. That accounts for both drops exactly, with nothing left over.

For task 0 the retirement is the substantive change and it is declared. For task 1 it costs nothing at
all: task 1's only fee-refund write is `credit_savings_fee_review_ce0a6323`, which stamps
`adjustment_reason = "bank_error"`, and base `savings_evt_fee_refund` says a bank_error refund "has no
time limit and does not count toward the courtesy limit" — so `courtesy_window` never governed that write.
It was being counted for task 1 because the counter attaches base gates by policy and subject rather than
by `adjustment_reason`. **This is a retired gate, not the quiet loss of an inherited provision.**

**CG-8 / F0-5 — still standing, as the reworker states.** `courtesy_limit` was not retired and
`allowed_refund_count` is still `P('courtesy_refund_limit_365d') + K('extra_high')` = 4 against a tier
limit of 2. Observation, unchanged.

All other `overwrite` blocks are unchanged from revision 1 and their sentence-by-sentence conclusions
carry forward.

### prerequisite_graph and prerequisite_sentences (revision_2)

Graph unchanged: same four edges, same `kind`, `gate`, `form` and `resolved_by`, still acyclic, still two
disjoint trees of depth 3 and 2. All four `policy_source` sentences re-checked mechanically: each is still
a verbatim substring of the **blocked** policy's own rule and still absent from the depended-on rule. No
tool name, policy id or snake_case token appears in any rule or any `policy_source`; no authoring-viewpoint
phrasing appears in any `prerequisite` block. The two rule rewrites did not disturb any prerequisite
sentence.

**CG-6 / F0-4 — acted on, and the action is real.** The promotional edge's `condition` changed from

> "The account's ledger carries **a promotional interest credit** for the closed statement cycle, so that
> the posted total … already includes the promotional interest due on that cycle's new money."

to

> "The account's ledger carries **promotional interest credits** for the closed statement cycle **that
> together cover** the promotional interest due on that cycle's new money, so that the posted total …
> already includes it."

The first clause is no longer satisfied by the mere existence of the seeded 1.85 row: 1.85 does not
"together cover" the 14.00 due. The `condition` now carries the same strength as its `policy_source`
sentence, which is what check 7 requires. The other three conditions are unchanged, as they should be —
revision 1 found no fault with them.

**CG-7 — still standing, as the reworker states.** The surplus edge's sentence still scopes the awaited
credit to branch and ATM fees while the policy it routes to scopes itself to all uncounted withdrawals.
Observation; on task 1's seed the two scopes coincide exactly.

### factor_ladders (revision_2)

Structure re-counted over all six policies. Unchanged and within bounds everywhere:

| policy | factors | parameter | method | cross_difficulty | tiers per ladder | `decides: result` | overlapping bindings |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `promotional_interest_correction` | 6 | 2 | 4 | 3 | 3 | none | none |
| `relationship_bonus_correction` | 5 | 2 | 3 | 2 | 3 | none | none |
| `periodic_fee_courtesy_credit` | 5 | 2 | 3 | 2 | 3 | none | none |
| `standing_transfer_amount` | 6 | 3 | 3 | 2 | 3 | none | none |
| `excess_fee_review_credit` | 4 | 2 | 2 | 2 | 3 | none | none |
| `surplus_transfer_amount` | 6 | 3 | 3 | 2 | 3 | none | none |

Some ladder `value`/`method` strings were rephrased (for example `refundable_pool_width`'s tiers now read
"the pool is …" where they read "the refundable fee pool is …"). The rephrasings are cosmetic; every tier's
condition and its value or method is still stated in its policy's `rule` prose, verified by reading the two
rewritten rules in full and by carrying forward revision 1's reading of the four unchanged ones.

**CG-9 — still standing, as the reworker states.** `instalment_pacing` is still `method` while
`moved_surplus_share` and `goodwill_share_step` are still `parameter`, all three selecting a multiplier.
No scored value turns on the labels. Observation.

### findings (revision_2)

| id | revision-1 verdict | revision-2 verdict | basis |
| --- | --- | --- | --- |
| CG-1 / F0-1 | `SOURCE-POLICY RED` | **CLOSED** | one uniform `float(int(x+0.5))` across all four tiers; identity with half-up proved for all reachable worlds, not just these seeds |
| CG-2 / F0-2 | `SOURCE-POLICY RED`, `SOURCE-FACTOR RED` | **CLOSED** | rule rewritten into two named stages; offending phrase gone from the charter; factor baseline now equals what `baseline.rule` states |
| CG-4 / F0-3 | `SOURCE-POLICY RED` | **CLOSED** | second `overwrite` entry, verbatim base sentence, retires exactly one gate; replacement stated in the rule and satisfied |
| CG-6 / F0-4 | observation | **CLOSED** | `condition` strengthened to "together cover" |
| CG-3 | observation | unchanged, still standing | policy byte-identical |
| CG-5 | observation | unchanged, still standing | framework window convention |
| CG-7 | observation | unchanged, still standing | sentence and policy scope still differ, coincide on the seed |
| CG-8 / F0-5 | observation | unchanged, still standing | `courtesy_limit` not retired; allowance still 2+2 |
| CG-9 | observation | unchanged, still standing | multiplier labels untouched |
| F0-6 / F1-4 | observation | unchanged, still standing | near-miss decisiveness, seeds unmoved |

**No new red light was found.** Three new observations, all **pre-existing** in revision 1's artifacts and
none introduced by this rework:

**R2-O1 — two compute bindings have no `compute_basis` entry.**
`savings_ext_promotional_interest_correction.compute` defines `new_money_three_month` and
`new_money_one_month` (each a subtraction over three bindings that do have entries), and neither name
appears in `compute_basis`. The quantity is grounded — the rule sentence "Qualifying new money is the
total of the deposits posted in those three calendar months other than internal transfers and automatic
transfers from another Piedmont Crescent Bank account" states exactly that subtraction — so no second
reading arises and no number moves. Recorded because check 2 asks for a quotation behind every quantity
and these two intermediates have none of their own. Missed in revision 1; present then too.

**R2-O2 — one `compute_basis` entry cites a dependency sentence instead of the definitional one.**
`savings_ext_relationship_bonus_correction.compute_basis["bonus_ledger_basis"]` quotes the policy's
**prerequisite** sentence ("The relationship bonus owed for a closed statement cycle is settled only after
the promotional interest due on that cycle's new money stands credited on the account") rather than the
sentence that defines the bonus ledger basis. The quotation is verbatim from the rule, so the mechanical
check passes, but it explains when the quantity is measured rather than what it is. The definitional
sentence is cited under `deposits_all`, `interest_all` and `withdrawals_all`, so the basis is reachable.
No consequence. Missed in revision 1; present then too.

**R2-O3 — `savings_ext_promotional_interest_correction` is only meaningful on the three money-market
tiers.** `P('promo_new_money_apy')` and `P('promo_balance_cap')` are the string `"not_offered"` on Starter
Savings, Statement Savings and Goal Builder Savings, so `MN(P('promo_balance_cap'), …)` would compare a
string with a float on those tiers. Neither task is affected (task 0 is Money Market Account, task 1 is
Premier Money Market and does not use this policy) and nothing in the charter directs the policy at a
tier without a promotion, so this is a latent scope question rather than a defect of either task. Missed
in revision 1; present then too.

## closing_checklist (revision_2)

**The difficulty closes out.** Both tasks' comparison sections carry PASS on all four relationships.

| Step 4 item | status |
| --- | --- |
| audit files one-to-one with the tasks, `_difficulty.md` alongside, old revisions traceable | yes — revision 1's text is untouched above and this section is appended below it |
| every comparison section carries a PASS | **yes** — `0.md` and `1.md` `## source_gt_comparison (revision_2)` both PASS on all four |
| extended policies fully covered, task scopes pairwise disjoint | yes — unchanged from revision 1; both `charter_scope` blocks still agree with the derived trees |
| task tools and GT closed | yes — six tools, each the `target_tool` of exactly one policy, each called exactly once across the two tasks |
| each task tool uses an independently generated, frozen uuid8 | yes — `task_tools.py` byte-identical, carried forward on hash |
| every tree: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 `owner=user` write, no cycle | yes — task 0: n=3, 3 `value_input`, `owner=user` root; task 1: n=1, 1 `value_input`, `owner=user` root |
| the difficulty's `prerequisite` edges are jointly a DAG | yes — two disjoint trees, no cross-task edge |
| every computation: self-sufficient baseline, 4–6 factors (2 of each effect, 2 multi-source, 2 cross-difficulty), ladders of ≥3 tiers stated in the rule, every factor load-bearing against an **honest** baseline, all-baseline ≠ gold | **yes** — 32 of 32 factors bear weight; `bonus_basis_netting`'s baseline now equals what `baseline.rule` states, which was the one exception in revision 1; all six all-baseline fall-backs (0.00, 0.00, 6.00, 155.37, 10.00, 5,000.00) differ from their golds |
| instantiation-stage gates re-run on the final form | the coordinator re-ran the full block after the rework and supplied the snapshot; cited, not re-run by this auditor. The base-gate count movement in it is accounted for above as a declared single-gate retirement |
