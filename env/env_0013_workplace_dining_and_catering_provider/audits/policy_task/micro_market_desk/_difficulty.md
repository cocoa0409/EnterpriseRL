# Policy-task audit — micro_market_desk / charter-global

## charter_global_frozen

- freeze time: 2026-09-22 (audit run), revision 1. Written **before** any task's GT field was read;
  nothing in this section is derived from a revealed GT.
- auditor: independent policy-task auditor (not the instantiating agent).
- freeze hashes (verified at the repository root with `sha256sum`):
  - `env/env_0013_workplace_dining_and_catering_provider/tasks/micro_market_desk/market.extended.yaml`
    = `f3e9f35d4b1517badcb63de77406079ed2b99c319e2ab42900506444a13945ea`
  - `env/env_0013_workplace_dining_and_catering_provider/tasks/micro_market_desk/task_tools.py`
    = `58bcd93e327f26bdc68bcfffb4629110e94d39d7209ab8fe5e39d0348c9aee0d`
- fields permitted for this section: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`,
  `blueprint/share_tools.py`, `blueprint/products/*.yaml`, the whole of `market.extended.yaml`,
  the whole of `task_tools.py`, and — for the per-task consequences cited from the task files only —
  each task's `frozen_time`, `user_scenario` and `initial_state` as delivered in the masked views.
- fields explicitly masked for this section: every task's `evaluation_criteria`, `computations`,
  `design_rationale`, `solvability_contract`, `prerequisite_closure`, `charter_scope`,
  `required_documents`, `db_closure`, `db_closure_matches_initial_state`.
- entry conditions: supplied with the brief and checked, not re-run — `check_extended.py`,
  `check_task_tools.py`, `replay_tasks.py --check`, `check_solvability.py`, `check_compute.py`,
  `check_grounding.py`, `check_cross_fire.py`, all green, with both masked-view hashes.
  `check_traceability.py` is legitimately absent (the KB has not been rendered). Input complete.

### policy_conflict_scan

The base section of `market.extended.yaml` (lines 1–688) is **byte-identical** to
`blueprint/products/market.yaml` (`diff` reports only a trailing blank line before
`extended_policies:`). Nine base policies, three measures, six variants and twelve event types
are carried verbatim.

Seven extended policies. Subjects, triggers and terminal states:

| policy | subject | trigger | computes | target tool | owner |
| --- | --- | --- | --- | --- | --- |
| `market_ext_kiosk_catch_up_drawdown` | `market_subsidy_drawdown_posted` | state_due | `subsidy_amount_usd` | `post_kiosk_catch_up_drawdown_96ce656f` | agent |
| `market_ext_period_settlement_true_up` | `market_monthly_settlement_invoiced` | state_due | `settlement_amount_usd` | `post_market_settlement_true_up_13e3670a` | agent |
| `market_ext_outage_service_credit` | `market_service_credit_issued` | state_due | `credit_amount_usd` | `issue_market_outage_credit_49294a76` | agent |
| `market_ext_settlement_payment_amount` | `market_settlement_payment_posted` | on_request | `payment_amount_usd` | `pay_market_settlement_invoice_693f0fba` | **user** |
| `market_ext_standby_period_settlement` | `market_monthly_settlement_invoiced` | state_due | `standby_settlement_usd` | `post_market_standby_settlement_ab27821d` | agent |
| `market_ext_lapsed_lot_settlement_credit` | `market_service_credit_issued` | state_due | `lapsed_lot_credit_usd` | `issue_lapsed_funding_credit_131d77d2` | agent |
| `market_ext_subsidy_funding_lot` | `market_subsidy_funding_posted` | on_request | `funding_amount_usd` | `fund_market_subsidy_lot_f6d53aaa` | **user** |

Two pairs share a `subject` (`market_monthly_settlement_invoiced`: true-up vs standby;
`market_service_credit_issued`: outage credit vs lapsed-funding credit). They do not conflict on
overlapping subjects: the true-up governs a period the market was open, the standby a period it
stood shut (`market_ext_standby_period_settlement.rule`: "No product settlement is raised for a
period the market stood shut, since nothing was rung at the kiosk"); the outage credit answers
kiosk hours, the lapsed credit answers expired funding. Eligibility, time anchors and cross-category
read boundaries are compatible throughout: every extended policy inherits its base state gate
(`settlement_state` installing/active/suspended, `fundable_state` installing/active/suspended,
`drawable_state` active/suspended, `payable_state` active/suspended/closed, `credit_claim_window`
and `shrink_dispute_window`), and no extended rule weakens one.

**Scope exclusivity and completeness.** Task 0's tree covers {`market_ext_settlement_payment_amount`,
`market_ext_period_settlement_true_up`, `market_ext_outage_service_credit`,
`market_ext_kiosk_catch_up_drawdown`}; task 1's covers
{`market_ext_subsidy_funding_lot`, `market_ext_lapsed_lot_settlement_credit`,
`market_ext_standby_period_settlement`}. 4 + 3 = 7, pairwise disjoint, jointly the whole
`extended_policies` list. No cross-task prerequisite reference exists in either direction.

Conflicts found in this scan are recorded under `### findings` (C-1 … C-5). The only conflict that
bears on a task's scored value is **C-2**, demonstrated in `1.md`.

### rule_compute_equivalence

Checked sentence by sentence, in both directions, over all seven policies.

*Forward (rule → compute).* Every quantity, window, filter, tier, branch, cross-category read,
acting base, grouping, cap/floor and rounding convention the rules state is carried by a
`compute_basis` entry that quotes a sentence of that policy's own `rule` verbatim, and is
implemented by a restricted expression. Mechanically verified: for all seven policies, every
sentence of every `compute_basis` value occurs verbatim in that policy's `rule` (0 exceptions), and
every sentence of every `baseline.rule` occurs verbatim in that policy's `rule` (0 exceptions).
Every non-fall-through tier of every declared ladder is likewise a sentence of the rule and a branch
of the `decides` binding, and every branch of every `decides` binding is a tier the rule states
(4 of 36 ladder `when` strings differ from the rule only by expanding the rule's anaphora — "over
those three months" written out as "over the three months to the day the settlement is raised" —
which is the same tier, not a missing one).

*Backward (compute → rule).* One binding has no warrant in its rule:

- `market_ext_settlement_payment_amount.compute.invoice_posted_date` =
  `LATEST('market_ledger','posted_date', date_field='posted_date', charge_code='equipment_fee')`,
  whose `compute_basis` quotes "Where the settlement invoice **the client is settling** still has at
  or above the early-settlement days to run before it falls due…". The rule anchors the clock on the
  invoice the client names; the compute anchors it on the most recent **equipment-fee** row anywhere
  on the ledger. These are two different objects, and `equipment_fee` appears nowhere in any rule of
  this charter. Recorded as C-4.

Rounding: every rule says "rounded half up to two decimal places"; the evaluator's `RND` is
Python `round`, i.e. banker's rounding. No figure in either task's derivation lands on an exact
half-cent, so the divergence is latent here; recorded as C-5.

### action_binding_and_uuids

Each `(target_tool, computes)` pair is claimed by exactly one policy: the seven `computes` names
(`subsidy_amount_usd`, `settlement_amount_usd`, `credit_amount_usd`, `payment_amount_usd`,
`standby_settlement_usd`, `lapsed_lot_credit_usd`, `funding_amount_usd`) and the seven target tools
are pairwise distinct, and no tool is named by two policies.

uuid8 tails: `96ce656f`, `13e3670a`, `49294a76`, `693f0fba`, `ab27821d`, `131d77d2`, `f6d53aaa`.
All seven are 8 hex digits, pairwise distinct, share no prefix, form no arithmetic or lexical
sequence, and none is another with a changed tail. Independently generated and frozen: PASS.

Tool docstrings add no confirmation, review, wait or procedure outside the policy, name no other
tool, and state no action's position in a sequence — with one exception, recorded as C-6: all seven
`market_agreement_id` Arg entries end "read it from the micro market agreement lookup **before**
calling", which carries an ordering word. It points at a share-tool read rather than at another
problem's write, so it leaks no part of the problem tree; observation only.

Every function body is a `ctx.make_id` → `ctx.find(_AGREEMENTS, …)` → `ctx.create(_LEDGER, …)` →
formatted-return sequence. There is no `if`, no `raise`, no status inspection and no hint in any of
the seven, so no tool judges a prerequisite.

The docstrings do, however, assert business effects the code does not perform — recorded as C-3.

### prerequisite_graph

All seven policies fill in `prerequisite` (`[]` on `market_ext_kiosk_catch_up_drawdown` and
`market_ext_standby_period_settlement`). Six edges:

| blocked policy | problem | kind | gate | form | resolved_by |
| --- | --- | --- | --- | --- | --- |
| `market_ext_period_settlement_true_up` | `market_ext_kiosk_catch_up_drawdown` | value_input | `window_subsidy` | state | `post_kiosk_catch_up_drawdown_96ce656f` |
| `market_ext_outage_service_credit` | `market_ext_period_settlement_true_up` | value_input | `settlement_base` | state | `post_market_settlement_true_up_13e3670a` |
| `market_ext_settlement_payment_amount` | `market_ext_period_settlement_true_up` | value_input | `charges_side` | state | `post_market_settlement_true_up_13e3670a` |
| `market_ext_settlement_payment_amount` | `market_ext_outage_service_credit` | value_input | `credits_recent` | state | `issue_market_outage_credit_49294a76` |
| `market_ext_lapsed_lot_settlement_credit` | `market_ext_standby_period_settlement` | value_input | `settlement_base` | state | `post_market_standby_settlement_ab27821d` |
| `market_ext_subsidy_funding_lot` | `market_ext_lapsed_lot_settlement_credit` | value_input | `drawable_balance` | state | `issue_lapsed_funding_credit_131d77d2` |

Every `problem` points at another extended policy id in this file, never at a base policy and never
at itself. The graph is acyclic (topological order: catch-up drawdown → true-up → outage credit →
payment; standby settlement → lapsed credit → funding lot), and the two components are disjoint, so
no cycle can arise across tasks. Every `policy_source` is verbatim locatable in the **blocked**
policy's own `rule` (mechanically verified, 6/6) and appears in no depended-on rule (0/6). `form` is
`state` on all six and no `fallback_reason` is present anywhere, which is correct — the state form
has priority and no action-form fallback is claimed. Every `gate` names a binding that genuinely
exists in the blocked policy's `compute` and is an input rather than `result`, so `kind:
value_input` is honest in all six cases. Every `resolved_by` is the depended-on policy's own
`target_tool`. No authoring-viewpoint phrasing ("in this task", "at the opening", "the current
world") appears in any `prerequisite` block.

`condition` against the sentence it is derived from: five of six are neither strengthened nor
weakened. The sixth — `market_ext_lapsed_lot_settlement_credit`'s condition "the market ledger
carries the settlement charge for the period the market stood shut on the agreement" — is broader
than the sentence's "the settlement charged for the period the market stood shut", because the
ledger's `market_monthly_settlement_invoiced` family also carries `equipment_fee` and
`restocking_fee` rows. Recorded as C-7; demonstrated against task 1's world in `1.md`.

### prerequisite_sentences

Four-point test on each of the six sentences:

1. **true-up ← catch-up**: "The settlement invoiced for a period is not worked out **before** the
   agreement's drawdown record carries the client discount owed for every kiosk trip the till failed
   to meet." Ordering connective *before*; waits on a record-visible state (the drawdown record on
   the market ledger); names no tool, policy id, snake_case token or row id; scope matches the
   condition. The one write of this difficulty that brings it about is
   `post_kiosk_catch_up_drawdown_96ce656f` (the only write producing a
   `market_subsidy_drawdown_posted` row). Single reading. PASS.
2. **outage credit ← true-up**: "The credit allowed for a settlement period is fixed only **after**
   the product settlement for that period stands charged on the agreement." Ordering connective
   *only after*; record-visible state; the one write is
   `post_market_settlement_true_up_13e3670a` — `post_market_standby_settlement_ab27821d` also writes
   a `market_monthly_settlement_invoiced` row, but its own rule says "No **product** settlement is
   raised for a period the market stood shut", so "the product settlement" resolves to the true-up
   alone. Single reading. PASS.
3. **payment ← true-up**: "The amount tendered against a settlement invoice is not settled
   **before** the product settlement for that period stands charged on the agreement." Same
   analysis as 2. PASS.
4. **payment ← outage credit**: "The amount tendered against a settlement invoice is not settled
   **before** the credit owed for the hours the kiosk could not take a payment stands allowed
   against that invoice." Ordering connective *before*; names no tool or id. **It fails the
   record-visibility half of the state form**: `market_ledger` records no field that separates an
   outage credit from any other service credit — `issue_market_outage_credit_49294a76` and
   `issue_lapsed_funding_credit_131d77d2` both write `event_type=market_service_credit_issued`,
   `charge_code=service_credit`, `product_category=other` and leave `source_reference` unset, and
   `db_schema.market_ledger.charge_code` offers no finer value. The state "a credit **for the hours
   the kiosk could not take a payment**" is therefore not a state the tables and finders can name.
   Recorded as C-1; demonstrated against task 0's world in `0.md` (two defensible readings,
   693.31 vs 806.06).
5. **lapsed credit ← standby settlement**: "The credit handed back for a lapsed funding lot is fixed
   only **after** the settlement charged for the period the market stood shut stands on the
   agreement." Ordering connective *only after*; the one write is
   `post_market_standby_settlement_ab27821d` (`post_market_settlement_true_up_13e3670a` is for a
   period the market was open). The `condition` restating it is broader than the sentence — C-7.
6. **funding lot ← lapsed credit**: "The lot the client pays in is not fixed **before** the funding
   handed back to the client on a settlement stands credited on the agreement." Same
   record-visibility weakness as 4 (C-1), and the compute reads it as
   `credits_all = SUM('market_ledger','amount_usd', event_type='market_service_credit_issued')`,
   i.e. **every** service credit including outage credits, which are not "funding handed back".
   Recorded as C-8. No consequence is demonstrable on task 1's world (its seed carries no service
   credit at all).

No rule carries a second wording of a dependency, another problem's tool name, another policy's id,
or an aggregated chain; no depended-on rule restates a blocked rule's sentence; a full scan of every
extended rule for ordering connectives (`before`, `after`, `until`, `first`, `prior to`, `only
once`) returns exactly the six sentences above plus ordinary within-formula sequencing ("the
prompt-settlement discount is **then** taken off what is left") and calendar phrases ("what was paid
in **before** the twelve months"). No base rule sentence grounds any declared edge.

### override_declarations

Sentence by sentence against each policy's `base_policy_refs`. Findings only; the consequence of
each is demonstrated in the task file it bears on.

| extended policy | base refs | declared `overwrite` | undeclared deviations found |
| --- | --- | --- | --- |
| `market_ext_kiosk_catch_up_drawdown` | `market_subsidy_drawdown_rules`, `market_combination_dining_interaction` | the `percent_discount` share clause | **C-9** (daily ceiling: base pools it with the cafe's, extended uses the market's own), **C-10** (base's `fixed_per_visit` branch dropped, and the extended compute is undefined for the formats that carry it) |
| `market_ext_period_settlement_true_up` | `market_agg_portfolio_settlement_band`, `market_settlement_terms`, `market_combination_dining_interaction` | the subsidy-true-up basis clause | **C-11** (base's sales-shortfall charge), **C-12** (portfolio band not applied) |
| `market_ext_outage_service_credit` | `market_service_credit_terms` | the per-hour credit clause | none: the uptime-guarantee bar, the claim window, the client-cause exclusion and the period ceiling are all inherited and none is weakened |
| `market_ext_settlement_payment_amount` | `market_settlement_payment_terms` | the part-payment clause | none: due date, grace, late charge, late cap and credit-hold threshold are untouched by this policy and remain in force |
| `market_ext_standby_period_settlement` | `market_agg_portfolio_settlement_band`, `market_settlement_terms`, `market_combination_dining_interaction` | the standby-charge clause | **C-12** (portfolio band not applied) |
| `market_ext_lapsed_lot_settlement_credit` | `market_service_credit_terms` | the kiosk-outage trigger clause | **C-2** (the lot-expiry sentence of `market_subsidy_funding_terms` — a base policy this entry does not even cite) |
| `market_ext_subsidy_funding_lot` | `market_subsidy_funding_terms` | the minimum-lot clause | none: the lot-expiry, state and same-site sentences are inherited and the minimum-lot floor is re-stated in the extended rule |

`overwrite: []` appears nowhere in this charter; every policy declares at least one replacement.

### factor_ladders

Structure only. Whether a factor bears weight is a fact about one world and lives in the task files
(`0.md` / `1.md`, § `factor_weight`).

| policy | factors | `parameter` | `method` | multi-source tiers | `cross_difficulty` |
| --- | --- | --- | --- | --- | --- |
| `market_ext_kiosk_catch_up_drawdown` | 4 | 2 | 2 | all non-fall-through tiers | `pooled_dining_share` → cafe |
| `market_ext_period_settlement_true_up` | 5 | 3 | 2 | all non-fall-through tiers | none |
| `market_ext_outage_service_credit` | 5 | 3 | 2 | all non-fall-through tiers | none |
| `market_ext_settlement_payment_amount` | 5 | 3 | 2 | all non-fall-through tiers | `group_settlement_offset` → cafe |
| `market_ext_standby_period_settlement` | 4 | 3 | 1 | all non-fall-through tiers | `management_fee_share` → cafe |
| `market_ext_lapsed_lot_settlement_credit` | 5 | 3 | 2 | all non-fall-through tiers | none |
| `market_ext_subsidy_funding_lot` | 5 | 3 | 2 | all non-fall-through tiers | none |

Every policy declares 4–6 factors with ≥ 2 `parameter` and ≥ 1 `method`; every ladder has exactly
three tiers, the fall-through counted; the two non-fall-through tiers of every ladder are, as
stated, pairwise disjoint (each pair differs on the second conjunct or on a strict
above/below split, and the evaluation order in `compute` matches the rule's order); every ladder's
`decides` is an input binding and never `result`; every factor's `bindings` set is disjoint from
the other factors' of the same policy; and every fall-through tier's outcome is exactly the sentence
`baseline.rule` states for that input. No two tiers of any ladder select the same value or method —
checked value by value across all 21 ladders (e.g. 97/103/100, 60/80/100, 2.0/4.0/0.0, ×1.5/×0.75/×1,
+2.5/−5.0/0.0, 100/85/95, 35/18/25, 5/15/10).

Labels are honest: every factor labelled `method` changes the algorithm (which window the aggregate
is taken over, whether hours are halved or netted against declines, whether a charge is apportioned
or flat, whether the whole, half or none of a balance is offset), and every factor labelled
`parameter` substitutes a number into an unchanged formula. Every `method` tier names a computation
the charter states in the same policy's rule.

**Three ladders are not real, in the specific sense that a part of a tier's compound condition holds
of every customer who can reach that write, so that a tier of the ladder is unreachable in this
charter:** recorded as **C-13** and demonstrated against task 1's world in `1.md`.

Counts per task (over the task's computations): task 0 — 19 factors, ≥ 1 multi-source, 2
cross-difficulty (cafe); task 1 — 14 factors, ≥ 1 multi-source, 1 cross-difficulty (cafe). Both meet
the floors. Both tasks seed the cafe holding and the cafe ledger rows their cross-difficulty factors
read (`0.md` and `1.md` name the rows).

### findings

**C-1 — SOURCE-POLICY RED — the "outage credit" state is not record-visible, so two prerequisite
edges wait on a state the records cannot show.**
*Symptom.* The prerequisite sentences of `market_ext_settlement_payment_amount` ("…before the credit
owed for the hours the kiosk could not take a payment stands allowed against that invoice") and of
`market_ext_subsidy_funding_lot` ("…before the funding handed back to the client on a settlement
stands credited on the agreement") are declared `form: state`, but the state each names cannot be
read off any record.
*Root cause.* `issue_market_outage_credit_49294a76` and `issue_lapsed_funding_credit_131d77d2`
(`tasks/micro_market_desk/task_tools.py`) write identical rows apart from the amount:
`event_type="market_service_credit_issued"`, `charge_code="service_credit"`,
`product_category="other"`, `payment_channel="not_applicable"`, and neither sets
`source_reference`. `blueprint/db_schema.json` → `market_ledger.charge_code` has a single
`service_credit` value for both.
*Evidence.* Both tool bodies, lines of `task_tools.py` cited above; the schema entry; the base event
declaration `market_service_credit_issued.fields.source_reference: "the service request the credit
answers"`, which both tools leave empty.
*Demonstrated consequence.* Bears on task 0, where `initial_state.market_ledger`
`5e31eac9-3b8d-4116-9b2d-74cbb2b7cb8b` is a `service_credit` of 45.00 against the very invoice the
customer is settling: see `0.md` § `findings` F-0-1 for the two readings and the two payment
figures. On task 1 no consequence is demonstrable (that seed carries no service credit at all).
*Affected artifact.* `market.extended.yaml` → `market_ext_settlement_payment_amount.prerequisite[1]`
and `market_ext_subsidy_funding_lot.prerequisite[0]`; `task_tools.py` →
`issue_market_outage_credit_49294a76`, `issue_lapsed_funding_credit_131d77d2`;
`db_schema.json` → `market_ledger.charge_code`.

**C-2 — SOURCE-POLICY RED — undeclared override of the base lot-expiry rule.**
*Symptom.* Base and extended reach different answers to "has this funding lot lapsed?".
*Root cause.* `blueprint/products/market.yaml` → `market_subsidy_funding_terms.rule`: "A lot stays
drawable for **the number of months printed against the market format**, counted from the day the
funding cleared, and lapses at the end of that period with the unspent balance credited on the next
settlement invoice." `market_ext_lapsed_lot_settlement_credit.rule` tier 1: "Where the market format
keeps a funding lot drawable for below the long drawable life and the agreement carries at or above
the repeat funding count of funding lots, the lapsed funding is what was paid in **before the six
months** to that day." The `overwrite` block of that policy names only
`market_service_credit_terms`; `market_subsidy_funding_terms` is not even in its `base_policy_refs`.
*Evidence.* The two quoted sentences; `overwrite:` of `market_ext_lapsed_lot_settlement_credit`
(one entry, `base_policy: market_service_credit_terms`).
*Demonstrated consequence.* Task 1: `subsidy_funding_lot_expiry_months` = 12 for Smart Store, so
under base only the lot cleared 2025-04-18 has lapsed (6 500.00) and the lot cleared 2026-01-15
stays drawable until 2027-01-15; under extended, everything paid in before 2026-03-22 is lapsed
(13 000.00). See `1.md` § `findings` F-1-3 for the two credit figures and the two root figures.
*Affected artifact.* `market.extended.yaml` → `market_ext_lapsed_lot_settlement_credit.overwrite`,
`.base_policy_refs`, `.rule` (the `lapsed_funding` ladder) and `.compute.lapsed_funding`.

**C-13 — SOURCE-FACTOR RED — three ladders whose tiers no customer of this desk can reach.**
*Symptom.* A part of a compound condition holds of every customer who reaches the write, so the
ladder divides nobody on that part and one of its three tiers is dead.
*Root cause and evidence.*
 (a) `market_ext_lapsed_lot_settlement_credit.params.long_drawable_life_months: 18` and
 `market_ext_subsidy_funding_lot.params.long_drawable_life_months: 18`, against
 `blueprint/products/market.yaml` `subsidy_funding_lot_expiry_months` = 6 / 9 / 12 / 12 / 12 / 12
 across the six formats — the maximum is 12. Therefore "the market format keeps a funding lot
 drawable for **below** the long drawable life" is true of **all six** formats
 (`lapsed_funding_window` tiers 1 and 2), so that ladder's fall-through — which is also its declared
 `baseline` (`MX(RND(funding_all - funding_12m,2),0.0)`) — is unreachable; and "**at or beyond** the
 long drawable life" (`cover_period_basis` tier 1) is reachable by no format at all.
 (b) `market_ext_subsidy_funding_lot` `kiosk_handling_step`: both non-fall-through tiers require
 "the market format takes the mobile wallet at the kiosk". `mobile_pay_enabled` is false for exactly
 one format, Cooler & Snack Wall — and Cooler & Snack Wall is the one format whose `subsidy_model`
 is `none`, which base `market_subsidy_funding_terms.rule` says "takes no funding at all". So every
 agreement that can reach a `market_subsidy_funding_posted` write has `mobile_pay_enabled` true, the
 condition divides no customer, and the ladder's fall-through (declared `baseline` `0.0`) is dead.
*Demonstrated consequence.* Task 1 sits on `lapsed_funding_window` tier 1, `cover_period_basis`
tier 2 and `kiosk_handling_step` tier 1 — i.e. on the live half of each ladder — and no world this
charter admits could place a customer on the dead tier. See `1.md` § `factor_weight` and § `findings`
F-1-1. Task 0 uses none of the three ladders.
*Affected artifact.* `market.extended.yaml` →
`market_ext_lapsed_lot_settlement_credit.params.long_drawable_life_months`, `.factors[0].ladder`;
`market_ext_subsidy_funding_lot.params.long_drawable_life_months`, `.factors[0].ladder`,
`.factors[4].ladder`.

**C-3 — observation — tool docstrings assert balance effects their code never performs.**
All seven tools in `task_tools.py` state an effect on the agreement's running quantities — e.g.
`post_market_settlement_true_up_13e3670a`: "the client's unsettled balance grows by the amount
given … the balance owing on the agreement rises accordingly"; `fund_market_subsidy_lot_f6d53aaa`:
"the agreement's spendable subsidy funding grows by the amount paid in". None of the seven calls
`ctx.update` on `market_agreements`; each only creates a `market_ledger` row. Recomputed on task 0's
replayed world, `market_agreements.receivable_balance_usd` is 1016.15 before and after all four
writes; on task 1, `subsidy_pool_balance_usd` is 495.00 before and after all three. No consequence
is demonstrable on either world, because the policies that read these fields
(`unsettled_balance`, `unspent_funding`) read them at a step where the seed value is also the value
GT uses, and both tier boundaries (`subsidy_funding_minimum_usd`) sit far from the moved figure —
but the contracts and the code disagree.

**C-4 — observation — `invoice_posted_date` anchors on a charge code the rule never names.**
See § `rule_compute_equivalence`. On task 0 the latest `equipment_fee` row (2026-09-10,
`INV-MK-440318`) happens to be the invoice the customer is settling, so the two readings coincide
and no second answer follows; on task 1 the policy is not used.

**C-5 — observation — "rounded half up" vs the evaluator's banker's rounding.** Every extended rule
says "rounded half up to two decimal places"; the compute evaluator's `RND` is Python `round()`,
i.e. banker's rounding. No *scored* figure in either task lands on an exact half-cent, but the
divergence is live, not merely latent: task 1's `market_ext_lapsed_lot_settlement_credit` has
`period_ceiling` = 5653.70 × 25 % = 1413.425, which the rule makes **1413.43** and the compute makes
**1413.42** — and `tasks/1.json` → `computations[1].factor_trace[5]` states the rule's figure,
1413.43, while the binding holds the other. The ceiling does not bite at either value, so no scored
value moves. See `1.md` § `source_gt_comparison`.

**C-6 — observation — ordering word in all seven docstrings.** "read it from the micro market
agreement lookup **before** calling". It points at a share-tool read, not at another problem's
write, so it discloses no part of the problem tree.

**C-7 — observation — one `condition` broader than its sentence.**
`market_ext_lapsed_lot_settlement_credit.prerequisite[0].condition` says "the market ledger carries
**the settlement charge** for the period the market stood shut", while the sentence says "the
settlement **charged** for the period the market stood shut". The `market_monthly_settlement_invoiced`
family also carries `equipment_fee` and `restocking_fee` rows, so read literally the condition can be
met by a charge that is not the standing charge. See `1.md` F-1-2.

**C-8 — observation — `credits_all` counts credits that are not "funding handed back".**
`market_ext_subsidy_funding_lot.compute.credits_all` sums every `market_service_credit_issued` row
ever posted, although the rule sentence it quotes says "less what has been **handed back to the
client on a settlement**". An outage credit issued under `market_ext_outage_service_credit` would
reduce "the funding still drawable" although it hands back no funding. Not demonstrable on task 1
(no service credits are seeded there).

**C-9 — observation — undeclared override of the pooled daily ceiling.**
`market_combination_dining_interaction` (a declared `base_policy_ref` of
`market_ext_kiosk_catch_up_drawdown`): "Where the same client holds an active workplace cafe
management contract at the site the market stands in, the two subsidy pools are read as one for the
employee daily ceiling, and **the ceiling printed against the cafe service model governs both
outlets together** rather than each separately." The extended rule instead says the discount "is
held to the daily ceiling printed against **the market format**", and
`compute.result = RND(MN(discount_owed, P('subsidy_cap_per_employee_per_day_usd')), 2)`. The
`overwrite` block names only `market_subsidy_drawdown_rules`. On task 0 the client does hold an
active Full Service Cafe at the same site `CS-418` (cafe ceiling 7.25 vs market ceiling 5.50), but
the computed discount is 2.62, so neither ceiling binds and no second answer follows.

**C-10 — observation — base's `fixed_per_visit` branch is dropped and the extended compute is
undefined for the formats that carry it.** `market_subsidy_drawdown_rules.rule`: "a
`fixed_per_visit` model meets a flat amount once per shopping visit". No extended rule states a
`fixed_per_visit` branch, and
`market_ext_kiosk_catch_up_drawdown.compute.trip_shelf_value = RND(basket_value /
(P('subsidy_pct_of_shelf_price') / 100), 2)` — together with
`market_ext_period_settlement_true_up.compute.shelf_sales` — divides by
`subsidy_pct_of_shelf_price`, which is 0.00 for Expanded Campus Micro Market (`subsidy_model:
fixed_per_visit`) and for Cooler & Snack Wall (`subsidy_model: none`). In the same situation base
yields a flat per-visit amount and the extended compute yields no number at all. Neither task
instantiates such a format, so no task verdict turns on this.

**C-11 — observation — base's sales-shortfall charge has no route.**
`market_settlement_terms.rule`: "Where sales for the period fall short of the sales guarantee
printed against the market format, the shortfall share printed against that format is invoiced to
the client". No extended policy mentions it and no task tool can write it. On task 0's world the
shelf value of the quarter's trips is 103.55 against a `monthly_sales_guarantee_usd` of 7 800.00, so
base would have a very large shortfall charge falling due on the same invoice. The extended
overwrite replaces only the true-up basis clause, so the shortfall sentence stays in force with
nothing to execute it.

**C-12 — observation — the portfolio settlement band is never applied.**
`market_agg_portfolio_settlement_band` is a declared `base_policy_ref` of both
`market_ext_period_settlement_true_up` and `market_ext_standby_period_settlement`, and it discounts
"the management fee and the equipment lease". Neither extended compute applies a band and neither
`overwrite` names it. On both tasks the client holds one market agreement, so the ladder step is 1
and the discount is 0.00 % — no consequence.


## closing_checklist

Written after both tasks' `source_gt_comparison` sections were completed. **This difficulty cannot
be closed out**: two of the four relationships fail on task 0 and two fail on task 1, so the Step 4
checklist is recorded as a status rather than as a sign-off.

| Step 4 item | status |
| --- | --- |
| per-task audit files correspond one-to-one with the tasks, `_difficulty.md` alongside them, old revisions traceable | **met** — `0.md`, `1.md`, `_difficulty.md`; revision 1, no prior revision exists |
| every comparison section carries a PASS | **not met** — `0.md` records SOURCE-CHAIN RED and SOURCE-TASK RED; `1.md` records SOURCE-POLICY RED and SOURCE-FACTOR RED |
| this difficulty's extended policies fully covered, the M task scopes pairwise disjoint (each spanning its whole tree) | **met** — 4 + 3 = 7 policies, disjoint, complete; `charter_scope` of both tasks confirms it |
| task tools and GT closed | **met** — 7 task tools, each claimed by exactly one policy, all seven used across the two tasks |
| each task tool uses an independently generated, frozen uuid8 | **met** — § `action_binding_and_uuids` |
| every task's tree has 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥ 1 `owner=user` problem, no cycle | **met in structure** — task 0: n = 3, 4 value_input edges, root owned by the user; task 1: n = 2, 2 value_input edges, root owned by the user. **But task 0's fourth edge is not in fact unmet at the opening on the records (C-1 / `0.md` F-0-1).** |
| the difficulty's `prerequisite` edges together are a DAG, with no cycle created by cross-task references | **met** — two disjoint acyclic components, no cross-task reference |
| every computation declares a self-sufficient baseline and 4–6 factors (2 `parameter`, 1 `method`; per task ≥ 1 multi-source and ≥ 1 cross-difficulty) | **met** — § `factor_ladders`; task 0 has two cross-difficulty factors, task 1 one, all reading seeded cafe rows |
| every ladder ≥ 3 tiers stated in full in its rule, tiers distinct in outcome, conditions and outcomes ones the line of business actually holds | **not met** — C-13: three ladders carry a tier no customer of this charter can reach, so they divide customers on two tiers, not three |
| every factor proved to bear weight on its task's world against an honest baseline, baseline alone giving a definite number different from gold | **met** — all 33 factors across the two tasks move the scored value; all seven whole-baseline figures differ from gold (3.05, 33.02, 70.49, 40.61, 1920.00, 0.00, 2914.22) |
| instantiation-stage gates re-run once on the final form | **not run.** The artifacts have not changed since the snapshot supplied with the brief (both freeze hashes re-verified at the end of this audit), and `replay_tasks.py` rewrites task files, which is outside this audit's write domain. Re-running belongs to the rework that these findings call for, not to this pass. |

**Difficulty verdict: FAIL.** Four red lights, in two classes that a fix must address separately:

1. **C-1** — the charter waits, twice, on a state (`a service credit for the hours the kiosk could
   not take a payment` / `funding handed back to the client on a settlement`) that `market_ledger`
   cannot record, because both credit-writing tools emit the same `charge_code` and leave
   `source_reference` empty. Demonstrated on task 0: 693.31 vs 806.06.
2. **C-2** — `market_ext_lapsed_lot_settlement_credit` overrides the base lot-expiry rule without
   declaring it, and without even citing the base policy. Demonstrated on task 1: 1329.22 vs 669.22
   and 8548.51 vs 8218.51.
3. **C-13** — `long_drawable_life_months: 18` against a charter maximum of 12, and the mobile-wallet
   condition against the one format that can never be funded, leave three ladders with a dead tier
   apiece. Demonstrated on task 1.
4. **`0.md` F-0-2** — one seeded `market_service_intake` row is scored both as the missed kiosk trip
   and as an approved outage hour. Demonstrated on task 0: 224.68 vs 204.85, 693.31 vs 704.80.

Everything else this audit could check held: the base copy is byte-identical, `rule`↔`compute` is
lossless in both directions bar C-4, every prerequisite sentence is verbatim in its own blocked
rule and nowhere else, the six edges are all `value_input` and all load-bearing, both roots are the
customer's own write, no write waits on a real-world event, no tool judges a prerequisite, and the
independent derivation reproduced **all seven gold values and all 33 factor-sensitivity figures
exactly**.

---

## revision_2

### charter_global_frozen (round 2)

- freeze time: 2026-09-22 (round-2 run). Revision 1 above is untouched.
- Both shared sources moved, so **this section is re-derived in full** rather than carried forward:
  - `market.extended.yaml` `588cc9207f139d451c2cc62332dd4e508fbdf6c0325501f049778087a3f4526f`
    (round 1 `f3e9f35d…`)
  - `task_tools.py` `a085595de8e3f269d53951de4dc361c13a79aa20cdffbc78fc6dd228b125bd11`
    (round 1 `58bcd93e…`)
- Both masked worlds moved as well (`edfec694…`, `3f1e702c…`), so every per-task conclusion is
  re-derived in `0.md` / `1.md` § `revision_2`.
- Independence disclosure: round-1 GT was read at the end of revision 1, so this round is not a
  blind audit. Round-2 GT was opened only after both task files' `revision_2` derivations were on
  disk.
- Entry conditions checked, not re-run: the coordinator's gate block is complete and green
  (`EXTENDED OK`, `TASK TOOL CONTRACT OK`, `REPLAY OK`, `SOLVABILITY OK`, `COMPUTE OK`,
  `GROUNDING OK`, `SCOPE OK`) with the new addition `BASE FROZEN OK (10 files verified by hash)`.
  Independently re-verified here: lines 1–688 of `market.extended.yaml` are byte-identical to
  `blueprint/products/market.yaml` (`diff` reports only the trailing blank line).

### policy_conflict_scan (round 2)

Still seven extended policies, the same seven `computes` names and the same seven target tools with
the same uuid8 tails (`96ce656f`, `13e3670a`, `49294a76`, `693f0fba`, `ab27821d`, `131d77d2`,
`f6d53aaa`) — pairwise distinct, no shared prefix, no sequence. `(target_tool, computes)` is claimed
by exactly one policy each. Task scopes are unchanged: 4 + 3 = 7, pairwise disjoint, jointly
complete.

The two same-subject pairs are now separated by a **record-visible** field as well as by their
rules:

- `market_monthly_settlement_invoiced`: the true-up covers a trading period, the standby a shut one
  ("No product settlement is raised for a period the market stood shut").
- `market_service_credit_issued`: `market_ext_outage_service_credit.rule` — "The credit is recorded
  against **the kiosk** whose lost hours it answers"; `market_ext_lapsed_lot_settlement_credit.rule`
  — "The credit is recorded against **no kiosk**, since it hands back funding rather than answering
  kiosk time". Both sentences are carried in the respective `baseline.rule` too, both tools
  implement them (`kiosk_reference=parent.get("kiosk_reference","")` vs `kiosk_reference=""`), and
  `find_market_ledger` returns the field and names it in its docstring.

Eligibility, time anchors and cross-category read boundaries carry no new conflict; every extended
policy still inherits its base state gate unweakened.

### rule_compute_equivalence (round 2)

Mechanically re-verified over all seven policies: every sentence of every `compute_basis` value and
every sentence of every `baseline.rule` occurs verbatim in that policy's own `rule` (0 exceptions),
every non-fall-through ladder tier is a sentence of the rule and a branch of its `decides` binding,
and every branch of every `decides` binding is a tier the rule states.

Backward sweep — the one round-1 exception is now warranted. The payment rule carries a new
sentence, *"The day the invoice was raised is read from the **equipment line** the settlement
invoice carries, the equipment lease being raised with the invoice itself"*, which is the basis
`invoice_posted_date` (`charge_code='equipment_fee'`) was missing in round 1.

Rounding now agrees in both faces: every rule and every `baseline.rule` says "rounded to the nearest
cent, a figure falling exactly on the half-cent going to the nearest even cent", which is exactly
what the evaluator's `RND` (Python `round`) does, and every tool docstring's amount Arg repeats it.

### action_binding_and_uuids (round 2)

uuid8s as above: independently generated, frozen, unreused, not batch-derived. Every tool body is
`make_id` → `find(_AGREEMENTS,…)` → `create(_LEDGER,…)` → `update(_AGREEMENTS,…)` → formatted return,
with no branch, no raise and no status test, so no tool judges a prerequisite. The `ctx.update`
calls are new (round 1's C-3) and are unconditional arithmetic on the agreement's running
quantities: `subsidy_pool_balance_usd` −/+ for drawdown/funding, `receivable_balance_usd` +/− for
settlement charges, credits and payments.

Docstrings state no sequence and name no other tool, **except one residual**: six of the seven
`market_agreement_id` Arg entries now read "as returned by the micro market agreement lookup", but
`post_kiosk_catch_up_drawdown_96ce656f` (line 31) still reads "read it from the micro market
agreement lookup **before** calling". Recorded as **C-6 (round 2: not closed)**.

### prerequisite_graph (round 2)

Same six edges, all `value_input`, all `form: state`, no `fallback_reason` anywhere (correct — no
action-form edge is claimed). Every `problem` points at another extended policy id in this file; the
graph is acyclic and splits into the same two disjoint components, one per task. Every
`policy_source` is verbatim locatable in the **blocked** policy's own `rule` and in no depended-on
rule (mechanically verified 6/6, 0 leaks). Every `gate` names an input binding that exists in the
blocked policy's compute; every `resolved_by` is the depended-on policy's own `target_tool`.

Two `condition` strings were rewritten and both now match their sentence exactly rather than
exceeding it:

- payment ← outage credit: "…a service credit against that settlement invoice **that names the
  kiosk** whose lost hours it answers" (was: any service credit against that invoice);
- lapsed credit ← standby: "a **monthly settlement charge** raised for the period the market stood
  shut" (was: "the settlement charge", which the `equipment_fee` and `restocking_fee` rows of the
  same event family also satisfied).

`market_ext_subsidy_funding_lot`'s condition likewise now names the field: "a service credit on the
agreement **that names no kiosk**".

### prerequisite_sentences (round 2)

Four-point test on all six. All six join the blocked policy's own result to what it waits on with an
explicit ordering connective (*before* ×4, *only after* ×2), name no tool, policy id, snake_case
token or row id, and are written at the scope their `condition` carries. All six are state-form, and
for each exactly one write of this difficulty brings the waited-on state about:

| edge | waited-on state | the one write |
| --- | --- | --- |
| true-up ← catch-up | the drawdown record carries the discount for every trip the till failed to meet | `post_kiosk_catch_up_drawdown_96ce656f` (the only writer of `market_subsidy_drawdown_posted`) |
| outage credit ← true-up | the **product** settlement for the period stands charged | `post_market_settlement_true_up_13e3670a` (the standby policy's own rule disclaims a product settlement) |
| payment ← true-up | same | same |
| payment ← outage credit | a service credit **naming the kiosk** stands against that invoice | `issue_market_outage_credit_49294a76` (the other credit writer records no kiosk, by its own rule and its code) |
| lapsed credit ← standby | a **monthly settlement charge** for the shut period stands | `post_market_standby_settlement_ab27821d` |
| funding lot ← lapsed credit | a service credit **naming no kiosk** stands | `issue_lapsed_funding_credit_131d77d2` |

The two edges that in round 1 waited on a state no record could show (round-1 **C-1**) now wait on
`market_ledger.kiosk_reference`, a field the schema declares, the tools set deterministically, the
rules state on both sides, and `find_market_ledger` returns. **C-1 closed.**

A full scan of all seven rules for ordering connectives returns exactly these six sentences plus
within-formula sequencing and calendar phrases; no rule states a cross-problem order that grounds no
declared edge, and no base rule sentence grounds any edge.

### override_declarations (round 2)

| policy | base refs | `overwrite` entries | round-2 finding |
| --- | --- | --- | --- |
| `market_ext_kiosk_catch_up_drawdown` | `market_subsidy_drawdown_rules`, `market_combination_dining_interaction` | **2** — the `percent_discount` share clause **and** (new) "the ceiling printed against the cafe service model governs both outlets together" → "the discount so obtained is held to the daily ceiling printed against the market format" | **C-9 closed.** Residual: base's `fixed_per_visit` clause — see C-10 |
| `market_ext_period_settlement_true_up` | unchanged | **2** — the true-up basis clause **and** (new) the sales-shortfall clause → "No shortfall charge is invoiced on a subsidy true-up basis" | **C-11 closed.** The portfolio band needs no overwrite here: base itself says "subsidy true-up … carry no portfolio discount" — **C-12 closed for this policy by agreement** |
| `market_ext_outage_service_credit` | unchanged | 1 | none |
| `market_ext_settlement_payment_amount` | unchanged | 1 | none |
| `market_ext_standby_period_settlement` | unchanged | **2** — the standby clause **and** (new) the portfolio-band clause → "No portfolio discount is taken off a settlement raised for a period the market stood shut" | **C-12 closed** |
| `market_ext_lapsed_lot_settlement_credit` | **`market_service_credit_terms`, `market_subsidy_funding_terms`** (base policy added) | 1 | **C-2 closed by agreement, not by declaration** — verified below |
| `market_ext_subsidy_funding_lot` | unchanged | 1 | none |

**C-2 verified on the merits.** Base `market_subsidy_funding_terms.rule`: *"A lot stays drawable for
the number of months printed against the market format, counted from the day the funding cleared,
and lapses at the end of that period with the unspent balance credited on the next settlement
invoice."* Extended `market_ext_lapsed_lot_settlement_credit.rule` now states: *"A lot stays
drawable for the months printed against the market format, counted from the day the funding cleared,
so the lapsed funding is what was paid in before that many months back from the day the credit is
worked out."* Same anchor (the day the funding cleared), same duration (the printed
`subsidy_funding_lot_expiry_months`), same consequence (the unspent balance is credited on a
settlement). The compute follows it — `funding_live = funding_6m if lot_expiry <= 6 else (funding_9m
if lot_expiry <= 9 else funding_12m)`, a bucketing that is **exact** for the six printed values
(6, 9, 12, 12, 12, 12) — and the round-1 six-month ladder tier is gone entirely. Base and extended
now reach the same conclusion in the same situation, so no `overwrite` is owed, and the lineage
addition to `base_policy_refs` is honest rather than decorative: the extended rule quotes that base
policy's sentence and its `baseline.params` names `subsidy_funding_lot_expiry_months`.

### factor_ladders (round 2)

| policy | factors | `parameter` | `method` | `cross_difficulty` | change from round 1 |
| --- | --- | --- | --- | --- | --- |
| `market_ext_kiosk_catch_up_drawdown` | 4 | 2 | 2 | `pooled_dining_share` → cafe | `thin_funding_step_pct` 5.0 → **4.0** |
| `market_ext_period_settlement_true_up` | 5 | 3 | 2 | — | none |
| `market_ext_outage_service_credit` | 5 | 3 | 2 | — | none |
| `market_ext_settlement_payment_amount` | 5 | 3 | 2 | `group_settlement_offset` → cafe | none |
| `market_ext_standby_period_settlement` | 4 | 3 | 1 | `management_fee_share` → cafe | none |
| `market_ext_lapsed_lot_settlement_credit` | 5 | 3 | 2 | — | `lapsed_funding_window` **removed**, `settlement_reading_window` **added** |
| `market_ext_subsidy_funding_lot` | 5 | 3 | 2 | — | `long_drawable_life_months` 18 → **12**; `kiosk_handling_step` re-forked from `mobile_pay_enabled` to `sku_count`/`wide_range_sku_floor` 250 |

Mechanically re-verified across all 33 ladders: every ladder has exactly three tiers ending in
`otherwise`; no two tiers of any ladder select the same value or method; every `decides` is an input
binding, never `result`; no two factors of one policy share a binding; every tier is stated in the
rule and implemented in `compute`; every `method` factor's tiers change the algorithm and every
`parameter` factor's tiers substitute a number.

**Reachability, format by format, for every ladder the rework touched** (the round-1 defect was a
tier no format could reach, and a replacement ladder can reintroduce it):

- `cover_period_basis` — tier 1 `lot_expiry >= 12`: Standard, Fresh, Expanded, Smart (all 12);
  tier 2 `< 12`: Compact (9), and Cooler (6) which base excludes from funding, so Compact carries it;
  tier 3: any agreement with fewer than 2 funding lots. **All three live.**
- `kiosk_handling_step` — tier 1 `sku_count >= 250`: 280 / 420 / 650 / 380; tier 2 `< 250`:
  Compact 140 (Cooler 60); tier 3: fewer than 6 drawdowns in the year. **All three live**, and the
  fall-through, which is the factor's declared `baseline` (`0.0`), is reachable.
- `settlement_reading_window` (new) — tier 1 `invoice_cycle_day >= 10`: Standard 10, Fresh 12,
  Expanded 15, Smart 18; tier 2 `< 10`: Cooler 5, Compact 8; tier 3: fewer than 2 settlement charges
  in two months. **All three live.**
- `drawdown_attribution_basis` — unchanged fork on history; both non-fall-through tiers reachable.

No factor's declared `baseline` now sits on an unreachable tier anywhere in the charter; the
`long_drawable_life_months = 18` and `mobile_pay_enabled` conditions that produced round-1 **C-13**
are both gone. **C-13 closed.**

Every face of every touched factor was checked, not only the face the rework's item named — `rule`,
`baseline.rule`, `compute`, `compute_basis`, each `ladder[].when`, each `ladder[].value`/`method`,
`bindings`, `baseline`, and the policy's `cross_category` block. No face was left selecting a
different tier from another: the mechanical sweep above finds zero rule/compute tier mismatches, and
the two-way `compute_basis` and `baseline.rule` sweeps are clean.

### findings (round 2)

Round-1 charter-global items, item by item.

| id | round-1 verdict | round-2 disposition |
| --- | --- | --- |
| **C-1** the "outage credit" state is not record-visible | SOURCE-POLICY RED | **closed** — `market_ledger.kiosk_reference` now carries the distinction; both rules and both `baseline.rule`s state it; both tools set it deterministically; both rewritten `condition`s name it; `find_market_ledger` returns it and names "kiosk" in its docstring. Demonstrated per task in `0.md` § `revision_2` → `findings` F-0-1. |
| **C-2** undeclared override of the base lot-expiry rule | SOURCE-POLICY RED | **closed by agreement rather than by declaration, and the route is legitimate** — verified sentence against sentence in § `override_declarations` above; base and extended now yield the same lapsed lots on task 1's world (13 000.00, the lots of 2025-03-12 and 2025-06-18). The `base_policy_refs` addition is honest lineage, not decoration. |
| **C-13** three ladders with a tier no customer can reach | SOURCE-FACTOR RED | **closed** — `long_drawable_life_months` 18 → 12, `kiosk_handling_step` re-forked onto `sku_count`, `lapsed_funding_window` removed outright and replaced by `settlement_reading_window`. Reachability re-checked format by format in § `factor_ladders` above; no factor's declared baseline sits on a dead tier anywhere in the charter. |
| **C-3** docstrings assert balance effects the code never performs | observation | **closed** — all seven tools call `ctx.update`; verified moving on both worlds. |
| **C-4** `invoice_posted_date` anchors on an unwarranted charge code | observation | **closed, narrowed** — the rule now names the equipment line. Residual scope gap (`LATEST` across the ledger vs "the equipment line **the settlement invoice carries**") coincides on task 0's world. |
| **C-5** "half up" vs banker's rounding | observation | **closed** — every rule, `baseline.rule` and amount Arg now states nearest-even; the round-1 live instance (1413.43 vs 1413.42) is gone. |
| **C-6** ordering word in the docstrings | observation | **NOT CLOSED** — six of seven reworded, `post_kiosk_catch_up_drawdown_96ce656f` line 31 still reads "read it from the micro market agreement lookup **before** calling". |
| **C-7** one `condition` broader than its sentence | observation | **closed** — narrowed to "a **monthly settlement charge**". |
| **C-8** `credits_all` counts credits that are not funding handed back | observation | **closed** — `kiosk_reference=''` filter, matching the rule. |
| **C-9** undeclared override of the pooled daily ceiling | observation | **closed** — declared on `market_combination_dining_interaction`. |
| **C-10** base's `fixed_per_visit` branch dropped | observation | **NOT CLOSED** — see R-1. |
| **C-11** base's sales-shortfall charge has no route | observation | **closed** — declared overwrite, "No shortfall charge is invoiced on a subsidy true-up basis". |
| **C-12** the portfolio band is never applied | observation | **closed** — declared on the standby policy; the true-up needs none, base itself exempting a subsidy true-up. |

**R-1 — observation (C-10 re-raised) — base's `fixed_per_visit` drawdown branch is still dropped,
now silently rather than by an error.**
Base `market_subsidy_drawdown_rules.rule`: "…a `fixed_per_visit` model meets a flat amount once per
shopping visit…". `market_ext_kiosk_catch_up_drawdown.rule` now says "Where the market format's
subsidy model meets no share of shelf price, no shelf figure is recovered and **no discount is
booked at all**", and `compute.trip_shelf_value` guards the division
(`… if P('subsidy_pct_of_shelf_price') > 0 else 0.0`). For Expanded Campus Micro Market
(`subsidy_model: fixed_per_visit`, `subsidy_pct_of_shelf_price: 0.00`) base promises a flat amount
and extended books nothing; the `overwrite` block names only the `percent_discount` clause. What the
rework did fix is real — round 1's defect was a `ZeroDivisionError`, i.e. *no* number; there is now
a definite number and a rule sentence behind it. What survives is an undeclared divergence from a
base clause that is still in force and will be rendered into the same KB. It cannot be implemented
inside the write domain, because base names no flat per-visit amount and `parameter_schema` carries
none — which makes declaring the overwrite the available route, not implementing the branch.
Bears on neither task: both instantiate percent-discount formats.

**R-2 — observation (F-0-6 / F-1-5 re-raised) — the seeded drawdown ledgers do not match the event
the charter declares, and the decline's stated ground does not hold.**
The residual was declined on the ground that the blocking definition lives in frozen base — the
`market_subsidy_drawdown_posted` grain line "one row per kiosk purchase that draws subsidy". That
line is indeed frozen. The **seed** is not: `initial_state` is inside this difficulty's write
domain, and a ledger of per-purchase rows would satisfy the grain, the base per-employee-per-day cap
(`subsidy_cap_per_employee_per_day_usd`, 5.50 for Standard and 9.00 for Smart Store — every one of
task 1's 26 rows is 700.00–830.00) and the trading volume the format's entry gate implies. So the
constraint could have been routed around and the decline is not on the merits.
The reason it matters beyond realism: four ladders in this charter fork on **counts** of those rows
— `busy_kiosk_postings` 8, `busy_year_postings` 6, `busy_kiosk_trips` 8, `busy_quarter_trips` 10 —
and on task 0 also on a count of 11 quarter trips against `thin_quarter_trips` 12. On a per-purchase
ledger for a 200- or 480-head site those thresholds would be cleared by an order of magnitude and
every one of those ladders would collapse onto a single tier. The ladders are calibrated to the
aggregate-shaped seed rather than to the business the charter describes.
Still an observation and not a red light: no second scored number follows from it on either world,
and every factor demonstrably bears weight as the worlds actually stand.

**R-3 — SOURCE-CHAIN RED (new, task 0 only) — one proof face was not regenerated with the rework.**
Recorded in full, with its verbatim evidence and its demonstration, in `0.md` § `revision_2` →
`findings` **F-0-9**: `tasks/0.json` → `prerequisite_closure.edges[0].unresolved_at_frozen_time`
still describes the POS-linked intake row as "One **approved** kiosk outage request" although the
F-0-2 fix put it into `received`, and still states the window figure as "rises from 19.40 to
**20.71**" although the round-2 recomputation gives **20.77**. Both are round-1 values surviving
into round-2 artifacts. Every other proof face of both tasks — all 33 `factor_trace` entries, the
other five `why_false`/`flips_to_true_by` blocks, `design_rationale`,
`argument_uniqueness_tracing` and `solvability_contract` — recomputes correctly, so this is one
stale block rather than a systematic gap; but it is the same class of defect as round-1 **F-1-8**,
which the rework closed.

**R-4 — observation (new) — a claim made about the rework does not hold.**
The rework is presented as having moved gold on every computation of both tasks. Independently
re-derived, task 1's `market_ext_standby_period_settlement` is unchanged from round 1: **2633.70**,
`baseline_result` **1920.00**, sensitivities **1358.10 / 2746.50 / 3809.70 / 2551.20**. The closure
shortened from 57 to 39 days but `ceil(39/30) = ceil(57/30) = 2`, and no other input of that
computation moved. The figure is correct for the world it is computed on; only the claim is wrong.

## closing_checklist (round 2)

| Step 4 item | status |
| --- | --- |
| per-task audit files correspond one-to-one, `_difficulty.md` alongside, old revisions traceable | **met** — revision 1 preserved verbatim in all three files; revision 2 appended below it |
| every comparison section carries a PASS | **not met** — `1.md` § `revision_2` PASSes on all four relationships; `0.md` § `revision_2` carries one open SOURCE-CHAIN RED (F-0-9 / R-3) |
| extended policies fully covered, task scopes pairwise disjoint over the whole tree | **met** — 4 + 3 = 7, disjoint, complete |
| task tools and GT closed; each tool an independently generated, frozen uuid8 | **met** — seven tools, seven uuid8s, all used |
| every tree: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥ 1 `owner=user` problem, no cycle; the difficulty's edges together a DAG | **met** — task 0 n = 3 with 4 `value_input` edges, task 1 n = 2 with 2; both roots `owner=user`; two disjoint acyclic components |
| every computation: self-sufficient baseline, 4–6 factors (2 `parameter`, 1 `method`), ≥ 1 multi-source and ≥ 1 cross-difficulty per task, ladders of three tiers stated in full, tiers distinct in outcome, conditions and outcomes ones the business holds, every factor bearing weight against an honest baseline, baseline alone giving a definite number different from gold | **met** — 33 factors across the two tasks, all bearing weight; seven whole-baseline figures (3.05, 33.17, 70.49, 60.49, 1920.00, 0.00, 2969.22) all differing from gold; every tier of every ladder reachable by at least one market format |
| instantiation-stage gates re-run once on the final form | **supplied by the coordinator and green**, including the new `BASE FROZEN OK (10 files verified by hash)`; independently re-verified here that the base section of `market.extended.yaml` is byte-identical to `blueprint/products/market.yaml`. Not re-run by this auditor: `replay_tasks.py` rewrites task files, which is outside the audit's write domain |

**Difficulty verdict (round 2): NOT CLOSED — one open red light, down from four.**

- Closed and verified: **C-1**, **C-2**, **C-13** (the three round-1 REDs at charter level),
  **F-0-1**, **F-0-2**, **F-1-1**, **F-1-3**, **F-1-8** (the per-task REDs), and the observations
  C-3, C-4, C-5, C-7, C-8, C-9, C-11, C-12, F-0-3, F-0-5, F-0-8, F-1-2, F-1-4, F-1-6, F-1-7.
- Open: **R-3 / F-0-9** (SOURCE-CHAIN, task 0) — a stale `prerequisite_closure` proof block.
- Not closed, observations: **C-6** (one docstring still carries "before"), **C-10 / R-1** (base's
  `fixed_per_visit` clause still undeclared), **R-2** (the drawdown-grain residual, decline not on
  the merits).
- Accepted decline: **F-0-7** — `related_reference` is the only free reference field on
  `market_service_intake` and `db_schema.json` is frozen base, so there is no route inside the write
  domain; the field's declared *format* line accommodates the usage.
- New claim inaccuracy, no artifact defect: **R-4**.

Nothing that revision 1 recorded as holding has regressed: the base copy is still byte-identical,
`rule`↔`compute` is lossless in both directions in both faces, every prerequisite sentence is
verbatim in its own blocked rule and nowhere else, all six edges are `value_input` and all six bear
weight, both roots are the customer's own write, no write waits on a real-world event, no tool
judges a prerequisite, and the independent re-derivation reproduced **all seven gold values, all
seven whole-baseline figures, all 33 factor sensitivities and all six edge-skip figures exactly**.

---

## revision_3

### charter_global_frozen (round 3)

- freeze time: 2026-09-22 (round-3 run). Revisions 1 and 2 above are untouched.
- Both shared sources moved again, so **this section is re-derived in full**:
  `market.extended.yaml` `c03c6343a3b0455eeab53d8c0932f134b8802beeccce863357ce00f031305a51`
  (round 2 `588cc920…`), `task_tools.py`
  `885a6f86021e53892349383a06a9c270dcc292f88515daa846cd3777b555a3ba` (round 2 `a085595d…`).
- **Neither world moved**: `0.masked.json` `edfec694…` and `1.masked.json` `3f1e702c…` are the
  round-2 files byte for byte. Every change this round is in the charter, the tool contracts and the
  tasks' proof faces.
- Independence disclosure: not blind — round-1 and round-2 GT were read in earlier revisions.
  Round-3 GT was opened only after both task files' `revision_3` derivations were on disk.
- Gates supplied by the coordinator, all green including `BASE FROZEN OK (10 files verified by
  hash)`; independently re-verified that lines 1–688 of `market.extended.yaml` are byte-identical to
  `blueprint/products/market.yaml`. The note that the rework was interrupted by a usage limit and
  resumed changes nothing for this audit: the artifacts are judged as they stand, and the
  interruption is exactly the circumstance under which a half-applied fix would show up, which is
  what the proof-face sweeps below test for.

### what changed in the charter

| policy | change |
| --- | --- |
| `market_ext_kiosk_catch_up_drawdown` | a **third** `overwrite` entry, on `market_subsidy_drawdown_rules`, superseding "a fixed_per_visit model meets a flat amount once per shopping visit" (C-10) |
| `market_ext_lapsed_lot_settlement_credit` | `busy_kiosk_postings: 8` → `material_drawn_usd: 5000`; `drawdown_attribution_basis` forks on an **amount** drawn rather than a count of rows; `bindings` follow (`drawdown_count_all` → `drawdowns_all`) |
| `market_ext_subsidy_funding_lot` | `busy_year_postings: 6` → `active_kiosk_year_usd: 3000`; `take_up_share` and `kiosk_handling_step` fork on `drawn_year`/`drawn_year_handling`, amounts drawn over twelve months |
| `task_tools.py` | the last ordering connective removed from `post_kiosk_catch_up_drawdown_96ce656f` (C-6) |

Everything else — the seven policies, their subjects, triggers, `computes` names, target tools,
uuid8 tails, the six prerequisite edges and the task scopes — is unchanged from round 2.

### policy_conflict_scan / action_binding_and_uuids (round 3)

Seven policies, seven distinct `computes` names, seven distinct target tools, seven uuid8 tails
(`96ce656f`, `13e3670a`, `49294a76`, `693f0fba`, `ab27821d`, `131d77d2`, `f6d53aaa` — pairwise
distinct, no shared prefix, no sequence). `(target_tool, computes)` claimed once each. Scopes 4 + 3
= 7, disjoint, complete. The two same-subject pairs remain separated by rule **and** by
`market_ledger.kiosk_reference`.

**C-6 closed.** Scanned `task_tools.py` for `before|after|first|prior to|then|once|until` — a
deliberately wider net than the connective list the prerequisite check uses — and it returns **zero
hits**. All seven `market_agreement_id` Arg entries now read "as returned by the micro market
agreement lookup". Every tool body is still `make_id` → `find` → `create` → `update` → return, with
no branch, no raise and no status test, so no tool judges a prerequisite.

### rule_compute_equivalence / prerequisite_graph / prerequisite_sentences (round 3)

Mechanically re-verified over all seven policies: every sentence of every `compute_basis` value and
of every `baseline.rule` occurs verbatim in that policy's own `rule` — **0 failures**; every
non-fall-through ladder tier is stated in the rule (5 tiers state the window anaphorically, "over
those three months", which the ladder writes out — the same tier, verified by reading each pair) and
is a branch of its `decides` binding, and every branch is a tier the rule states. All six
`policy_source` sentences are verbatim in the **blocked** policy's own rule and in **no**
depended-on rule (6/6, 0 leaks). The graph is the same DAG in two disjoint components, all six edges
`value_input` and `form: state`, no `fallback_reason` anywhere, every `gate` an existing input
binding, every `resolved_by` the depended-on policy's own `target_tool`.

### override_declarations (round 3)

All eleven `overwrite` entries across the charter were checked on four points at once — the named
base policy present in that policy's `base_policy_refs`, the `superseded_clause` verbatim locatable
in that base policy's `rule`, the `replaced_by` text present in the extended `rule`, and no
duplicate (policy, base policy, clause) pair. **11 of 11 pass.**

**C-10 closed.** `market_ext_kiosk_catch_up_drawdown` now carries three entries, the new one being
`market_subsidy_drawdown_rules` / "a fixed_per_visit model meets a flat amount once per shopping
visit" → "Where the market format's subsidy model meets no share of shelf price, no shelf figure is
recovered and no discount is booked at all." The base policy was already in `base_policy_refs`, the
superseded clause is verbatim in `blueprint/products/market.yaml`, the replacing sentence is in the
extended `rule` **and** in its `baseline.rule`, and the three entries name three different clauses,
so there is no duplicate pair. The round-1 and round-2 defect — base promising a flat per-visit
amount while extended booked nothing, undeclared — is now a declared override, which is the only
route available inside the write domain since base names no flat amount and `parameter_schema`
carries none.

### factor_ladders (round 3)

Structural sweep across all 33 ladders: every ladder has exactly three tiers ending in `otherwise`;
no two tiers of any ladder select the same value or method; no `decides` is `result`; no two factors
of one policy share a binding; per-policy counts are 4/5/5/5/4/5/5 factors with ≥ 2 `parameter` and
≥ 1 `method` throughout — **0 structural issues**.

**Reachability of the three re-forked ladders, since a re-fork can reintroduce round-2's dead
tier:**

- `drawdown_attribution_basis` (`material_drawn_usd` 5000) — tier 1 (≥ 5000 drawn with some outside
  the drawable window) is task 1's world; tier 2 (≥ 5000, none outside) is a market funded and
  trading only inside its lot-expiry window; tier 3 (< 5000 drawn in total) is the archetypal
  lapsed-lot case and is reachable on every fundable format, the printed minimum lots running from
  1800.00 (Compact) to 16 000.00 (Expanded Campus). The factor's declared baseline
  (`drawdowns_all`) sits on the reachable fall-through.
- `take_up_share` and `kiosk_handling_step` (`active_kiosk_year_usd` 3000) — tiers 1 and 2 are task
  1's world (7800.00 drawn), split by the suspension flag and by `sku_count` against 250
  (280/420/650/380 against 140/60); the fall-through, under 3000.00 drawn in a year, has a concrete
  witness in **task 0**, whose market drew 47.15 over its trailing year. Three live tiers each, both
  baselines on reachable fall-throughs.

All other ladders are unchanged from round 2, where their reachability was established format by
format.

### findings (round 3)

| id | round-2 verdict | round-3 disposition |
| --- | --- | --- |
| **R-3 / F-0-9** the stale `prerequisite_closure` proof block | SOURCE-CHAIN RED | **closed** — both round-2 stale values replaced with the correct ones ("standing received"; "19.40 to 20.77"), verified against my own recomputation. See `0.md` § `revision_3` → `findings`. |
| **C-6** ordering word in a docstring | observation, not closed | **closed** — zero hits under a wider regex than the gate's. |
| **C-10 / R-1** base's `fixed_per_visit` clause undeclared | observation, not closed | **closed by declaration**, verified on all four override points above. |
| **R-2** the drawdown grain and the ladders calibrated to it | observation, re-raised | **second half closed outright; first half accepted on its merits** — see R-5. |
| **R-4** the "gold moved everywhere" claim | observation | **corrected** — the `design_rationale` now records "it is 2633.70 in round 1, round 2 and round 3, with baseline_result 1920.00 and sensitivities 1358.10 / 2746.50 / 3809.70 / 2551.20 unchanged throughout … ceil(39/30) = ceil(57/30) = 2", which is exactly what my re-derivation finds. |

**R-5 — observation — R-2's remainder, judged on the arithmetic offered rather than on the frozen
base ground I rejected last round.**
The re-fork closed the half that was inside the write domain: no ladder in this charter now forks on
a count of the aggregate-shaped drawdown rows, and the count forks that remain are over funding
lots, service requests, settlement charges, payments, credits and disputes — each one row per
business object under its own event's grain. Task 0's ledger was rebuilt as genuinely per-purchase
(19 rows, all `POS-` till references, largest 5.40 against a 5.50 per-employee-per-day cap), so
**F-0-6's contradiction is fully closed**; task 1's rows are now declared kiosk **day** settlements
with `KDS-` day references, largest 830.00 against a site-day ceiling of 480 × 9.00 = 4320.00, so
**F-1-5's size contradiction is closed** too.
What is declined is that task 1's rows are day settlements rather than the single purchases the
frozen base grain line declares. I tested the argument rather than accepting it: with the standing
charge raised, `period_ceiling` is 1413.42 against a `gross_credit` of 1249.22, so the ceiling does
not bite — but substituting `drawn_against_lapsed` = 12 000.00 gives 1669.22 and caps at 1413.42,
and 2000.00 or 0.00 cap likewise. The lapsed lot must therefore be consumed to within roughly 580
of its 13 000.00 before four of that computation's five factors bear any weight. At the largest
per-employee-per-day subsidy any format prints (9.00) that is upwards of 1,380 seeded rows, and
moving to the smallest fundable format does not rescue it: `drawdown_attribution_basis` needs
`drawdowns_all` ≥ 5000 to leave its own fall-through, which at Compact's 3.00 cap is ≥ 1,667 rows.
The tension is between a frozen base grain line and the factors-bear-weight requirement, and it
cannot be routed around inside the write domain. **The decline is correct; the residual stands
recorded, not fixed.**

**R-6 — observation — what my own proof-face coverage was.**
The reworker's answer to this defect family is a claim about process (generation from a machine fact
pack, plus a verifier), and a face a verifier does not parse is a face it cannot fail. So rather
than test the verifier I ran my own sweep, independent of it, over **every prose field of both task
files**: `design_rationale`, `solvability_contract`, every `argument_uniqueness_tracing`, the whole
of `prerequisite_closure` and all seven `factor_trace` blocks. Every number in them was matched
against the values my own replay produces — every binding of every computation at its own
handling-time world, every per-factor substitution and every whole-baseline substitution — plus
every `initial_state` field and every charter parameter. The only unmatched figures are skip-world
figures, running balances, row counts, dates, credentials, and round-1/round-2 values the
`design_rationale` quotes explicitly as superseded history. **No stale claim about either world
survives.** On top of that I parsed each `decides` binding into its two guard conditions, evaluated
them on the handling-time world and compared the tier actually selected against `tier_taken`:
**33 of 33 agree**, and all 33 `tier_taken` strings are verbatim `when` clauses of the charter
ladders.

## closing_checklist (round 3)

| Step 4 item | status |
| --- | --- |
| per-task audit files one-to-one with the tasks, `_difficulty.md` alongside, old revisions traceable | **met** — revisions 1, 2 and 3 all present and untouched in all three files |
| every comparison section carries a PASS | **met** — `0.md` and `1.md` § `revision_3` both PASS on all four relationships |
| extended policies fully covered, task scopes pairwise disjoint over the whole tree | **met** — 4 + 3 = 7, disjoint, complete |
| task tools and GT closed; each tool an independently generated, frozen uuid8 | **met** |
| every tree: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥ 1 `owner=user` problem, no cycle; the difficulty's edges a DAG | **met** — task 0 n = 3 with 4 edges, task 1 n = 2 with 2 edges; both roots `owner=user`; two disjoint acyclic components; all six edges load-bearing |
| every computation: self-sufficient baseline, 4–6 factors (2 `parameter`, 1 `method`), ≥ 1 multi-source and ≥ 1 cross-difficulty per task, three-tier ladders stated in full, tiers distinct in outcome and reachable, every factor bearing weight against an honest baseline, whole baseline differing from gold | **met** — 33 factors, all bearing weight; whole baselines 3.05 / 33.17 / 70.49 / 60.49 / 1920.00 / 0.00 / 2969.22, all differing from gold; every tier reachable by at least one market format and one admissible world |
| instantiation-stage gates re-run once on the final form | **supplied by the coordinator and green**, including `BASE FROZEN OK` and the scenario-wide `MERGE IDS OK`; base freeze independently re-verified here. Not re-run by this auditor: `replay_tasks.py` rewrites task files, outside the audit's write domain |

**Difficulty verdict (round 3): PASS — the source-layer audit is closed.**

Policy self-consistency PASS, the problem tree holds PASS, factors bear weight PASS, unique solution
PASS, on both tasks. Every round-1 and round-2 red light is closed and verified by recomputation
rather than by reading the fix: **C-1**, **C-2**, **C-13**, **F-0-1**, **F-0-2**, **F-1-1**,
**F-1-3**, **F-1-8**, **F-0-9/R-3**. Every round-1/round-2 observation is closed except the two
recorded residuals — **R-5** (task 1's rows are kiosk day settlements, not single purchases; the
tension is with a frozen base grain line and cannot be routed around) and **F-0-6**'s volume half
(a sample of a market's trading rather than a month of it) — and **F-0-7** (`related_reference`
carrying a till reference, the only free reference field on a frozen-base table), all three accepted
on their merits. **F-0-10** stands as a recorded reading question that produces no second number.

Independent re-derivation reproduced, across the two tasks, **7 scored values, 7 whole-baseline
figures, 33 factor sensitivities, 6 edge-skip figures and 33 tier selections — 86 of 86 exact.**
Nothing recorded as holding in revision 1 or revision 2 has regressed.
