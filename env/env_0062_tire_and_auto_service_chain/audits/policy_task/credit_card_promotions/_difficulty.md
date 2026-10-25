# Policy-task audit — credit_card_promotions / charter-global

## charter_global_frozen

- Frozen: 2026-10-14T23:13Z, round 1. Auditor: independent policy-task auditor (not the instantiator).
- Hashes (sha256, re-checked against the gate snapshot before reading; all match):
  - `tasks/credit_card_promotions/card.extended.yaml` 0c5454bee40a016c6de9295181f054b03ee1d85fdc18bf95c22eeb3146becbd6
  - `tasks/credit_card_promotions/task_tools.py` cbde45477f18caa28b1bf37db9a82f938780f844f21bac89b692112c44ccaa19
  - `.audit_views/policy/credit_card_promotions/0.json` 1f50f55d…3fff66, `1.json` fa80b701…16d93
- Read: `blueprint/{blueprint.yaml, db_schema.json, share_tools.py, products/card.yaml}`, the hazard / alignment / tires product charters (only to check seeded cross-category rows), the extended charter, `task_tools.py`, the two masked views, and the DSL evaluator `skills/erl-task-instantiate/scripts/check_compute.py` (functions only, used to replay the charter's own `compute` on the views).
- Not read: `tasks/credit_card_promotions/tasks/*.json`, both worklogs, `plan.md`, any other scenario or sibling difficulty, any `/tmp/*_0062` instantiator scratch. No recursive search over `env/`. This section is built from the charter, schema and tool contracts only; nothing in it is derived from any revealed GT.
- Base-copy check: the first 1221 lines of the extended charter parse identical to `blueprint/products/card.yaml` for every top-level key (`category … policies`); only `extended_policies` is added. Verbatim: PASS.

### policy_conflict_scan

Five extended policies:

| id | target_tool (owner) | trigger | prerequisite |
| --- | --- | --- | --- |
| card_ext_courtesy_fee_credit | apply_courtesy_fee_credit_68b22b43 (agent) | state_due | [] |
| card_ext_statement_minimum_payment | pay_statement_minimum_b2a1a039 (user) | on_request | ← courtesy (value_input, fee_part) |
| card_ext_late_fee_schedule | post_late_fee_f19feed4 (agent) | state_due | [] |
| card_ext_deferred_interest_assessment | assess_deferred_interest_7b31b265 (agent) | state_due | [] |
| card_ext_payment_direction | direct_payment_to_plan_c5f7b721 (user) | on_request | ← late fee (value_input, cover_amt); ← DI (value_input, interest_amt) |

- Overlapping subjects: courtesy and base `card_evt_fee_reversal` both govern `card_fee_reversal` (scoped by overwrite to courtesy credits only); late fee schedule vs base `card_evt_late_fee` (scoped by overwrite); DI vs base `card_evt_deferred_interest`; direction vs base `card_evt_payment_allocation`; statement minimum vs base `card_evt_statement`. No two extended policies claim the same `(target_tool, computes)`.
- Cross-policy interaction: the extended late-fee schedule has no effective date, so every historical `card_late_fee` row in a seed (posted at base amounts 30/41) is a fee a reader can re-figure under the schedule and find different (e.g. view 0's 2026-09-19 fee of 41.00 re-figures to 28.00 on its own posting day). It moves no scored value as long as the agent does not treat history as `fee_not_permitted` (observation O-1).
- Scopes: the coordinator states two tasks; the charter's five policies split naturally into {courtesy, statement minimum} and {late fee, DI, direction}; whether the tasks claim exactly these is checked per task after the reveal. The difficulty claim also lists `card_purchase`, `card_returned_payment_fee`, `card_merchandise_credit`, `card_closure`, which no extended policy targets (base-only; observation).

### rule_compute_equivalence

Checked binding by binding against `compute_basis` and back. Each binding quotes a rule sentence verbatim, and the expressions implement them, with these exceptions:

- **E-1 (rounding, every policy):** every `result` is `RND(x, 2)` = Python `round(float(x), 2)`, while every rule says "rounded half up to the cent". Python float rounding is not half-up: on an exact .xx5 figure whose float form sits below the half, RND rounds down. Members of the class: courtesy `result`, statement-minimum `result`, late-fee `result`, DI `result`, direction `result`. (`pct_up`/`ep_fixed` round up through `round_tolerance` correctly.) Finding F-2.
- **E-2 (late fee, no-fee test):** rule: "No late fee is owed … when the payments made toward the statement **before the fee posts**, less any of them returned unpaid, equal or exceed it." compute: `result: … paid_before >= st_min`, where `paid_before` subtracts payments with `txn_date=NOW`, i.e. "before **today**" (the wording the same rule uses for the partial-payment relief). The fee posts today ("the fee posts on the day after that due date"), so a payment made earlier on the posting day is "before the fee posts" in the prose and excluded by compute. Finding F-1.
- E-3 (courtesy; observation): "another late fee besides the one being credited … fewer than 12 / 3 months" is implemented as `lf_12m >= 2` / `lf_3m < 2`, which counts the credited fee itself. Equivalent only while the credited (most recent) fee falls inside the window.
- E-4 (DI; observation): `ended` takes the first expired plan in the order deferred_6 → 12 → 18 without excluding one already assessed. The rule's "the plan assessed is the one whose period has ended" assumes one.
- E-5 (direction; observation): `e_left` (deciding the "ended with a balance left" tier) leaves out merchandise credits and the ticket refund credit. The direction rule never defines that balance.
- E-6 (statement minimum; observation): `fee_in_cycle` reads only the LATEST late fee, so a second fee in one cycle cannot be represented.
- Every factor tier appears both in the rule prose and as a branch of its `decides` binding. No tier exists only in compute.

### action_binding_and_uuids

- Each `(target_tool, computes)` is claimed once. Tools: apply_courtesy_fee_credit_68b22b43, pay_statement_minimum_b2a1a039, post_late_fee_f19feed4, assess_deferred_interest_7b31b265, direct_payment_to_plan_c5f7b721. The five uuid8s share no prefix, sequence or adjacency pattern, and no reuse was found.
- Function bodies (task_tools.py lines 34-205) only `ctx.find` the account and `ctx.create` one row. None checks status, prerequisite or amount, and none computes a figure, so the tool layer judges no prerequisite.
- Docstrings: no ordering words (before/after/first), no other tool named, no concrete monetary example (regex for `\d+\.\d\d` finds none). No factor id is a substring of any tool name (checked mechanically, 24 ids × 5 tools).
- Observation O-2: docstrings and the base lifecycle treat late fees and deferred-interest assessment as ledger postings, and the base events describe them as system postings (late fee "posts … the day after the due date"; DI "at the next statement closing"). The blueprint summary lists the agent's writes as "corrections, allocations, credits and fee reversals", not penalty or interest assessment. A care-desk agent hand-posting a late fee and a deferred-interest charge during a cardholder's call is not how a US card program runs; these are overnight cycle postings. No wait is created, since the write is synchronous, so this is realism only.

### prerequisite_graph

- `prerequisite` is filled in on all five (`[]` on three). Edges: minimum → courtesy, direction → late fee, direction → DI. Every `problem` is an extended id in this file, none is base, none points at itself, and the graph is acyclic (depth 1).
- Each `policy_source` is found verbatim in its own rule:
  - minimum: "The minimum payment the desk takes on a statement is not fixed until every late fee posted in that statement's cycle that meets the courtesy credit conditions carries its courtesy credit."
  - direction: "A payment direction is fixed only after the late fee owed for a minimum missed on the latest statement stands on the account."
  - direction: "A payment direction is not fixed until the deferred interest owed on a plan whose promotional period ended since the latest statement closed stands assessed on the account."
- All edges are `form: state` with no `fallback_reason`. `kind: value_input` and `gate` (fee_part / cover_amt / interest_amt) are real bindings of the blocked compute. `resolved_by` is the depended-on `target_tool`, and its row is exactly what the gate binding reads: `fee_reversed`/`fee_part`/`nb_adj`, `fee_on_stmt`, `e_di`. `condition` matches each sentence's strength. No authoring-viewpoint wording appears.

### prerequisite_sentences

- Four-point test, all three edges:
  - ordering connective: "not fixed until", "fixed only after", "not fixed until";
  - state form, record-visible: "carries its courtesy credit" (a `card_fee_reversal` row, reason courtesy_waiver, citing the fee); "the late fee … stands on the account" (a `card_late_fee` row for that statement); "the deferred interest … stands assessed" (a `card_deferred_interest_assessed` row citing the plan);
  - no tool, id or snake_case token;
  - the strength matches the condition.
- One writer per waited-on state. Only apply_courtesy_fee_credit creates `card_fee_reversal`, only post_late_fee creates `card_late_fee`, and only assess_deferred_interest creates `card_deferred_interest_assessed`.
- Derivations, each with a single reading:
  - "courtesy credit conditions" leads the reader to the one rule that defines courtesy credits (card_ext_courtesy_fee_credit), whose target writes that row.
  - "late fee owed for a minimum missed on the latest statement" leads to card_ext_late_fee_schedule ("figures the late fee owed when the minimum payment of the latest statement was not received…").
  - "deferred interest owed on a plan whose promotional period ended" leads to card_ext_deferred_interest_assessment.
- The depended-on rules do not restate the sentences. The blocked rules name no other policy id or tool. No base rule sentence grounds a declared edge, and no extended rule states a cross-problem order that grounds no edge. The direction rule's "before that day's allocation runs" refers to an un-modelled back-office allocation, not a problem of this charter (observation).

### override_declarations

Sentence by sentence against each `base_policy_refs` entry:

- **courtesy** vs card_evt_fee_reversal:
  - "three reasons / at most once" and "Each fee row may be reversed only once": followed.
  - courtesy_waiver clause: declared (overwrite 1; it also turns the discretionary "may" into a mandatory posting and the payment test into "before the next statement closed").
  - billing_error, fee_not_permitted: followed.
  - "full amount of the fee row": declared (overwrite 2).
  - "Interest is never reversed as a courtesy": followed.
  - vs card_billing_dispute and card_evt_late_fee: no overlap with the courtesy quantity.
- **statement minimum** vs card_evt_statement:
  - minimum-payment sentence: declared.
  - dispute exclusion: inherited and silent.
  - "Equal-payment balances carry interest at the plan's equal_pay_apr_pct": NOT overwritten and still in force. It bears on the factor `installment_rate` (F-6).
  - vs card_evt_payment_allocation: the minimum's allocation row (lowest APR first, to the EP plan) is not produced by the payment tool. This is a back-office allocation, unscored (observation O-3).
  - vs card_evt_late_fee: no conflict.
- **late fee** vs card_evt_late_fee:
  - S1 (charged when not received by the due date): followed.
  - S2 (one per statement): inherited.
  - **S3 "No late fee is charged when the minimum payment due was 0.00 or when the payments received by the due date equal or exceed it": NOT named in `overwrite`.** The extended rule restates it as "payments made toward the statement before the fee posts, less any of them returned unpaid", which changes both the window (due date → fee posting) and the selector (posting window → statement tag). Undeclared override (F-1).
  - S4 (fee level and cap): declared.
  - S5 (no double fee with a returned payment fee): inherited.
- **DI** vs card_evt_deferred_interest:
  - accrual, the period-ended gate and the calendar-month counting: followed.
  - "assessed in one row at the next statement closing": declared.
  - "paid in full → nothing": followed.
  - S7 "A merchandise credit on the ticket reduces the remaining balance but never reverses an accrual already recorded": not overwritten. The near-payoff window lets a credit or refund that lowers the balance left drop recorded accruals from the assessment. This is a tension rather than a literal reversal, since the accrual rows stay (observation O-4).
  - The base events field "txn_date: the statement closing date following expiration" is contradicted by the day-after posting. It is an events description, not a policy sentence (observation).
- **direction** vs card_evt_payment_allocation:
  - channels / no fee, and minimum allocation: followed.
  - "amount above the minimum under highest APR first, except …": the instruction clause is replaced (declared), and the new cover/interest/hold amounts all sit inside the replaced instruction clause.
  - promo-window clause: not triggered.
  - allocation row ≤ promo remaining: followed (cap `t_left`).

### factor_ladders

| policy | factor | label | tiers | multi-source | cross-difficulty | structural verdict |
| --- | --- | --- | --- | --- | --- | --- |
| courtesy | history_share | parameter | 3 | yes (late fees × open_date) | – | OK |
| courtesy | service_plan_bonus | parameter | 3 | yes (hazard × alignment) | hazard, alignment | OK; realism observation O-5 |
| courtesy | card_spend_bonus | parameter | 3 | yes (sum × promo count) | – | OK |
| courtesy | fee_weight_bonus | parameter | 3 | no | – | OK; realism observation O-5 |
| courtesy | repeat_fee_basis | method | 3 | yes (fee level × 3-month fees) | – | OK |
| statement min | minimum_basis | method | 3 | no | – | OK |
| statement min | fee_component | parameter | 3 | – | – | **RED F-4**: tiers 1 and 3 are one netting rule (fee less reversal; tier 3 is reversal = 0, tier 2 is no fee) |
| statement min | installment_component | parameter | 3 | – | – | OK (final-installment cap is real); tier 3 is the cap at 0 (observation) |
| statement min | installment_rate | parameter | 3 | – | – | **RED F-6**: the ladder is the base variant table `equal_pay_apr_pct.equal_pay_24` (Starter, Card, Preferred, Mastercard 9.99 / MC Preferred 8.99 / World 7.99), still in force; the baseline 9.99 is a rate the base gives no MC Preferred or World account |
| late fee | fee_level | parameter | 3 | yes (6-month fees × missed min) | – | OK (repeat / CARD-Act cap / first are real) |
| late fee | partial_payment_relief | parameter | 3 | no | – | **RED F-3** (realism) |
| late fee | tenure_relief | parameter | 3 | yes | – | **RED F-3** (realism) |
| late fee | service_plan_relief | parameter | 3 | yes | tires, alignment | **RED F-3** (realism) |
| late fee | card_spend_relief | parameter | 3 | yes | – | **RED F-3** (realism) |
| late fee | repeat_step_basis | method | 3 | yes | – | **RED F-3** (realism: charging half the disclosed repeat step depending on a 3-month window is no issuer's fee schedule) |
| DI | ticket_refund_credit | parameter | 3 | yes | hazard, alignment | **RED F-4**: the three tiers are hz_refund + aln_refund (both / that one / none) |
| DI | stub_accrual | method | 3 | yes | – | OK (interest through the expiration date is real) |
| DI | near_payoff_window | method | 3 | no | – | **RED F-3** (realism); label borderline (window length, F-5 member at observation strength) |
| DI | final_cycle_effort | parameter | 3 | no | – | **RED F-3** (realism) |
| DI | account_tenure_relief | parameter | 3 | yes | – | **RED F-3** (realism) |
| direction | missed_minimum_cover | method | 3 | yes | – | **RED F-5** (mislabel: its tiers substitute an amount into `available = pay − cover − interest`, the same shape as `ended_plan_interest`, which is labelled parameter). Also F-4: tier 2 ("unpaid part", due date not passed) equals tier 1's "unpaid + late fee for that statement", since no fee can exist before the due date |
| direction | ended_plan_interest | parameter | 3 | yes | – | OK; tier 2 exists only for the unresolved-prerequisite state |
| direction | returned_payment_hold | parameter | 3 | no | – | OK (post-return payment holds are real); observation O-5 |
| direction | hold_release | parameter | 3 | yes | – | OK |

All ladders are disjoint as stated, every tier is in the rule prose, and every fall-through equals its factor baseline. Counts as declared: courtesy 5 (4p/1m), statement minimum 4 (3p/1m), late fee 6 (5p/1m), DI 5 (3p/2m), direction 4 (3p/1m). **Counts after striking the RED factors:**

- courtesy 5 (OK);
- statement minimum 2 (minimum_basis, installment_component): below 4;
- late fee 1 (fee_level): below 4, no method;
- DI 1 (stub_accrual): below 4;
- direction 3 (ended_plan_interest, returned_payment_hold, hold_release): no method.

Cross-difficulty factors surviving: courtesy.service_plan_bonus only (hazard + alignment). The late fee's and DI's cross-difficulty factors are struck.

### findings

- **F-1 SOURCE-POLICY RED (undeclared override plus a second reading): card_ext_late_fee_schedule's no-fee test.**
  - Symptom: base card_evt_late_fee says "No late fee is charged when the minimum payment due was 0.00 or when the payments received by the due date equal or exceed it", and this sentence is absent from `overwrite`. The extended rule says "No late fee is owed when the minimum payment due was zero or when the payments made toward the statement before the fee posts, less any of them returned unpaid, equal or exceed it." Compute uses "before today" (`paid_before` subtracts `txn_date=NOW`).
  - Root cause: the sentence was rewritten without declaration, with a time anchor (fee posting) that is neither the base's (due date) nor compute's (start of today).
  - Consequence: on any world where a payment toward the statement arrives on the fee's posting day before the fee is written, the two readings split (owed / not owed).
  - Bears on task 1, demonstrated in `1.md`.
  - Class members across the charter: none other. Every other "payments made toward …" sentence uses "before today" or "since it closed".
- **F-2 SOURCE-POLICY RED (rule/compute non-equivalence, rounding).**
  - Symptom: every rule says "rounded half up to the cent", while every `result` uses RND = `round(float, 2)`.
  - Class members: all five `result` bindings.
  - Bears on task 1, where the direction lands on an exact half cent (`1.md`). Task 0's values are not on a half cent (no consequence there).
- **F-3 SOURCE-FACTOR RED (unreal ladder: relief tiers no US card issuer applies to a disclosed penalty fee or to deferred interest).**
  - A late fee is a disclosed penalty set by first/repeat level and capped at the minimum due (Reg Z §1026.52(b)). No issuer reduces it for a partial payment, for account tenure, for holding a Crestline tire set or alignment plan bought with the card, or for card spend, and none charges half the repeat step depending on a 3-month window.
  - Deferred interest on a promo plan is, by its disclosure ("interest will be charged from the purchase date if the balance is not paid in full"), all accrued interest. No issuer publishes a windowed assessment for nearly-paid plans, an "effort" discount, or a tenure discount on it.
  - Members:
    - late fee: partial_payment_relief, tenure_relief, service_plan_relief, card_spend_relief, repeat_step_basis;
    - DI: near_payoff_window, final_cycle_effort, account_tenure_relief.
  - Bears on task 1. Courtesy-credit and direction-hold ladders are goodwill or hold matters where the line of business does weigh tenure, history, relationship and returned payments; they are recorded as observation O-5, not RED.
- **F-4 SOURCE-FACTOR RED (one rule written as several tiers).**
  - Members: statement-minimum fee_component (fee less reversal, so tier 3 is reversal 0 and tier 2 is fee 0), DI ticket_refund_credit (the tiers are the sum of the two refunds), direction missed_minimum_cover tiers 1–2.
  - Bears on task 0 (fee_component) and task 1 (ticket_refund_credit, missed_minimum_cover).
- **F-5 SOURCE-FACTOR RED (mislabelled effect): direction missed_minimum_cover** is labelled `method` but substitutes an amount (see table). Direction is then left with 0 `method` factors. DI near_payoff_window is a weaker member (it selects a window length). Bears on task 1.
- **F-6 SOURCE-FACTOR RED (straw-man baseline / base table under another name): statement-minimum installment_rate.**
  - The base charter's in-force sentence "Equal-payment balances carry interest at the plan's equal_pay_apr_pct", together with the variant parameter (MC Preferred 8.99, World 7.99, others 9.99), already fixes each product's rate.
  - The factor's baseline 9.99 for an MC Preferred or World account is a rate the charter says that product does not get. A reader without the factor document reads 8.99 from the base and lands on gold.
  - Bears on task 0.
- **F-7 SOURCE-FACTOR RED (factor counts).** This follows from F-3 to F-6: statement minimum 2, late fee 1, DI 1, direction 0 methods. It bears on both tasks.
- Observations:
  - O-1: no effective date on the late-fee schedule versus seeded base-amount fees.
  - O-2: agent-posted penalty and interest assessment, a realism concern.
  - O-3: the minimum payment's allocation row is not written.
  - O-4: DI S7 tension.
  - O-5: courtesy service_plan_bonus and fee_weight_bonus, and the direction hold and release, are invented goodwill or hold schedules. They are plausible for a retail private-label program, so not RED.
  - E-3 to E-6.

## closing_checklist

Not written. The difficulty does not close: there are open REDs (see the task files and the findings above).

## revision_2

### charter_global_frozen (round 2)

- Frozen: 2026-10-15, before any round-2 GT was revealed. Auditor: the same independent auditor.
- Hashes, re-checked and matching snapshot_r2:
  - `card.extended.yaml`: 08a7fa73…4e49
  - `task_tools.py`: e87d57d4…1e46
  - views: `0.json` 303fc7e7…0f36, `1.json` cccd2df9…4b78
- Both the charter and the tools changed since round 1, so every charter-global section is re-derived in full below. The round-1 text above is left untouched.
- Read domain and mask are the same as in round 1. No task JSON, worklog or plan.md was read before the freeze.
- Base copy: every top-level key equals `blueprint/products/card.yaml`; only `extended_policies` is added. Verbatim: PASS.

### policy_conflict_scan (r2)

| id | tool (owner) | trigger | prerequisite |
| --- | --- | --- | --- |
| card_ext_courtesy_fee_credit | apply_courtesy_fee_credit_68b22b43 (agent) | state_due | [] |
| card_ext_statement_minimum_payment | pay_statement_minimum_b2a1a039 (user) | on_request | ← courtesy (value_input, `rev_off`) |
| card_ext_returned_fee_courtesy | credit_returned_payment_fee_d3814d72 (agent) | state_due | [] |
| card_ext_deferred_interest_assessment | assess_deferred_interest_7b31b265 (agent) | state_due | [] |
| card_ext_payment_direction | direct_payment_to_plan_c5f7b721 (user) | on_request | ← returned-fee courtesy (value_input, `hold`); ← DI (value_input, `charges`) |

- **Two policies overwrite the same base clause.** Both courtesy policies replace the base `courtesy_waiver` clause and the "full amount" sentence. Their `replaced_by` texts split the clause by fee type: "a returned payment fee is credited as a courtesy only under the returned-payment courtesy schedule" and "a late fee is credited as a courtesy only under the late-fee courtesy schedule". The merged meaning is unique.
- **Observation R2-O1: one allowance, two schedules, no order.** Both schedules count "courtesy credits … in the rolling 12 calendar months" against the same `courtesy_late_fee_waivers_per_12_months`. On an account with an eligible late fee and an eligible returned payment fee but an allowance of 1, nothing in the charter decides which one gets the credit. Neither task's world has both kinds of fee, so this is not demonstrated here.
- Scope partition from the rule surfaces: {courtesy, statement minimum} and {returned-fee courtesy, DI, direction}. This is checked per task after the reveal.

### rule_compute_equivalence (r2)

- Every `compute_basis` entry is a verbatim rule sentence (checked mechanically, all five policies).
- Every `result` now rounds half up: `int(x*100 + 0.5 + half_up_nudge)/100`. Every "rounded up to the cent / whole dollar" step uses `round_tolerance`. Round-1 E-1 is closed.
- Round-1 E-3, E-4, E-5 and E-6 are closed:
  - courtesy now says "two or more late fees in that time, the credited one included";
  - DI `ended` excludes plans already assessed;
  - the direction's ended-plan balance is the "recorded balance", including merchandise credits;
  - the statement minimum names "the most recent late fee … one late fee at most is charged for each statement".
- Prose and compute agree on every tier, branch and anchor for each policy, including:
  - the DI stub, refund, void and reallocation day counts;
  - the direction's window-routing and `net_hold = MN(1, holds) × (1 − MN(1, releases))`.
- **Observation R2-O2: weaker hold wording.** The direction prose "the holds … are lowered by the releases … the part directed is what reaches the named plan less that net held share" no longer says "of the hold", as round 1 did. A subtractive reading (holds − releases) is conceivable. It is not adopted as a second reading: the rule caps the releases at "never above one", which only matters for a proportional reduction, and a subtractive reading would give a negative share the rule never floors. So this is recorded as an observation, not RED.

### action_binding_and_uuids (r2)

- Each `(target_tool, computes)` pair is claimed exactly once. The new uuid8 `d3814d72` is independent of the other four.
- Every function body is find + create only. No tool judges eligibility, a prerequisite or an amount.
- Docstrings contain no ordering word (before / after / first / then), no other tool's name and no monetary example.
- No factor id is a substring of any tool name (checked mechanically).
- `apply_courtesy_fee_credit` and `credit_returned_payment_fee` write identical `card_fee_reversal` rows. Their docstrings ("against one late fee" / "against one returned payment fee") and the two courtesy rules' partition sentences keep the binding to one reading.

### prerequisite_graph (r2)

- Edges: minimum ← courtesy; direction ← returned-fee courtesy; direction ← DI.
- The graph is acyclic.
- Each `policy_source` is verbatim in its own rule.
- Each `gate` (`rev_off`, `hold`, `charges`) is a real binding of the blocked compute.
- Each `resolved_by` is the depended-on `target_tool`.
- All edges are state form with no `fallback_reason`.
- Conditions match the sentences' strength.

### prerequisite_sentences (r2)

- **Four-point test.** All three sentences pass:
  - "…not fixed until every late fee posted in that statement's cycle that meets the courtesy credit conditions carries its courtesy credit";
  - "…fixed only after the most recent returned payment fee, when it meets the returned-payment courtesy conditions, carries its courtesy credit";
  - "…not fixed until the deferred interest owed on a plan whose promotional period ended since the latest statement closed stands assessed".
- **One writer per state, by policy.** A courtesy credit on a late fee is posted by apply_courtesy_fee_credit; on a returned payment fee, by credit_returned_payment_fee; a DI assessment, by assess_deferred_interest.
- **R2-F1, SOURCE-POLICY RED: the DI rule restates the dependency on the depended-on side.**
  - card_ext_deferred_interest_assessment's own rule says: "when the cardholder directs a payment on that closing day before the closing runs, the desk posts the assessment then so that the direction can be fixed against it."
  - Check 6 requires that the depended-on rule not restate the edge, and that no rule carry a second wording of a dependency or name another problem's action.
  - This sentence names the depended-on problem's dependent (the payment direction) and states the order ("so that the direction can be fixed against it"). It is a second, action-form wording of direction ← DI, written in the DI rule.
  - Consequence: the DI hub that renders this rule hands the reader the hop and the order that the direction's own state-form sentence is meant to make them derive. The edge's discoverability is no longer tested.
  - Class members across the charter: this sentence only. The two courtesy rules' partition sentences name the other courtesy schedule but state no order and no dependency.

### override_declarations (r2)

- **Courtesy (late fee)** vs `card_evt_fee_reversal`: both replaced sentences are declared, and the other sentences are followed, as in round 1.
- **Returned-fee courtesy** vs `card_evt_fee_reversal`:
  - Its two declared overwrites cover the same clauses, and the returned-payment courtesy is introduced by the first. "Each fee row may be reversed only once" is followed ("the fee carries no reversal").
  - vs `card_evt_returned_payment`: fee level and cap are inherited, not touched.
  - vs `card_billing_dispute`: no overlap.
- **Statement minimum** vs `card_evt_statement`:
  - The superseded clause now includes the dispute exclusion; this is declared.
  - The EP rate is now "the product's 24-month equal_pay_apr_pct", which follows the base parameter. Round-1 F-6 is closed.
  - The minimum's lowest-APR allocation row is still not produced by the payment tool. Round-1 O-3 remains an observation (unscored).
- **DI** vs `card_evt_deferred_interest`: the assessment sentence is declared, and "never reversed for a credit" is now honoured explicitly. Round-1 O-4 is closed.
  - Observation R2-O3: the `replaced_by` keeps "at the next statement closing", while the rule's first sentence lets the desk post "then" (before the closing runs, on the closing day). The posting date is the same; only the time of day differs. Not scored.
- **Direction** vs `card_evt_payment_allocation`:
  - The instruction clause is replaced (declared).
  - The window-cycle allocation is followed: "read here as a period ending no more than window_days days after today" restates `promo_allocation_window_cycles = 2` as 61 days. That is a narrowing of 2 billing cycles into days, inside the declared replacement.
  - The allocation cap (≤ recorded balance) is followed.

### factor_ladders (r2)

Counts:

| policy | factors | parameter | method | multi-source | cross-difficulty factors |
| --- | --- | --- | --- | --- | --- |
| courtesy | 5 | 4 | 1 | yes | service_plan_bonus (hazard, alignment) |
| statement minimum | 4 | 2 | 2 | yes | none (task-level cross via courtesy) |
| returned-fee courtesy | 6 | 5 | 1 | yes | protection_plan_bonus (hazard, battery) |
| DI | 4 | 3 | 1 | yes | ticket_refund_link (hazard) |
| direction | 5 | 4 | 1 | yes | relationship_release (tires, alignment) |

Structural checks:

- Every ladder has 3 disjoint tiers, all stated in the prose, with the fall-through equal to the baseline.
- Each ladder has at least two distinct non-zero tiers. The round-1 F-4 members are gone: fee_component, ticket_refund_credit and missed_minimum_cover are removed.
- **DI `stub_period`:** tier 2 ("ended on that closing date → nothing") is tier 1 at zero stub days. It is the zero/absent case, accepted on the same standard as every "otherwise 0" tier, and tiers 1 and 3 are distinct anchors. This matches round 1's PASS of stub_accrual.

Realism review against US card-issuer practice:

- **R2-F2, SOURCE-FACTOR RED (unreal condition): statement minimum `dispute_exclusion` tier 1.**
  - Tier 1 requires "a dispute submitted to the bank is open on a purchase **posted in the statement's cycle**". Every other open dispute falls to "otherwise nothing is taken off".
  - Reg Z §1026.13(d)(1) lets the cardholder withhold the part of any required payment related to the disputed amount while the dispute is open. The base sentence ("while a billing-error dispute is open the disputed amount is left out") says the same.
  - No issuer weighs the cycle in which the disputed charge posted. The case the condition drops is the usual one: a charge disputed after the statement that first showed it is, at the next statement, a prior-cycle charge with the dispute still open.
  - Under the rule as written, that cardholder's minimum keeps the disputed share, which an issuer would not publish.
- **R2-F3, SOURCE-FACTOR RED (unreal condition): direction `returned_hold`'s counting rule.**
  - The rule counts "the most recent returned payment only while its returned payment fee carries no courtesy credit".
  - A payment hold after returned payments is a risk control. Waiving the fee as a courtesy, which is allowance-based, does not change the payment's return history. No issuer stops counting a bounced payment for hold purposes because its fee was courtesy-credited.
  - This condition is the only path through which the returned-fee courtesy edge moves the direction (`hold` is its gate). Strike it, and the courtesy write changes nothing in the direction: the edge bears weight only through this unreal condition.
- **R2-F4, SOURCE-FACTOR RED (unreal treatment): DI `window_reallocation`'s interest effect.**
  - The rule says "Interest on the reallocated amount at the daily rate for each stub day is taken off".
  - The stub days run from the day after the last accrual closing. The reallocated excess is a payment that may have arrived inside the stub. Crediting interest for days before the money was paid is no issuer's correction of a misallocated payment; interest is corrected from the date the payment should have been allocated.
  - Class members: only this one. `ticket_refund_link` tier 1 (refund before the last closing → stub days only) follows the base's "accruals never reversed". `voided_allocation` tiers (from allocation date / stub days) are correct for a voided allocation.
- Accepted-type relationship and goodwill schedules, observation only (same standing as round-1 O-5, which the coordinator accepted):
  - returned-fee courtesy `protection_plan_bonus` (hazard + battery) and `payment_weight_bonus`;
  - direction `channel_hold` and `relationship_release`.
- Realistic and accepted:
  - window_route (Reg Z §1026.53(b)(1)(ii) last-two-cycles rule);
  - voided_allocation;
  - ticket_refund_link;
  - stub_period;
  - reversal_refigure;
  - installment_component;
  - minimum_basis;
  - courtesy_record_bonus;
  - return_history_share;
  - returned_fee_basis.
- **Observation R2-O4: inconsistent labels.** `dispute_exclusion` (labelled parameter) and `reversal_refigure` (labelled method) have the same shape: tier 1 is a percentage-of-amount computation, tier 2 a whole or capped amount, tier 3 zero. One of the two labels is inconsistent with the other. The statement minimum's honest `method` count does not depend on it (`minimum_basis`), so no count consequence is demonstrated.
- **Observation R2-O5: first-match reads.** The charter limits several reads to the latest record:
  - "only the most recent fee reversal is looked at" (statement minimum);
  - "only the most recent returned payment is looked at" (DI `voided_allocation`);
  - direction `returned_hold` reads the most recent returned payment fee only;
  - courtesy and returned-fee courtesy credit only "the most recent" fee.

  On these worlds each read meets a single matching row, so no consequence is demonstrated.

**Counts after striking (R2-F2, R2-F3):**

- statement minimum: 3 (minimum_basis, installment_component, reversal_refigure), below 4. This is R2-F5, SOURCE-FACTOR RED (count), and it bears on task 0.
- direction: 4 (window_route, channel_hold, tenure_release, relationship_release), still 4 with 1 method.
- R2-F4 leaves the factor `window_reallocation` itself standing (its tier choice is real); it is the treatment that is unreal.

### round-1 items: closure check

| item | status | basis |
| --- | --- | --- |
| F-1 / E-2 | closed | late-fee schedule and its tool removed |
| F-2 / E-1 | closed | all results round half up |
| F-3 | closed | late-fee and DI relief factors removed |
| F-4 | closed | the three named factors removed; no new member |
| F-5 | closed | missed_minimum_cover removed; window_route is an honest routing method |
| F-6 | closed | installment_rate removed |
| F-7 | reopened for the statement minimum only, via R2-F2 (see R2-F5) | — |
| O-1 | moot | schedule removed |
| O-2 | addressed | DI posts on its closing day by rule |
| O-3 | open (observation) | — |
| O-4 | closed | — |
| E-3 to E-6 | closed | — |
| hazard seed contradiction | closed | the task-1 refund of 26.60 equals the hazard charter's pro-rata figure |

### findings (r2)

| id | class | bears on |
| --- | --- | --- |
| R2-F1 | SOURCE-POLICY RED: dependency restated on the depended-on side | task 1 |
| R2-F2 | SOURCE-FACTOR RED: unreal condition, dispute_exclusion | task 0 |
| R2-F3 | SOURCE-FACTOR RED: unreal condition, returned_hold courtesy-uncount; carries the returned-fee courtesy edge | task 1 |
| R2-F4 | SOURCE-FACTOR RED: unreal treatment, window-reallocation interest over pre-payment days | task 1 |
| R2-F5 | SOURCE-FACTOR RED: count, statement minimum 3 | task 0 |

Observations: R2-O1 to R2-O5, and O-3.

### closing_checklist (r2)

Not written. The difficulty does not close. Open items: R2-F1, R2-F2, R2-F3, R2-F4, R2-F5.

Both tasks' gold values were reproduced blind, figure for figure, so these open items are structural and realism findings, not value disagreements.

## revision_3

### charter_global_frozen (r3)

- **Frozen:** 2026-10-15, before any round-3 reveal.
- **Hashes (all match snapshot_r3):**
  - charter 246df9b2…c3c8: changed, so re-derived in full;
  - task_tools e87d57d4…1e46: unchanged, so round-2 §action_binding_and_uuids is carried forward by reference;
  - views 5654e1a6…4239 and 6896b829…7170.
- **Base copy:** verbatim (every top-level key equals products/card.yaml).

### re-derived checks (r3)

- **Rule/compute equivalence:**
  - every `compute_basis` entry is a verbatim rule sentence;
  - every `replaced_by` appears in its rule;
  - every result rounds half up;
  - "both days counted" is implemented as `DAYS(...)+1` in the DI refund tier 2, void tier 1 and reallocation interest.
- **Prerequisite graph:** acyclic.
  - Edges: minimum ← courtesy (`rev_off`); direction ← returned-fee courtesy (`fees_owed`, new); direction ← DI (`charges`).
  - Each `policy_source` is verbatim in its own rule, each gate is a real binding, and each `resolved_by` equals the target tool.
  - All edges are state form.
- **Prerequisite sentences:**
  - New: "A payment direction is not fixed until the returned payment fee charged for a payment made toward the latest statement, when it meets the returned-payment courtesy conditions, carries its courtesy credit." It passes the four-point test, and by policy its single writer is credit_returned_payment_fee.
  - The DI rule no longer names the direction or states any order. R2-F1 is closed, and no other rule restates a dependency.
- **Factor id inside a tool name:** none.

### round-2 items: closure

| item | status | what changed |
| --- | --- | --- |
| R2-F1 | closed | DI rule now reads "the assessment may be posted at any time on that closing date" with no cross-problem wording. |
| R2-F2 | closed | dispute_exclusion tier 1 now covers "a charge carried in the statement's balance … whatever cycle it posted in", plus disputed fees other than the cycle's late fee. This is consistent with Reg Z §1026.13(d)(1). |
| R2-F3 | closed | returned_hold now counts every return in 6 months, with no courtesy-uncount. The returned-fee courtesy edge now works through fees still owed: "the returned payment fee charged for a payment made toward it … less any fee reversal standing against it" is covered before the direction. |
| R2-F4 | closed | Reallocation interest now runs "from the date of the latest allocation recorded toward that statement to such a later-ending plan through the last day of the period". A misdirected-allocation row is now seeded (task 1). |
| R2-F5 | closed | dispute_exclusion is no longer struck, so the statement minimum keeps 4 factors (3 parameter, 1 method). |
| R2-O1 | closed | Both courtesy rules: "late fees and returned payment fees draw on that one allowance in the order they posted". |
| R2-O3 | closed | — |
| R2-O4 | closed | reversal_refigure is relabelled parameter, consistent with dispute_exclusion. |
| R2-O5 | closed | Single-record reads are now scoped by each rule's applicability sentence ("at most one fee reversal … at most one … dispute"; "at most one payment made toward the latest statement was returned"; "no payment returned unpaid before the most recent returned payment carried an allocation to the plan"). Both worlds satisfy the scopes. |
| R2-O2 | open, observation | Unchanged hold/release wording; the proportional reading stands. |
| O-3 | open, observation | Unscored allocation row of the minimum payment. |

### realism of the changed material (r3)

- **New edge mechanism is real.** A fee waived as a courtesy no longer has to be covered from the payment. Covering outstanding fees and assessed interest before honouring a direction is an ordinary allocation choice within the issuer's discretion over the minimum.
- **Misdirected 300.00 allocation in the DI window is real.** Allocating excess to the expiring deferred-interest plan in its last two cycles (Reg Z §1026.53(b)(1)(ii)) and dating the interest correction from the allocation date are both actual practice.
- **New observation R3-O1.** The direction's sentence waits on "the returned payment fee charged for a payment made toward the latest statement". The returned-fee schedule credits only "the most recent returned payment fee". On a world where these two differ, the waited-on fee could never meet the schedule. Neither task's world has that shape, so there is no consequence here.

### findings (r3)

- No charter-global RED is open.
- Open observations: R2-O2, O-3, R3-O1.

### closing_checklist (r3)

- **Audit files:** `0.md`, `1.md` and `_difficulty.md` each carry revisions 1–3, with older text untouched. Every r3 comparison section reads PASS.
- **Coverage:** the 5 extended policies are fully covered by the two tasks, whose scopes are disjoint.
- **Task tools:** each has a frozen, independent uuid8.
- **Problem trees:**
  - task 0 has n=1 and task 1 has n=2;
  - every edge is `value_input`;
  - each tree has a user-owned root;
  - the difficulty-wide graph is acyclic.
- **Computations:**
  - every computation has a self-sufficient baseline that differs from gold;
  - each has 4–6 factors with at least 2 `parameter` and 1 `method`, and every factor bears weight on its task's world;
  - each task has a multi-source factor and a cross-difficulty factor whose seeded rows are consistent with their own charters;
  - no ladder fails the realism review.
- **Gates:** the coordinator's r3 snapshot lists every instantiation-stage gate as green apart from the two known pre-render items (traceability and validate on unrendered docs). I cite it; I did not re-run it.
- **Open observations (not grounds for rework):** R2-O2 (hold wording), O-3 (the minimum payment's unscored allocation row) and R3-O1 (latest-statement fee vs most-recent-fee scoping).

VERDICT revision_3: task0=PASS task1=PASS charter=CLEAN

## revision_4

### charter_global_frozen (r4)

- **Gate.** The worklog tail reads `REWORK round 4: gates 7/7 green`. Snapshot r4: every gate green, with TRACEABILITY OK (0 misses).
- **Hashes.**
  - charter b47db353…7e2c: changed, so re-derived;
  - task_tools 6601bbf7…af2a: changed;
  - views 5654e1a6… / 6896b829…: unchanged from r3.
- **Base copy.** Verbatim.
- **Sources read.** `audits/render_source/card/notes.md` (M1–M13) and the source-side section S1–S8 of `audits/policy_kb/credit_card_promotions/{0,1}.md`.
- **Frozen before any r4 GT reveal.**

### source-side items: closure check

| item | status | evidence |
| --- | --- | --- |
| M1 / S6 | closed | direction `baseline.rule` now reads "the amount available to direct, all of which reaches the named plan with no share of it held back, never more than the named plan's recorded balance". That equals the compute with every factor at its baseline (task 1: 725.72). |
| M2 | closed | the rule says "the plan whose period ends last …, the longer plan where two end on the same day"; `t_plan` now compares end dates (deferred_18 only if its end ≥ each running plan's end). |
| M3 / S7 / R2-O2 | closed | the hold rule now spells out that releases are fractions of the held share: "the held share is multiplied by one less their total, that total never above one". Proportional reading only. |
| M4 / S2 | closed | below-floor branch now reads "nothing taken off it but the payments made toward the statement since it closed", which matches `st_nb − paid_since`. |
| M5 | closed | "another fee posted on or before the statement's closing date"; `rev_off` tier 2 now checks `r_fdate ≤ st_date`. |
| M6 | closed | "never less than zero" is now stated for the past-due amount. |
| M7 | closed | "again never more than this plan's recorded balance", plus "those plans'"; `o18_rem` added. |
| M8 | closed | the assembly sentences are restated in baseline terms ("Every amount a rule of this schedule adds to or takes off …", "The assessment is the recorded accruals with every amount of interest a rule … adds or takes off"). The courtesy and returned-fee baselines now name the outright part, the whole-fee basis and the full share. |
| M9 | closed | factor bindings now own their quantities: `fee_stmt`; `ep_rate`/`ep_mrate`/`ep_fixed`; `realloc_int`; `refund_bal`/`void_bal`. |
| M10 / S5 | closed | the card_evt_statement `replaced_by` restates the printed-minimum rule in force; the card_evt_payment_allocation `replaced_by` keeps "the instruction is the cardholder's own request …". |
| M11 / S8 | closed | docstrings now say each call "writes only that entry … (the account record's stored balance field is not updated)". No ordering word, no other tool name, no monetary example. |
| M13 / S1 | closed | scope clauses moved into the sentences of the factor they bound ("This is figured for an account with at most one billing-error dispute open", etc.); the DI `replaced_by` no longer lists its corrections. |
| M12 | — | render-side; nothing to fix in source. |
| S3 / S4 | — | base, unchanged as instructed. |
| E1 | — | render-side. |

### re-checks (r4)

- **Rule ↔ compute.** Every `compute_basis` entry and every `baseline.rule` and `replaced_by` is verbatim in its rule.
- **Prerequisites.** The three edges, their sentences, gates and resolvers are unchanged from r3. The graph is acyclic and every edge is in state form.
- **Factor independence** (checked mechanically, all five policies). No binding is owned by two factors, and no factor's expression reads a binding that another factor owns; shared inputs are non-factor bindings only.
- **Docstrings.** No factor id is a substring of a tool name.

**Observation R4-O1 (rounding, class over all five `result` bindings).** `half_up_nudge` was removed, so every result is now `int(x*100 + 0.5)/100`. On an exact half-cent whose float lies just below .5 (for example 1.005 → 100.4999…), this rounds down where the rule says "half up". The defect is the same kind as round-1 F-2. No scored figure in either world lands on a half-cent (35.00, 116.02, 38.00, 92.7092, 334.8066), so there is no consequence here and it is not a RED.

R3-O1 and O-3 remain observations.

### closing_checklist (r4)

- Both tasks PASS on all four relationships.
- The render and KB-audit source items M1–M11 and M13 / S1, S2 and S5–S8 are closed in the source.
- The five policies are covered by disjoint scopes.
- Trees: task 0 has n=1, task 1 has n=2. All edges are value_input, the roots are user-owned, and the graph is acyclic.
- Every computation has 4–6 independent factors. Each has an honest baseline that differs from gold, and every factor bears weight.
- Cross-difficulty rows are seeded and consistent with their charters.
- Gates: the coordinator's r4 snapshot is all green, including traceability.
- Open observations: R4-O1 (rounding without tolerance, no consequence on these worlds), R3-O1 and O-3.

VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN
