# Policy-task audit — custom_commission_desk / charter-global

## charter_global_frozen

- freeze time: 2026-09-17 (session clock), written **before any task's GT fields were revealed**.
- auditor: independent audit agent, not the author of these artifacts.
- freeze hashes:
  - `env/env_0001_fine_jewelry_retailer/tasks/custom_commission_desk/custom.extended.yaml` sha256 `847b7f0210b73f0ff7388bca53f728c1cdf99bf2a2d5bf125917319232c2b916`
  - `env/env_0001_fine_jewelry_retailer/tasks/custom_commission_desk/task_tools.py` sha256 `d92b4094b80d25094dfbf89611fa3a1680e4311114a7503a011db33684d0605d`
  - masked task views: `0.json` sha256 `17928c82b495b9e9e2392be06c2075b360231915964162e24036ea339302cf4f`, `1.json` sha256 `d791f35bc83ab985d866e633001f88b37794742c08965d1c293644ce13468925`
- fields permitted while this file was written: the whole extended charter (base section + `extended_policies`), `task_tools.py`, `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/custom.yaml`, and each task's `frozen_time` / `user_scenario` / `initial_state` only.
- fields explicitly masked and never read while this file was written: `design_rationale`, `db_closure`, `db_closure_matches_initial_state`, `solvability_contract`, `evaluation_criteria`, `computations`, `prerequisite_closure`, `charter_scope`, `required_documents`. Nothing in this file is derived from a revealed GT field.
- entry conditions (Step 0): the coordinator supplied the instantiation gate snapshot (EXTENDED / TASK-TOOL-CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE, all green; `check_traceability` excluded for want of a published KB) and the mechanically masked views with their hashes. Entry conditions are complete; the gates were not re-run by the auditor at this stage and a green gate block is treated as the qualification to audit, not as proof.
- read-domain limitation recorded honestly: the brief fixed the readable blueprint surface as `blueprint.yaml`, `db_schema.json`, `share_tools.py` and `products/custom.yaml`. The charters of the three categories this difficulty reads across (`financing`, `tradein`, `protection`) were therefore **not** read, so the sub-check "the seeded cross-category rows do not contradict that product's own charter" could not be performed. Every other cross-difficulty test (rows present in `initial_state`, tier actually decided from them, factor bears weight) was performed and is reported.

### policy_conflict_scan

The structured policy in force for this difficulty is the base section of `custom.extended.yaml` (byte-identical to `blueprint/products/custom.yaml`: `category`, `display_name`, `binding`, `lifecycle`, `accounts`, `parameter_schema`, `variants`, `events`, `measures`, `policies` all compare IDENTICAL) plus the five `extended_policies`.

**Subjects / triggers / target tools.** The five extended policies partition their subjects and their tools without overlap:

| policy | subject | computes | target_tool | trigger |
| --- | --- | --- | --- | --- |
| custom_ext_change_consent | custom_order_specification_updated | agreed_change_value | confirm_specification_change_363ec738 | on_request |
| custom_ext_change_order_charge | custom_change_order_charged | change_charge_amount | charge_specification_change_ec6b5130 | on_request |
| custom_ext_metal_market_reprice | custom_price_adjustment_charged | metal_adjustment_amount | charge_metal_revaluation_a0bcb90e | state_due |
| custom_ext_closure_consent | custom_order_cancelled | retained_amount | confirm_commission_closure_3c2f355d | on_request |
| custom_ext_closure_refund | custom_refund_issued | refund_amount | issue_commission_refund_b90496cb | on_request |

No two policies claim the same subject, the same `computes` name or the same tool. Cross-category read boundaries are declared per policy (`financing` on change_consent, metal_market_reprice and closure_refund; `tradein` on change_order_charge and closure_consent; `protection` on closure_refund) and each declared category is actually read by a `CFIELD`/`EXISTS`/`XSUM` in that policy's `compute`; no policy reads a category it does not declare.

**Task scopes.** The two tasks' problem trees, as derived from the `prerequisite` graph alone, are
`{custom_ext_change_order_charge → custom_ext_change_consent}` and
`{custom_ext_closure_refund → custom_ext_closure_consent → custom_ext_metal_market_reprice}`.
The two sets are pairwise disjoint and together cover all five extended policies: **mutually exclusive and jointly complete**.

**Conflicts found.** Five, set out in `findings` below (F1–F5) and all bearing on task 1; two further items are recorded as observations (F6, F7). They are all of one family: the base section and the extended section reach different conclusions about the same scored quantity, and the extended side's `overwrite` does not name the base sentence it displaces. Because base and extended are rendered into the published KB together, each of these hands a reader a second, base-grounded value for a scored parameter.

### rule_compute_equivalence

Check 2 run mechanically and then by hand over all five policies.

- **Every `compute` binding has a `compute_basis` entry, and every `compute_basis` entry is a binding.** No orphans, no gaps (checked by script over all five policies).
- **Every `compute_basis` quotation is a verbatim sentence of that policy's own `rule`.** No exceptions across the five policies.
- **Every `baseline.rule` sentence is a verbatim sentence of the `rule`.** No exceptions across the five policies.
- **`baseline.params` name the keys the baseline reading actually uses** in each policy (`within_allowance_multiple`/`no_model_charge`/`house_stone_handling_pct`/`no_metal_move_factor`/`included_design_revisions`/`additional_revision_charge`; `published_fee_multiple`/`unstarted_reopen_pct`/`no_recast_pct`/`unstarted_day_rate`/`no_credit_settlement_pct`/`change_order_fee`; `standard_escalation_pct`/`house_stone_uplift_pct`/`full_pass_pct`/`no_start_delay_factor`/`metal_price_revaluation_window_days`; `no_design_fee_pct`/`no_metal_kept_pct`/`no_credit_restored_pct`/`no_relief_factor`/`cancellation_forfeit_pct_before_production`; `no_stone_holdback_pct`/`no_goodwill_pct`/`no_coverage_pct`/`no_overage_setoff_pct`). Each is the fall-through tier of the corresponding factor.
- **Every declared ladder tier is a branch of the `decides` binding and every branch of that binding is a declared tier.** Checked expression by expression; no tier lives only in `compute` and no rule tier is missing from `compute`.
- **Windows, anchors, counting conventions and rounding** each carry a quotation: the thirty-day period count and the "part period is not counted" rule (`periods_past`), the "never fewer than none" floors (`MX(0, …)` on `revisions_beyond`, `aged_days`, `bench_days_given_back`, `net_refund`, `result` of closure_refund), the "rounded half up to two decimal places … once" points (`result` of change_consent), and the per-component rounding of change_order_charge / metal_market_reprice / closure_consent / closure_refund.
- **Sweep back: compute invents no basis of its own** — with three exceptions, recorded as observations because no scored value in either task turns on them:
  - `credit_available` / `credit_minimum_spend` (change_order_charge) and `credit_remaining` / `credit_original_receipt` (closure_consent) filter the trade-in holding by `status='partially_redeemed'`. The rules say only "the customer holds an upgrade registration with credit still available"; a registration standing at `credit_issued` with credit left satisfies the rule's words and is silently invisible to the compute. Neither task seeds such a row.
  - `plan_open` (change_consent) implements the rule's "that plan still stands open" as `status == 'active'`. `past_due` and `in_hardship` plans stand open on the finance charter's own lifecycle but fall into the extended's second tier. Neither task seeds such a row. (The parallel bindings in closure_refund say "stands active" and match `status == 'active'` exactly; metal_market_reprice says "promotional term has not ended" and matches `promo_end_date > NOW` exactly.)
  - `days_since_approval` (closure_consent) is `DAYS(design_approved_date, NOW)`, i.e. the handling date, while the rule sentence says "the closure **reaches the studio**". In task 1 both dates fall on the same side of the window, so nothing turns on it.
- **Rounding mode.** The rules say "rounded half up"; the DSL's `RND` is Python `round`, which is half-to-even. No scored intermediate in either task lands on an exact half-cent, so the two agree here. Observation only.
- Four factors restate a ladder tier by expanding a pronoun or an abbreviation that the `rule` writes shorter (`bench_day_clock_anchor` tier 2 — rule: "they are counted from the date the casting stage was reached"; `revaluation_clock_anchor` tier 2 — rule: "it starts on the date the commission was opened at the consultation"; `overdue_closure_relief` tier 2 — rule: "it is taken at the studio's late relief fraction"; `money_put_in_source` tier 2 — rule: "it is read as the financed amount on that plan together with the amount paid at the till"; and `revision_overage_multiple` tier 2 — rule: "where every included revision has already been drawn and the piece has not gone into production"). Every tier is stated in the rule with its condition and its value or method; only the surface wording differs. Observation, no consequence.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (table above). No tool is the target of two policies and no `computes` name repeats.
- Each policy's subject, `base_policy_refs`, target tool, tool docstring and terminal state admit one business reading; no docstring adds a confirmation, a review, a wait or a procedure the policy does not carry.
- **No docstring states a position in a sequence, names another tool, or carries an ordering word.** `grep -i` over `task_tools.py` for `before|after|first|then|prior|until|once` returns nothing. (`afterwards` occurs twice, each time describing the state the customer sees once *this* call has completed, not a position relative to another call.)
- uuid8s: `363ec738`, `ec6b5130`, `a0bcb90e`, `3c2f355d`, `b90496cb`. Five distinct values; no shared prefix or suffix, no sequence, no adjacency, no reuse, no common stem with a changed tail. Each is frozen with its tool and appears in the charter only as that policy's `target_tool` and `resolved_by`.
- **Tool bodies judge nothing.** Every one of the five functions is a straight `ctx.make_id` + `ctx.create` + return-string; there is no branch, no `if`, no raised error, no eligibility read and no hint. A prerequisite left unresolved cannot be detected by the tool layer.

### prerequisite_graph

Check 7 over the whole graph.

- `prerequisite` is filled in on all five policies: `[]` on `custom_ext_change_consent` and `custom_ext_metal_market_reprice`; one edge each on the other three.
- Edges: `custom_ext_change_order_charge → custom_ext_change_consent`; `custom_ext_closure_consent → custom_ext_metal_market_reprice`; `custom_ext_closure_refund → custom_ext_closure_consent`.
- Every `problem` names another extended policy id in this file; none names a base policy and none names itself. The graph is a forest of two chains and is **acyclic**, including across the two tasks (no cross-task edge exists).
- `kind` is `value_input` on all three edges, and each `gate` is a real binding of the blocked policy's own `compute`: `agreed_change_value` (change_order_charge), `metal_adjustments` (closure_consent), `retained_confirmed` (closure_refund). None is a `state_gate` pointing at a non-gate.
- `form: state` on all three; no `fallback_reason` is present anywhere, which is correct because no edge is declared in the action form.
- `resolved_by` is in each case the depended-on policy's own `target_tool`, and each genuinely changes the gate binding's value: `confirm_specification_change_363ec738` creates the only `custom_intake` row with `request_type='change_order', request_status='customer_confirmed'` that `LATEST(...)` can read; `charge_metal_revaluation_a0bcb90e` creates the only `custom_ledger` row with `event_type='custom_price_adjustment_charged', charge_reason='metal_market'` that `SUM(...)` can read; `confirm_commission_closure_3c2f355d` creates the only `custom_intake` row with `request_type='cancellation', request_status='customer_confirmed'`.
- No `condition` is strengthened or weakened relative to the sentence it comes from (compared clause by clause in `prerequisite_sentences`).
- No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") appears anywhere in the three `prerequisite` blocks.

### prerequisite_sentences

Check 6, edge by edge. Each `policy_source` was located verbatim in the **blocked** policy's own `rule`.

**E1 — custom_ext_change_order_charge waits on custom_ext_change_consent.**
> "The charge for the agreed change is worked out only after the studio's request record carries the customer's own confirmation of the change and of what the work it puts back on the bench is worth."

Four-point test: (i) ordering connective — "only after"; (ii) form — state: what it waits on is a record-visible state ("the studio's request record carries … a confirmation of the change … and what the work is worth"), named in the words the finder uses (`find_custom_intake`: "Retrieve the requests a customer has raised with the design studio … whether the customer has confirmed it, … the revised total put to the customer"); (iii) names no tool, no policy id, no snake_case token, no row id; (iv) strength and scope match the edge's `condition` exactly. State-form priority honoured; no `fallback_reason` needed.
*One write brings it about:* only `confirm_specification_change_363ec738` writes a `customer_confirmed` request of type `change_order`; `confirm_commission_closure_3c2f355d` writes type `cancellation`, so the sentence's "confirmation **of the change**" resolves the hop uniquely.
*Derivation, single reading:* sentence → the request record must carry a customer-confirmed change request bearing the value of the work → `custom_ext_change_consent`'s own rule is the only rule that says what that value is ("A change to the specification agreed once the design has been approved is priced first as the value of the work it puts back on the bench, and that value is what the customer commits to when the studio takes their agreement down") → the studio takes the customer's agreement down, i.e. the customer's own write. No second reading.
*The rule carries nothing else about the dependency:* no tool name, no policy id, no second ordering sentence. (The rule's "The value of the work the customer has committed to is read from the confirmation of the change standing on the studio's request record, taken at the latest date such a confirmation is to take effect from" is the compute basis for the binding — it carries no ordering connective and states where a value is read, not that one problem waits on another. Recorded as an observation, not a second wording.) The depended-on policy's rule does not restate the sentence.

**E2 — custom_ext_closure_refund waits on custom_ext_closure_consent.**
> "The refund is worked out only after the studio's request record carries the customer's own confirmation of the closure and of the sum the studio keeps."

Same four points pass; "only after"; state form; no tool/id/token. *One write:* only `confirm_commission_closure_3c2f355d` writes a `customer_confirmed` request of type `cancellation`. *Derivation:* sentence → a customer-confirmed closure request bearing the sum kept must stand → `custom_ext_closure_consent`'s rule is the only rule that says what that sum is ("The sum the studio keeps when a commission is closed at the customer's request is …") and base `custom_cancellation_and_forfeit` says the cancellation is confirmed by the customer on the request record → the customer's own write. Single reading.

**E3 — custom_ext_closure_consent waits on custom_ext_metal_market_reprice.**
> "The sum the studio keeps is settled only after the commission's entries carry the repricing due where the metal price behind the quote has aged past the programme's revaluation window."

Four points pass: "only after"; state form ("the commission's entries carry the repricing …" — `find_custom_ledger`: "repricings for a movement in the metal market or for expedited production"); no tool name, no id, no token; scope matches the `condition`. *One write:* only `charge_metal_revaluation_a0bcb90e` books a `metal_market` price adjustment. *Derivation:* sentence → the entries must carry the repricing due for a metal price aged past the revaluation window → `custom_ext_metal_market_reprice`'s own rule is the only rule describing when such a repricing is due and how it is worked out → book it first. Single reading; the depended-on rule does not restate the sentence.

No rule in the charter states a cross-problem order that grounds no declared edge, and no base rule sentence is doing the work of an edge: all three edges rest on extended sentences of the blocked policy's own rule.

### override_declarations

Check 1, once, sentence by sentence against each `base_policy_refs` entry, and then over the whole base section for the conflict scan. Findings only; each affected task's file demonstrates the cost.

**custom_ext_change_consent → `custom_change_orders`, `custom_post_delivery_care`, `overwrite: []`.**
Sentence by sentence: "A change to the specification after the design has been approved is agreed as a change order, priced on its own and charged with the programme's change administration fee" governs the *charge*, not the value the customer commits to — change_consent computes a different quantity and neither follows nor displaces it. "A change to the specification is agreed only when the request reaches the studio within the change order window … counted from the date the customer approved the design" and "The change order window is counted in whole calendar days from the day the design was approved, that day counting as day zero" are inherited intact; change_consent recounts nothing. "No more changes are agreed on one commission than the programme allows" inherited intact. "The change itself is agreed by the customer on the commission service request record …" is *followed* — the target tool is `owner="user"` and writes `custom_intake`. Every sentence of `custom_post_delivery_care` concerns the period after delivery and governs no quantity change_consent computes. **`overwrite: []` is correct.** One inherited sentence has no write available (F6).

**custom_ext_change_order_charge → `custom_change_orders`, one `overwrite`.**
The declared entry names "A change to the specification after the design has been approved is agreed as a change order, priced on its own and charged with the programme's change administration fee" and replaces it with the five-part sum. That is the only base sentence whose quantity the extended handles differently: the administration fee's multiple (1.0/1.5/2.0) is a *refinement of the superseded sentence*, declared. The remaining sentences (change-order window, day-zero counting, maximum count, customer's own agreement) are inherited unchanged and none is weakened by extended, by a tool or by the persona. No anonymous intermediate, no 0/1 multiplier and no dropped branch: `admin_fee_multiple`'s fall-through reproduces exactly the base "the programme's fee for a change to the specification as the programme sets it". **Declarations complete.**

**custom_ext_metal_market_reprice → `custom_quoting_and_repricing`, two `overwrite` entries.**
Two base sentences are named and replaced (the revaluation trigger, and the pass-through/absorb branch). Sweeping the other five sentences of that base policy:
- "The quoted total is built from the design as approved …" — inherited, untouched.
- "The quote is booked to the commission only while it stands at consultation, design approval or deposit pending …" — inherited, untouched.
- **"The revaluation window is counted in whole calendar days from the day the metal price was taken, that day counting as day zero, weekends and market holidays included." — NOT named in any `overwrite`, and the extended rule fixes the same anchor differently.** See **F3**.
- "A stone sourced to order carries the programme's sourcing fee on the stone's cost, and the fee is shown as its own line rather than folded into the quote." — the extended folds the sourcing uplift into the single metal-market adjustment. The base sentence contrasts "its own line" with "folded into the *quote*", and the folding declared here is into the *adjustment*, so this is read as compatible; recorded as observation **F7**.
- "The design fee is charged where the programme charges one and credited against the quoted total …" / "The design fee is booked to the commission as its own entry under the design fee reason …" — inherited, untouched, and the seeds honour them.

**custom_ext_closure_consent → `custom_cancellation_and_forfeit`, one `overwrite`.**
The declared entry names "A commission is cancelled without the heavier forfeit only when the request reaches the studio within the cancellation window in calendar days, counted from the date the customer approved the design" and replaces it with the three-tier share ladder. Sweeping the rest:
- "A commission cancelled before the design is approved is closed with nothing forfeited beyond any consultation deposit the programme takes." — NOT named; the extended's fall-through tier would take the programme's lighter share (20 %) from such a commission. No world in either task has an unapproved design, so no consequence is demonstrable: observation only (listed under F2).
- "The cancellation window is counted in whole calendar days from the day the design was approved, that day counting as day zero, weekends and studio holidays included." — the extended uses the same anchor (the date the design was approved). Inherited compatibly.
- **"Cancelled before production begins, the commission forfeits the programme's lighter share of the quoted total; cancelled once production has begun, it forfeits the programme's heavier share, and the deposit's non-refundable share is never returned in either case." — NOT named in any `overwrite`, and the extended handles the same quantity differently in two independent ways.** See **F2** (the share) and **F5** (the non-refundable floor).
- "A piece already finished is not refunded at all …" — inherited, untouched.
- "The cancellation is confirmed by the customer on the commission service request record …" — followed; the target tool is `owner="user"`.

**custom_ext_closure_refund → `custom_cancellation_and_forfeit`, one `overwrite`.**
The declared entry names "The refund is what the customer has paid to date less what is forfeited, and where the forfeit exceeds what was paid nothing further is collected from the customer" and replaces it with the seven-part expression. Every other sentence of that base policy is inherited (and F2/F5 above already record what is not declared).

**Whole-base sweep beyond `base_policy_refs`.** Because base and extended are published together, the conflict scan also compared the extended computations against the base policies no extended policy cites. One base policy conflicts:
- `custom_agg_commission_portfolio`: "What the customer has paid to date on a commission is read as the sum of the deposits and staged payments booked to that commission, **and it is this figure, not the quoted total, that any forfeit is taken against.**"
  - against `custom_ext_closure_consent`, which takes the forfeit share on `F('quoted_total')` — **F2**;
  - against `custom_ext_closure_refund`'s `money_put_in_source`, whose first two tiers read what the customer has put in from the financing plan rather than from the commission's deposits and staged payments — **F4**;
  - and against base `custom_cancellation_and_forfeit`'s own "the programme's lighter share **of the quoted total**" — a base-against-base contradiction, **F1**.
- `custom_agg_multi_holding`, `custom_commission_admission`, `custom_design_revisions`, `custom_payment_schedule`, `custom_production_schedule`, `custom_delivery` and `custom_post_delivery_care` were swept sentence by sentence against all five extended computations and conflict with none of them.

### factor_ladders

Structure only; weight is per task.

| policy | factor | effect | decides | tiers | multi-source tiers | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| change_consent | revision_overage_multiple | parameter | revision_multiple | 3 | yes (custom_ledger revisions × custom_orders.production_start_date) | — |
| change_consent | rendering_and_model_charge | parameter | model_charge | 3 | yes (variant parameters × custom_ledger revision rows) | — |
| change_consent | centre_stone_handling_rate | parameter | stone_handling_pct | 3 | yes (custom_orders.center_stone_source × custom_ledger milestones) | — |
| change_consent | commission_worth_source | method | commission_worth | 3 | yes (financing_plans × custom_orders/custom_ledger) | financing |
| change_consent | market_movement_fraction | method | market_movement_factor | 3 | yes (price-adjustment rows × milestone rows) | — |
| change_order_charge | administration_fee_multiple | parameter | admin_fee_multiple | 3 | yes (custom_ledger charges × custom_orders.production_start_date) | — |
| change_order_charge | bench_reopening_rate | parameter | reopen_rate_pct | 3 | yes (custom_orders.rush_requested × custom_ledger milestones) | — |
| change_order_charge | metal_recasting_premium | parameter | metal_premium_pct | 3 | yes (custom_orders.metal_choice × custom_ledger casting rows) | — |
| change_order_charge | bench_day_clock_anchor | method | bench_day_anchor | 3 | yes (stone-setting rows × final-inspection rows) | — |
| change_order_charge | bench_daily_rate | parameter | bench_day_rate | 3 | yes (custom_orders.quoted_total vs variant bounds × elapsed bench days) | — |
| change_order_charge | upgrade_credit_settlement | parameter | credit_settlement_pct | 3 | single record (tradein_credits row) | tradein |
| metal_market_reprice | revaluation_clock_anchor | method | basis_anchor | 3 | yes (custom_orders.design_approved_date × custom_ledger deposit rows) | — |
| metal_market_reprice | metal_escalation_rate | parameter | escalation_pct | 3 | yes (custom_orders.metal_choice × custom_ledger quote metal price) | — |
| metal_market_reprice | stone_sourcing_uplift_rate | parameter | sourcing_uplift_pct | 3 | yes (custom_orders.center_stone_source × custom_ledger stone-upgrade rows) | — |
| metal_market_reprice | movement_pass_share | parameter | pass_share_pct | 3 | single record (financing_plans row) | financing |
| metal_market_reprice | late_start_relief_fraction | method | market_relief_factor | 3 | yes (custom_ledger deposit rows × custom_orders.production_start_date) | — |
| closure_consent | closure_forfeit_share | parameter | forfeit_pct | 3 | yes (custom_ledger milestones × custom_orders.completed_date/design_approved_date) | — |
| closure_consent | design_fee_retention | parameter | design_fee_kept_pct | 3 | yes (revision rows × overage-flagged revision rows) | — |
| closure_consent | metal_repricing_retention | parameter | metal_kept_pct | 3 | yes (custom_ledger metal-market rows × custom_orders.production_start_date) | — |
| closure_consent | upgrade_credit_restoration | parameter | credit_restored_pct | 3 | single record (tradein_credits row) | tradein |
| closure_consent | overdue_closure_relief | method | closure_relief_factor | 3 | yes (custom_orders.promised_delivery_date × custom_orders.completed_date) | — |
| closure_refund | money_put_in_source | method | paid_to_date | 3 | yes (financing_plans × financing_ledger × custom_ledger) | financing |
| closure_refund | centre_stone_holdback | parameter | stone_holdback_pct | 3 | yes (custom_orders.center_stone_carat × custom_ledger milestones) | — |
| closure_refund | slow_design_goodwill | parameter | goodwill_pct | 3 | yes (custom_orders dates × custom_ledger milestones) | — |
| closure_refund | revision_overage_setoff | parameter | overage_setoff_pct | 3 | yes (custom_ledger overage rows × custom_orders.balance_due) | — |
| closure_refund | bundled_coverage_return | parameter | coverage_return_pct | 3 | single record (protection_plans row) | protection |

Counts per policy: 5 / 6 / 5 / 5 / 5 factors — all inside 4–6. `parameter` counts 3 / 5 / 3 / 4 / 4 — all ≥ 2. `method` counts 2 / 1 / 2 / 1 / 1 — all ≥ 1. Every ladder has exactly three tiers, the fall-through counted, and the three conditions of each ladder are pairwise disjoint as stated (checked clause by clause: each ladder's first two tiers carry mutually exclusive conjuncts and the third is `otherwise`).

Per task: task 0's policies carry a multi-source factor (e.g. `administration_fee_multiple`) and two cross-difficulty factors (`commission_worth_source` → financing, `upgrade_credit_settlement` → tradein). Task 1's carry a multi-source factor (e.g. `revaluation_clock_anchor`) and three cross-difficulty factors (`movement_pass_share` → financing, `upgrade_credit_restoration` → tradein, `money_put_in_source` → financing, `bundled_coverage_return` → protection).

**`decides` is an input in every case**, never `result`; every `decides` name is a real binding; and the `bindings` sets of the factors within one policy are pairwise disjoint (checked by script; no binding is claimed by two factors).

**Labels are honest.** Each `method` factor changes the algorithm rather than a number: `commission_worth_source` and `money_put_in_source` change which record a quantity is read from; `bench_day_clock_anchor` and `revaluation_clock_anchor` change which dated event a day-count runs from; `market_movement_fraction`, `late_start_relief_fraction` and `overdue_closure_relief` change whether a fraction is taken at all and which one. Each is a computation rule the `rule` states in prose. Each `parameter` factor substitutes a rate, a multiple, a charge or a share into a formula whose shape does not change.

**Distinct outcomes.** No two tiers of any ladder select the same value or the same method as written. One ladder, however, has a tier that can never produce an outcome different from its fall-through — recorded as observation **F8**.

**Realism of conditions and outcomes.** Every tier's condition is something a design studio actually weighs for the quantity in hand (whether the bench has already started, how many revisions have been drawn, what metal is being cast, whether the customer supplied the stone, whether the sale sits on a store financing plan, whether an upgrade credit is live, how far past the promise the piece is, how long the design took), and none holds of every customer who reaches the write. Every tier's outcome, the fall-throughs included, is a treatment a fine-jewellery studio would publish: nothing charged for a revision still inside the included allowance, nothing charged for a rendering the programme includes, no premium for a metal not yet cast, no relief where the piece is not late, the published change fee where nothing aggravates it, the whole of the movement passed on where no financing plan intervenes.

### findings

**F1 — SOURCE-POLICY RED. Two base policies fix the forfeit base differently (base against base).**
- *Symptom.* The forfeit on a cancelled commission has two bases in the charter in force.
- *Root cause.* `custom_cancellation_and_forfeit` (base): "Cancelled before production begins, the commission forfeits the programme's lighter share **of the quoted total**". `custom_agg_commission_portfolio` (base): "What the customer has paid to date on a commission is read as the sum of the deposits and staged payments booked to that commission, and it is this figure, **not the quoted total**, that any forfeit is taken against." The second sentence names and forbids exactly what the first prescribes.
- *Evidence.* `env/env_0001_fine_jewelry_retailer/tasks/custom_commission_desk/custom.extended.yaml`, `policies[custom_cancellation_and_forfeit].rule` and `policies[custom_agg_commission_portfolio].rule`; both byte-identical to `env/env_0001_fine_jewelry_retailer/blueprint/products/custom.yaml`.
- *Consequence.* Demonstrated on task 1 in `1.md § policy_self_consistency`.
- *Affected artifact.* `blueprint/products/custom.yaml` and its verbatim copy in the extended charter; bears on task 1 only.

**F2 — SOURCE-POLICY RED. Undeclared override: the forfeit share and its base in `custom_ext_closure_consent`.**
- *Symptom.* Three different shares of three different bases are each defensible for the same scored quantity.
- *Root cause.* `custom_ext_closure_consent.overwrite` names one base sentence only (the cancellation-window sentence, `custom_cancellation_and_forfeit` D2). It does not name "Cancelled before production begins, the commission forfeits the programme's lighter share of the quoted total", which remains in force and fixes the share for a commission cancelled before production at the *lighter* share; nor does it name `custom_agg_commission_portfolio`'s "not the quoted total", which remains in force and fixes the *base*.
- *Evidence.* `extended_policies[custom_ext_closure_consent].overwrite` (one entry), `.rule` ("the share is the studio's late closure share"), `.compute[forfeit_pct]` and `.compute[share_amount] = RND(F('quoted_total') * forfeit_pct / 100, 2)`; against the two base rule sentences quoted in F1.
- *Consequence.* Demonstrated on task 1 in `1.md § policy_self_consistency` (three values for the same parameter).
- *Affected artifact.* `custom.extended.yaml`, `extended_policies[3]`; bears on task 1 only.

**F3 — SOURCE-POLICY RED. Undeclared override: the revaluation clock's anchor in `custom_ext_metal_market_reprice`.**
- *Symptom.* The days the metal price has aged are counted from two different days, giving two different period counts and two different adjustments.
- *Root cause.* `overwrite` names `custom_quoting_and_repricing`'s trigger sentence, which happens to contain the phrase "counted from the date the metal price behind the quote was taken", but leaves standing the separate base sentence "**The revaluation window is counted in whole calendar days from the day the metal price was taken, that day counting as day zero**, weekends and market holidays included." The extended's `revaluation_clock_anchor` moves that anchor to the design-approval date (tier 1) or the consultation date (tier 2). This is the "anonymous intermediate" shape: the override hides inside `basis_anchor` and no new parameter name appears.
- *Evidence.* `extended_policies[custom_ext_metal_market_reprice].overwrite` (two entries, neither naming the counting sentence); `.rule` ("counted from the day the studio's own clock for the quote starts running"); `.compute[basis_anchor]`; against `policies[custom_quoting_and_repricing].rule`, sentence 4.
- *Consequence.* Demonstrated on task 1 in `1.md § policy_self_consistency`, and it cascades through both later writes of that task.
- *Affected artifact.* `custom.extended.yaml`, `extended_policies[2]`; bears on task 1 only.

**F4 — SOURCE-POLICY RED. Undeclared override: what the customer has paid to date, in `custom_ext_closure_refund`.**
- *Symptom.* "What the customer has put into the commission" has two defensible values.
- *Root cause.* `custom_ext_closure_refund.overwrite` names only the refund-arithmetic sentence of `custom_cancellation_and_forfeit`. Base `custom_agg_commission_portfolio` — "What the customer has paid to date on a commission is read as the sum of the deposits and staged payments booked to that commission" — stays in force and is reproduced word for word by the extended's own fall-through tier and by `baseline.rule`; the first two tiers of `money_put_in_source` read the figure from the financing plan instead. The measure `custom_msr_paid_to_date` in the base section fixes the same reading.
- *Evidence.* `extended_policies[custom_ext_closure_refund].overwrite` (one entry); `.factors[money_put_in_source].ladder` tiers 1 and 2; `.compute[paid_to_date]`; against `policies[custom_agg_commission_portfolio].rule` and `measures[custom_msr_paid_to_date]`.
- *Consequence.* Demonstrated on task 1 in `1.md § policy_self_consistency`.
- *Affected artifact.* `custom.extended.yaml`, `extended_policies[4]`; bears on task 1 only.

**F5 — SOURCE-POLICY RED. Undeclared override: the deposit's non-refundable share is never applied.**
- *Symptom.* Base fixes a floor on what the studio keeps that the extended computation can fall below, without declaring it displaced.
- *Root cause.* `custom_cancellation_and_forfeit`: "… and **the deposit's non-refundable share is never returned in either case**", with `deposit_nonrefundable_pct` a first-class programme parameter in `parameter_schema` and set per variant. Neither `custom_ext_closure_consent` nor `custom_ext_closure_refund` names this sentence in `overwrite`, and neither `compute` reads `deposit_nonrefundable_pct` — the parameter is declared by the charter and used by no policy.
- *Evidence.* `policies[custom_cancellation_and_forfeit].rule`; `parameter_schema.deposit_nonrefundable_pct`; `variants[*].parameters.deposit_nonrefundable_pct`; absence of `deposit_nonrefundable_pct` from every `compute` in `extended_policies`.
- *Consequence.* Demonstrated on task 1 in `1.md § policy_self_consistency`.
- *Affected artifact.* `custom.extended.yaml`, `extended_policies[3]` and `[4]`; bears on task 1 only.

**F6 — Observation. An inherited base consequence with no write available.**
`custom_change_orders`: "A change agreed while the piece is in production puts the commission on hold until the revised specification is written, and the promised delivery date is moved out accordingly." The sentence is inherited intact by both task-0 policies, and task 0's commission stands `in_production`. No tool in `task_tools.py` or `share_tools.py` can move a commission to `on_hold` or move the promised delivery date, so the terminal state this base sentence prescribes is unreachable. No scored quantity turns on it, so this is an observation rather than a red light; it is recorded because a reader of the published KB will find an instruction they cannot carry out. Bears on task 0.

**F7 — Observation. The sourcing fee's "own line".**
`custom_quoting_and_repricing`: "A stone sourced to order carries the programme's sourcing fee on the stone's cost, and the fee is shown as its own line rather than folded into the quote." `custom_ext_metal_market_reprice` adds the sourcing uplift into the single metal-market adjustment entry rather than booking it separately, and the tool books one ledger row. Read strictly, the base sentence contrasts "its own line" with being folded into *the quote*, not with being folded into an adjustment, so no contradiction is demonstrable; recorded because the two readings give different ledger shapes (one entry of 661.32 versus 560.52 plus 100.80 on task 1's world). Bears on task 1.

**F8 — Observation. A tier that cannot differ from its fall-through.**
`custom_ext_metal_market_reprice.factors[stone_sourcing_uplift_rate]` decides `sourcing_uplift_pct`, which is applied as `sourcing_uplift = RND(stone_upgrade_charges * sourcing_uplift_pct / 100, 2)`. Tier 2's condition is "the centre stone is one sourced to order **and no charge for a stone upgrade stands booked**", i.e. `stone_upgrade_charges == 0`; the product is therefore 0.00 under tier 2 exactly as it is under the fall-through, whatever rate tier 2 names. The rule's own words say it out loud — "the studio's rate for an unpriced sourced stone is added **on that charge**", where that charge is nil. The tiers select distinct values (3.0 against 0.0), so the letter of the "no two tiers select the same value" test is met and this is not recorded as a red light; the tier nevertheless divides the studio's customers without ever dividing the figure. Bears on task 1 (whose gold path takes tier 1, so the factor does bear weight there).

**F9 — Observation. `custom_intake` rows written by the two `owner=user` tools carry no `customer_id`.**
`confirm_specification_change_363ec738` and `confirm_commission_closure_3c2f355d` call `ctx.create("custom_intake", …)` without `customer_id`, although `db_schema.json` declares `custom_intake.customer_id` and `find_custom_intake` offers it as a search key. An agent that reads the request back by `customer_id` will not see the row it just created; by `custom_order_id` it will. No scored value turns on it — both `LATEST('custom_intake', …)` bindings scope by `custom_order_id`. Bears on both tasks.

**F10 — Observation. Compute filters narrower than their rule sentences.**
Listed in full under `rule_compute_equivalence`: `status='partially_redeemed'` for the trade-in holding (change_order_charge, closure_consent) where the rule says only "an upgrade registration with credit still available"; `status == 'active'` for "that plan still stands open" (change_consent); `NOW` for "the closure reaches the studio" (closure_consent). In neither task's world does a record exist that the rule admits and the filter excludes, so no consequence is demonstrable. Bears on both tasks.

## closing_checklist

Written after both tasks' `source_gt_comparison` sections were on disk. **This difficulty does not close.** Step 4's list, item by item, with the state actually reached:

- **Per-task audit files correspond one-to-one with the tasks, and `_difficulty.md` sits alongside them.** ✔ `0.md`, `1.md` and this file, in `env/env_0001_fine_jewelry_retailer/audits/policy_task/custom_commission_desk/`. This is revision 1, so there is no older revision to preserve; any re-audit appends under `## revision_2` and leaves the text above untouched.
- **Every comparison section carries a PASS.** ✘ `0.md` carries PASS on all four relationships; `1.md` carries **SOURCE-POLICY RED** (F1–F5, demonstrated against its own world) and records the unique-solution relationship as not determinable while the policy contradicts itself.
- **The difficulty's extended policies are fully covered and the tasks' scopes are pairwise disjoint.** ✔ Task 0 claims `{custom_ext_change_consent, custom_ext_change_order_charge}` with tools `confirm_specification_change_363ec738` and `charge_specification_change_ec6b5130`; task 1 claims `{custom_ext_metal_market_reprice, custom_ext_closure_consent, custom_ext_closure_refund}` with `charge_metal_revaluation_a0bcb90e`, `confirm_commission_closure_3c2f355d` and `issue_commission_refund_b90496cb`. Each scope spans a whole problem tree — its root and all of its prerequisite problems — the two share no policy, tool or subject event, and together they cover all five extended policies and all five task tools. Independently derived, then confirmed against `charter_scope` on both tasks.
- **Task tools and GT are closed, and each task tool uses an independently generated, frozen uuid8.** ✔ See § `action_binding_and_uuids`: `363ec738`, `ec6b5130`, `a0bcb90e`, `3c2f355d`, `b90496cb` — distinct, unreused, not batch-derived.
- **Every task's problem tree has one to three prerequisite problems, at least max(n − 1, 1) `value_input` edges, at least one problem resolved by an `owner=user` tool, and no cycle; and the difficulty's `prerequisite` edges together remain a DAG.** ✔ Task 0: n = 1, one `value_input` edge, `confirm_specification_change_363ec738` is `owner=user`. Task 1: n = 2, two `value_input` edges, `confirm_commission_closure_3c2f355d` is `owner=user`. The three edges of the difficulty form two disjoint chains with no cross-task reference and no cycle.
- **Every computation declares a self-sufficient baseline and four to six factors (2 `parameter`, 1 `method`; per task at least 1 multi-source and 1 cross-difficulty), every ladder of at least three tiers stated in full in its rule, tiers distinct in outcome, conditions and outcomes ones the line of business actually holds, and every factor proved to bear weight against an honest baseline with the baseline alone giving a definite number different from gold.** ✔ with one observation. Five computations, 26 factors, every one of which bears weight on its own task's world (11 checked in `0.md § factor_weight`, 15 in `1.md § factor_weight`); every declared `baseline` recomputed from its `baseline.rule` and found honest; whole-baseline figures 0.00 / 1379.30 / 830.40 / 6920.00 / 11787.70 against golds 1205.30 / 1487.68 / 661.32 / 5512.30 / 1603.55. Observations F8 (a tier of `stone_sourcing_uplift_rate` that cannot differ from its fall-through) and O-0.3 in `0.md` (a whole baseline that is identically zero) stand against this item without meeting the red-light bar.
- **The difficulty's instantiation-stage gates are re-run once on the final form.** Not applicable at this revision: the audit edited no artifact, so the artifacts stand exactly as the coordinator's gate snapshot found them (EXTENDED / TASK-TOOL-CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all green, `check_traceability` excluded for want of a published KB). That snapshot is cited, not re-run, and it is the qualification to have audited — not evidence that the four relationships hold. It did not detect F1–F5, which is expected: no script can decide whether two sentences of a structured policy reach compatible conclusions in the same situation.

**Difficulty-level verdict.** `custom_commission_desk` fails the source-layer audit on **policy self-consistency**. Task 0 passes all four relationships. Task 1 holds on the problem tree and on the factors, and its scored solution is exactly the one an independent derivation reaches on the extended reading, but five base sentences in force over it — three of them naming the very quantities the extended policies compute, and one of them (`custom_agg_commission_portfolio`) contradicting another base sentence directly — are named in no `overwrite`, so the policy does not entail one solution. Reported as found; no artifact was edited and no fix is arranged here.

## revision_2

*Round-2 re-audit. Everything above this heading is revision 1 and is left untouched.*

### charter_global_frozen (revision 2)

- written **before** any round-2 GT field was read; the reworker's claims were taken as a checklist to verify, never as evidence.
- freeze hashes after rework: `custom.extended.yaml` sha256 `154bcc7bb56852e226bd0f1a7a8d52a8457842f1bdc23d789b244fd936fb0813` (was `847b7f02…`); `task_tools.py` sha256 `ea19e57f6de3d54d1bb956cd94f5aed681f80d782071f49a034f1dfad0fd064b` (was `d92b4094…`). **Both inputs of every charter-global section moved, so every section below is re-derived in full** rather than carried forward.
- masked views: `0.json` `17928c82…` **unchanged**; `1.json` `c6d52f3d0d3ce9c3e880ce55c54d67be45d4eb444f8dbded9dadf640ea82de28` (was `d791f35b…`). What actually moved in `1.json` was verified mechanically against the coordinator's round-1 backup, extracting only the three whitelisted keys: `frozen_time` identical, `initial_state` identical row for row, and exactly one sentence of `user_scenario` changed — "what she wants today is putting the commission to an end properly and then what is coming back to her and paid out" → "what she wants today is the commission finished with and whatever is coming back to her paid out". The reworker's account of the persona change is accurate.
- read-domain widening honoured: `blueprint/products/financing.yaml`, `tradein.yaml` and `protection.yaml` were read this round, so the cross-category seed check that revision 1 recorded as not performed is performed below.
- entry conditions: the coordinator's round-2 gate snapshot (all green, `check_traceability` excluded) was supplied and is cited as the qualification to re-audit.

### what moved in the charter (mechanical diff, round 1 → round 2)

Base section: still byte-identical to `blueprint/products/custom.yaml` on every key. `custom_ext_change_consent` and `custom_ext_change_order_charge`: **no change of any kind** (rule, compute, basis, factors, baseline, overwrite, prerequisite all identical). The three task-1 policies:

- `custom_ext_metal_market_reprice`: `overwrite` 2 → 4 (adds the day-zero counting sentence and the sourcing-fee own-line sentence); the rule's counting sentence rewritten to state the convention in full; the sourcing-uplift ladder re-based (tier 2 now "on the quoted total"); one new binding `sourcing_uplift_base` with its basis sentence; baseline updated accordingly.
- `custom_ext_closure_consent`: `base_policy_refs` gains `custom_agg_commission_portfolio`; `overwrite` 1 → 4 (adds the lighter/heavier-share sentence, the non-refundable-share clause, and the "not the quoted total" clause); rule gains a scoping sentence for design-approved commissions, a forfeit-basis sentence and a non-refundable-share sentence; forfeit tier 2 reworded "reaches the studio" → "is confirmed"; the credit-restoration tiers reworded to "standing part spent"; baseline updated.
- `custom_ext_closure_refund`: `base_policy_refs` gains `custom_agg_commission_portfolio`; `overwrite` 1 → 3 (adds the paid-to-date clause and the non-refundable-share clause); rule gains a linking sentence ("What the customer has put into the commission is what they have paid to date on it") and a non-refundable-share sentence; baseline updated. Compute unchanged.
- `task_tools.py`: only `confirm_commission_closure_3c2f355d` changed — a `customer_id: str` parameter added (docstring, `make_id` and `ctx.create(customer_id=…)`). The other four tools are byte-identical.

### policy_conflict_scan (revision 2)

Subjects, `computes`, target tools and triggers are unchanged and still partition without overlap. Task scopes are unchanged and still mutually exclusive and jointly complete. The five conflicts revision 1 recorded (F1–F5) were each re-tested against the reworked charter; the result per item is in `findings (revision 2)`. **No conflict between base and extended remains that is not named in an `overwrite`**, on a sentence-by-sentence sweep of every base policy against every extended computation, repeated in full this round.

### rule_compute_equivalence (revision 2)

Re-run mechanically and by hand over all five policies on the new file: every binding has a basis and every basis is a binding; every `compute_basis` quotation is verbatim in its `rule`; every `baseline.rule` sentence is verbatim in its `rule`; every ladder tier is a branch of its `decides` binding and vice versa; `baseline.params` unchanged and correct. New binding `sourcing_uplift_base: stone_upgrade_charges if stone_upgrade_charges > 0 else F('quoted_total')` carries the basis "The sourcing uplift is taken on the charge for a stone upgrade booked to the commission where one stands, and on the quoted total where none stands", and the uplift ladder's tier 2 now reads "the studio's rate for an unpriced sourced stone on the quoted total" — rule and compute agree. The compute filters revision 1 listed as narrower than their rules are now: `status='partially_redeemed'` in closure_consent **matched by the rule** ("standing part spent"); the forfeit tier's "the closure reaches the studio" **replaced by "is confirmed"**, which is the handling date the compute uses; `status='partially_redeemed'` in change_order_charge and `status == 'active'` for "still stands open" in change_consent **unchanged** (task 0 untouched), still consequence-free on task 0's world. The five pronoun/abbreviation expansions between ladder text and rule text persist unchanged (observation only). Rounding-mode observation unchanged.

### action_binding_and_uuids (revision 2)

Unchanged pairs, unchanged uuid8s (`363ec738`, `ec6b5130`, `a0bcb90e`, `3c2f355d`, `b90496cb`). The new `customer_id` argument on `confirm_commission_closure_3c2f355d` is Id-class, documented ("the reference number of the customer closing the commission, as read from the customer lookup that found the caller"), has exactly one reachable value on task 1's world (one profile, returned by `find_customers`), and enters `make_id` and the created row; it adds no branch, no read and no error — the function body is still `make_id` + one `create` + a return string. `grep -i` for ordering words over the module still returns none (the two "afterwards" describe the state after the call itself). No docstring names another tool.

### prerequisite_graph and prerequisite_sentences (revision 2)

Unchanged edges, kinds, gates, forms, `resolved_by`, conditions and `policy_source` sentences; each `policy_source` re-located verbatim in its own (rewritten) rule. The three rules gained sentences this round; none of the new sentences states a cross-problem order or restates a dependency: "This settlement is for a commission whose design stands approved when it is closed…" scopes the policy, and "…the closure is confirmed after the programme's cancellation window has run…" is a within-tier time comparison, not an ordering of problems. E1–E3 derivations of revision 1 stand unchanged.

### override_declarations (revision 2)

Every `overwrite` entry on the new file was tested three ways by script and confirmed by hand: **`superseded_clause` verbatim in the named base policy's rule — 12/12 true; `replaced_by` verbatim in the extended rule — 12/12 true; the named `base_policy` present in `base_policy_refs` — 12/12 true.** Sentence-by-sentence sweep of every `base_policy_refs` entry and of the whole base section:

- `custom_ext_change_consent`, `custom_ext_change_order_charge`: unchanged; conclusions of revision 1 stand (`overwrite: []` correct; one complete declaration).
- `custom_ext_metal_market_reprice` → `custom_quoting_and_repricing`: the four sentences the extended handles differently (trigger, pass-through branch, **day-zero counting, sourcing fee's own line**) are now all named. Remaining base sentences (quote built at the day's price; quote bookable at consultation/design approval/deposit pending; design fee charged, credited and booked as its own entry) inherited compatibly. Merged reading of the count: the studio's clock anchor, day zero at the anchor, to the day of booking, window off, whole thirty-day periods — one reading.
- `custom_ext_closure_consent` → `custom_cancellation_and_forfeit` + `custom_agg_commission_portfolio`: "Cancelled before production begins … heavier share" named and replaced by the ladder; "the deposit's non-refundable share is never returned in either case" named and replaced by "…sets no floor beneath that sum"; "it is this figure, not the quoted total, that any forfeit is taken against" named and replaced by "The forfeit share is taken against the quoted total … and not against what the customer has paid to date." "A commission cancelled before the design is approved is closed with nothing forfeited…" is no longer in tension: the rule now says such a closure "is outside it and is closed on the programme's own terms for that case". Window-counting sentence, finished-piece sentence and customer's-own-confirmation sentence inherited compatibly. **Merged reading unique: share ladder on the quoted total, no deposit floor.**
- `custom_ext_closure_refund` → `custom_cancellation_and_forfeit` + `custom_agg_commission_portfolio`: refund-arithmetic sentence, "What the customer has paid to date … deposits and staged payments booked to that commission" and the non-refundable clause all named. The rule's new sentence "What the customer has put into the commission is what they have paid to date on it" ties the extended term to the base term so the override is legible. **Merged reading unique: the money-put-in ladder, no deposit floor.**
- The one base sentence two policies both supersede (the non-refundable clause) has two `replaced_by` texts; they say the same thing (no floor beneath the sum kept / nothing held back on its account) and cannot yield different figures. Noted, not a finding.
- Base measure `custom_msr_paid_to_date` still defines the paid-to-date measure as the ledger sum. It is a measure, not a rule sentence, and the extended rule now expressly ties "what the customer has put in" to "what they have paid to date" and then overrides the base reading by a named `overwrite`; no second reading survives. Noted.

### factor_ladders (revision 2)

Structure unchanged except `stone_sourcing_uplift_rate`: its tier 2 now yields 3.0 % **of the quoted total** where no stone-upgrade charge stands, so its three tiers produce three distinct outcomes on any world — revision 1's observation F8 is closed. `upgrade_credit_restoration`'s tier conditions now read "standing part spent with credit still available", matching the compute; each condition is still one the desk weighs and holds of no customer automatically. Counts unchanged: 5/6/5/5/5 factors, `parameter` 3/5/3/4/4, `method` 2/1/2/1/1, every ladder three disjoint tiers, `decides` never `result`, bindings disjoint. All 26 factors re-proved to bear weight on their task's world this round (`0.md`/`1.md` § revision_2).

### cross-category seeds against their own charters (new this round)

- **financing** (both tasks): `original_principal = ticket − down_payment` (13800−5520=8280; 17300−5300=12000) ✔; down payments 40 % and 30.6 % clear the terms' 10 % / 15 % minimum ✔; `promo_end_date` = activation + `promo_term_months` (2026-09-09+24m; 2026-05-20+36m) ✔; payments posted while `active` ✔; the `returned_nsf` payment leaves `current_balance = 12000 − 3×640 = 10080` ✔. The finance charter's "a plan counts as open while it stands at applied, approved, active, past due or in a hardship arrangement" confirms revision 1's F10 note on change_consent's "still stands open" (task 0; no seeded plan is past due, so no consequence).
- **tradein**: fields the factors read — `status`, `remaining_credit`, `original_sales_receipt_number`, `upgrade_minimum_spend` — are consistent with the charter (partially_redeemed is a live state; a piece the chain did not sell carries an empty receipt on the revoked row). Two fields the factors do **not** read disagree with the charter: `expiry_date` is set on the Lifetime Diamond Upgrade Guarantee row (`credit_validity_days = 0`, "0 where the credit does not expire"; schema: "empty on credit that does not expire"), and on the Diamond Trade-Up Guarantee row it sits 731 days after issue against `credit_validity_days = 365` (+90 extension at most). `upgrade_minimum_spend` on the rows (2500.00; 4000.00) is far below what the charter's own rule would compute (twice the credit and twice the original price). On task 0 the tier that reads it is unchanged under either figure (1850.00 is below both). Recorded as observation **F11**.
- **protection** (task 1): fields the factor reads — `status='active'`, `premium_paid_to_date`, `claims_settled_count` — consistent; the Care Plan 3-Year row's 36-month term and single payment match its variant. Two unread fields disagree: the Heirloom row carries `expiry_date = 2036-05-20` against `coverage_term_months = 0` ("0 where coverage does not run to a fixed term"; schema: "empty on coverage that does not expire"), and `effective_date = purchased_date` against `waiting_period_days = 30`. Recorded under **F11**.

### findings (revision 2)

**F1 — CLOSED as a red light for this difficulty; residual observation.** The extended side now fixes one reading: `custom_ext_closure_consent` names both base sentences (`custom_cancellation_and_forfeit`'s "…lighter share of the quoted total…" and `custom_agg_commission_portfolio`'s "…not the quoted total…") in `overwrite` and states "The forfeit share is taken against the quoted total recorded on the commission and not against what the customer has paid to date." A reader of the merged policy has one base for the forfeit. *Residual:* the two base sentences still contradict each other inside `blueprint/products/custom.yaml`; the only forfeit in this category is the cancellation forfeit, which this difficulty's extended policy now governs, so no reader of this difficulty is left with two readings. Observation for the blueprint's owner; not a red light here.

**F2 — CLOSED.** "Cancelled before production begins, the commission forfeits the programme's lighter share of the quoted total; cancelled once production has begun, it forfeits the programme's heavier share" is named verbatim and replaced by the ladder verbatim; the ladder's tier 2 now keys on the confirmation date the compute uses. One reading.

**F3 — CLOSED.** "The revaluation window is counted in whole calendar days from the day the metal price was taken, that day counting as day zero, weekends and market holidays included." is named verbatim and replaced by a full counting convention anchored on the studio's clock, verbatim in the rule and in `baseline.rule`. The anonymous intermediate is now a declared one. One reading.

**F4 — CLOSED.** "What the customer has paid to date on a commission is read as the sum of the deposits and staged payments booked to that commission" is named verbatim and replaced by the money-put-in ladder verbatim; the rule ties the two terms together. One reading.

**F5 — CLOSED; realism observation.** "the deposit's non-refundable share is never returned in either case" is named in both closure policies and replaced, in each, by a sentence stating it sets no floor / nothing is held back on its account. One reading. *Observation:* `deposit_nonrefundable_pct` remains a first-class programme parameter in `parameter_schema` and all six variants while the extended policies now declare it inert on every closure this difficulty handles — the parameter is published and never applied. Not a red light: the declaration is explicit, the merged reading is unique, and no tier or outcome rests on it.

**F6 — unchanged observation** (task 0 untouched).

**F7 — CLOSED.** The own-line sentence is named and replaced ("…charged within the repricing entry together with the escalation, as one entry under the metal market reason, and not as its own line").

**F8 — CLOSED.** Tier 2 of `stone_sourcing_uplift_rate` now applies its rate to the quoted total, so it can no longer coincide with the fall-through.

**F9 — half closed.** `confirm_commission_closure_3c2f355d` now writes `customer_id`; `confirm_specification_change_363ec738` (task 0) still does not. Observation stands for task 0 only.

**F10 — closed for task 1's policies, stands for task 0's** (`status='partially_redeemed'` in change_order_charge; `status == 'active'` for "still stands open" in change_consent). No consequence on task 0's world.

**F11 — Observation (new; visible only because the read domain was widened).** Seeded cross-category rows carry fields that disagree with the financing/tradein/protection charters — `tradein_credits.expiry_date` and `upgrade_minimum_spend` (both tasks), `protection_plans.expiry_date` and `effective_date` (task 1) — as itemised above. None of these fields is read by any factor of either task, every tier taken rests on fields the seeds and charters agree on, and substituting the charter-consistent values changes no tier and no scored figure. Below the red-light bar; recorded because the seed should not contradict the constitution it lives under. Affected artifacts: `tasks/0.json` and `tasks/1.json` → `initial_state.tradein_credits`, `tasks/1.json` → `initial_state.protection_plans`.

**No new defect of the reworked charter or tool module was found**: every new sentence is verbatim in both faces where it must be, no new sentence orders problems, the new tool argument has one reachable value, and the reworked ladder tier rests on `custom_orders.quoted_total` and the stone-upgrade rows, both seeded.

### closing_checklist (revision 2)

Written after both revision_2 comparisons were on disk. **This difficulty closes at revision 2.**

- Per-task files correspond one-to-one with the tasks, `_difficulty.md` sits alongside, revision 1 is preserved verbatim under its own headings and revision 2 is appended; both `source_gt_comparison (revision 2)` sections carry **PASS**. ✔
- Extended policies fully covered; scopes pairwise disjoint and jointly complete (unchanged `charter_scope` on both tasks, re-verified). ✔
- Task tools and GT closed; five independently generated uuid8s unchanged; the one tool signature change (`customer_id` on `confirm_commission_closure_3c2f355d`) has a single reachable value and is carried in gold and in its tracing. ✔
- Problem trees: task 0 n=1 with one `value_input` edge; task 1 n=2 with two; one `owner=user` write in each; no cycle; the difficulty's three edges still form two disjoint chains. ✔
- Factors: 26 declared over five computations, 4–6 each with ≥2 `parameter` and ≥1 `method`; per task ≥1 multi-source and ≥1 cross-difficulty; every ladder three disjoint tiers stated in full in its rule and now distinct in outcome on every world (F8 closed); every factor re-proved to bear weight against an honest baseline; whole baselines definite and different from gold. ✔
- Instantiation-stage gates on the final form: the coordinator re-ran the full block after the rework (EXTENDED / TASK-TOOL-CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all green; `check_traceability` excluded pending the KB). Cited as supplied; not re-run by the auditor. ✔

**Difficulty-level verdict (revision 2).** Task 0: PASS (unchanged, no regression). Task 1: PASS — every round-1 red light is closed on the artifacts by a verbatim-named `overwrite` and a verbatim rule sentence, the merged reading is unique on the task's world, no scored figure moved, and the rework introduced no new defect. Residual observations (F1 residual in the blueprint, F5 dead parameter, F6, F9/F10 on task 0, F11 seed fields) are recorded and are below the red-light bar.
