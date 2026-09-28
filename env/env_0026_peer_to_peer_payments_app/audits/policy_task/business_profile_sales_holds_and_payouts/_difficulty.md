# Policy-task audit — business_profile_sales_holds_and_payouts / charter-global

## charter_global_frozen

- Round: r1 (first audit round). Auditor: independent policy-task auditor (erl-task-policy-audit), not the authoring agent.
- Freeze time: 2026-09-24 23:45 UTC, written before any task's GT was revealed.
- Frozen inputs:
  - `tasks/business_profile_sales_holds_and_payouts/business.extended.yaml` sha256 `d113c23c5495da5789cb323bab9c85324053e577b3336d162188d344871d2bd4`
  - `tasks/business_profile_sales_holds_and_payouts/task_tools.py` sha256 `21725cc71725ee8dba5743d6ee595ce4f6fe4a57003d751d57c5cc9aa01c4337`
  - `blueprint/blueprint.yaml` (difficulty entry lines 46-55), `blueprint/products/business.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`
- Fields I was allowed to read: the four blueprint artifacts, the extended charter, the tool module, and the coordinator's masked views (`task_index`, `frozen_time`, `user_scenario`, `initial_state`).
- Fields masked, and not read before this file was frozen: `tasks/*.json` in full (`evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`), plus `worklog.md`. No recursive search ran over `tasks/` or the scenario root. In the scratchpad I read only the two view files and `snap/d3_r1.txt`.
- Entry conditions (Step 0) came with the brief. All instantiation-stage gates are green in `snap/d3_r1.txt`: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (0.json 11 acts / 1.json 13 acts, match True), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. `check_traceability.py` is deferred until the KB is published. Both view hashes match the brief (`0.view.json` cfb79d00…, `1.view.json` 74fa310a…). Input is complete.
- Base copy check: lines 1-1104 of the extended charter are byte-identical to `blueprint/products/business.yaml`, shown by `diff`. The only difference is one trailing blank line before `extended_policies:`.

### policy_conflict_scan

Five extended policies are in scope:

| policy | trigger | subject | computes | target_tool (owner) |
| --- | --- | --- | --- | --- |
| business_ext_subscription_month_charge | state_due | business_fee (subscription_fee) | fee_amount | book_subscription_fee_2324701e (agent) |
| business_ext_instant_payout_amount | on_request | business_payout (instant_card) | amount | send_instant_payout_0ea58e95 (user) |
| business_ext_chargeback_fee_charge | state_due | business_fee (chargeback_fee) | fee_amount | book_chargeback_fee_9ab6815a (agent) |
| business_ext_refund_fee_credit | state_due | business_fee_credit | credit_amount | credit_refund_fee_b8556c63 (agent) |
| business_ext_bank_payout_amount | on_request | business_payout (standard_bank) | amount | pay_out_to_bank_7d50e7f4 (user) |

- **Overlapping subjects.**
  - Two policies share `business_fee`. They are separated by fee_type: the subscription tool always writes `fee_type=subscription_fee` with a billing_period, and the chargeback tool always writes `fee_type=chargeback_fee` with `source_txn_id`=chargeback.
  - Two policies share `business_payout`. They are separated by payout_method: the instant tool writes `instant_card`, the bank tool writes `standard_bank`.
  - No two policies write the same quantity.
- **Eligibility and state gates.** Both payout policies inherit the base `payout_status` gate (active only), plus min_payout_amount and the instant/daily caps from `business_payouts`. The refund credit is limited to tiers where `fee_refund_pct_portion_on_refund` is true (Growth and above). The subscription charge is limited to tiers where `monthly_subscription_fee` > 0 (Pro and above) and to months the base waiver does not waive. None of these contradict each other.
- **Time anchors.**
  - The charter defines the rolling-month window in one form, repeated verbatim in four rules: "dates after the same calendar day that many months earlier, up to and including the handling date". Profile age in whole months is defined the same way wherever it is used.
  - Handling-date anchoring is uniform. The chargeback-fee windows end on the handling date, not on the chargeback date.
- **Cross-category reads.**
  - Wallet `variant_name` is read by the subscription, chargeback and refund policies.
  - Advance `status` and `outstanding_balance` are read by the instant payout policy.
  - Pay in 4 `status` and `amount_owed` are read by the bank payout policy.
  - Every read is declared in `cross_category`, and all three read tables are in `db_schema.json`.
- **Terminal states.** Each write is one atomic ledger row plus a balance update. No policy moves a status.
- **Task scopes.** From the masked views, and consistent with the declared prerequisite graph:
  - Task 0 = {instant payout (root), subscription month charge}.
  - Task 1 = {bank payout (root), refund fee credit, chargeback fee}.
  - The two scopes are pairwise disjoint, and together they cover all five extended policies.
- **Blueprint claim.** It lists 11 event_types, some of them wider than the five extended policies (for example hold_release, seller_response, clear_review, suspend, close, chargeback_reversal). The claim is a scope reservation. The extended charter instantiates the five above, so the difference is not a conflict.

### rule_compute_equivalence

I swept every compute binding against its `compute_basis` quotation and back against the rule, sentence by sentence.

- **subscription_month_charge.**
  - Every binding maps to a quoted sentence: list_fee, owner_plan/bundle_pct, relief_net_month, relief_recent_chargebacks, relief_quarter_avg (RND to cent), relief_volume (three-way), relief_pct (two thresholds, "at or above" = `>=`), tenure_credit (two thresholds), and result (combined percentage applied once, then credit subtracted, floor 0, round at the end).
  - The rule's first sentence ("in a month the waiver rule does not waive") and the base waiver sentence are gates and are not in compute. That is correct: compute prices the fee, and the waiver decides whether a row exists at all.
  - No empty promise, no invented basis.
- **instant_payout_amount.**
  - All 20 bindings are quoted. The key ones: settling_today (Premier/Enterprise none, else age ≥ 12 → non-in-person, else all); claims_reserve_pct (both → 8, exactly one → 4, else 0; open claims = openings − closings); intl (`>` shares); advance (past_due/suspended → whole, active and > 0 → 25 %, else 0); velocity (≥ 4 / ≥ 2); instant_share (`int(x/2)`, `int(x*0.8)` for x ≥ 0 = rounding down to whole dollars, else whole); result caps.
  - The fee keep-back is P('instant_payout_fee_max'), which matches the rule.
- **chargeback_fee_charge.**
  - cb_sale is the LATEST chargeback's source sale ("most recently debited").
  - fee_level: count == 1 → first-claim fee, ≥ 3 → frequent fee, else the tier fee.
  - reason surcharge.
  - ratio_fee: `>` threshold → ×2, `>` threshold/2 → ×1.5 rounded up by the `-((-x)//1)` idiom, else kept.
  - sized_fee: `<100` → ×0.5 rounded down, `<250` → ×0.75 rounded down, else kept.
  - plan reduction.
  - response_credit: DAYS(opened, response) ≤ seller_response_days.
  - result: floor 0, round.
  - All quoted, both directions.
- **refund_fee_credit.**
  - refund_sale is the LATEST refund's source sale.
  - credited_pct (micropayment first, then channel).
  - pct_part = RND(sale × pct).
  - refund_share: Onyx/Summit = 1; Plus/Prime = ceil to tenths, capped at 1; else exact.
  - pct_credit has no rounding ("times").
  - settled_credit: NAD ×0.5 and INR ×0.75, each rounded down to the cent, both conditioned on a `refund_issued` response on that sale.
  - fixed_fee by channel; fixed_credit_pct (≤ 3 days and no delivery → 100; ≤ 14 days → 60; else 0).
  - result rounded once at the end.
  - All quoted, both directions.
- **bank_payout_amount.**
  - All 23 bindings are quoted: return keep-back (standard_bank returns in 6 months, ≥ 2 → 600, ≥ 1 → 250), refund exposure ("at least" = `>=`), invoice clearing (age < 12 → all, < 24 → half rounded down to whole dollars, else 0), ratio reserve, Pay in 4 keep-back, delivery keep-back (`<` 0.5 / `<` 0.8 of the sale count), cleared, daily room, result.
- **Ladders.** Every tier named in `factors[].ladder` is a sentence of the rule and a branch of its `decides` binding, and every branch of each `decides` binding is a tier the rule states. No tier lives in only one of the two.
- **Result: PASS.** Minor observations are listed under findings (CG-O2, CG-O6).

### action_binding_and_uuids

- **Binding pairs.** Each `(target_tool, computes)` pair belongs to exactly one policy: (book_subscription_fee_2324701e, fee_amount), (send_instant_payout_0ea58e95, amount), (book_chargeback_fee_9ab6815a, fee_amount), (credit_refund_fee_b8556c63, credit_amount), (pay_out_to_bank_7d50e7f4, amount).
- **Tool bodies.** I read all five function bodies in `task_tools.py`. Each one does the same four things and nothing more: build an id with `ctx.make_id`, create one row (two for the instant payout: payout plus its fee row), update `business_balance`, and return a receipt.
  - No body reads another row for eligibility.
  - No body refuses, errors or hints when a prerequisite is unmet.
  - No body adds a confirmation, review or wait.
- **Docstrings.** No docstring names another tool or states a position in a sequence. `credit_refund_fee_b8556c63` does carry the word "after" ("after that sale was refunded"). That refers to the business event being credited, not to any tree edge; see CG-O3.
- **uuid8s.** The five are 2324701e, 0ea58e95, 9ab6815a, b8556c63 and 7d50e7f4. They are pairwise distinct, share no prefix or tail, and show no sequence or adjacency pattern. I found no sign of reuse or batch derivation.
- **Result: PASS.**

### prerequisite_graph

- **`prerequisite` field.** It is filled in on all five policies. It is `[]` on subscription, chargeback and refund-credit.
  - instant → business_ext_subscription_month_charge (value_input, gate `balance`, form state).
  - bank → business_ext_refund_fee_credit (value_input, gate `balance`, form state) and → business_ext_chargeback_fee_charge (value_input, gate `balance`, form state).
- **Targets.** Every `problem` is an extended policy id in this file. None is a base policy and none points to itself.
- **Shape.** The graph is acyclic, with two sinks and three sources.
- **policy_source.** Each edge's `policy_source` appears verbatim in the blocked policy's own `rule`:
  - instant rule, last sentence;
  - bank rule, sentences 13 and 14.
- **form.** Every edge is `state`, and no edge carries a `fallback_reason`, which is consistent.
- **Condition scope.**
  - The instant edge's condition keeps the tier and waiver scope ("On a tier whose monthly_subscription_fee is above 0.00 and in a month not waived") at the same strength as the sentence ("on a tier that charges a monthly subscription and in a month the waiver rule does not waive").
  - The refund edge keeps the tier scope ("fee_refund_pct_portion_on_refund is true" / "a tier that credits part of the transaction fee back on refunds").
  - The chargeback edge is unscoped ("every chargeback"), matching its sentence.
- **resolved_by / effect.** Each `resolved_by` is the depended-on policy's `target_tool`, and its body writes the named row and moves `business_balance`. That is exactly the `balance` binding (`F('business_balance')`) in both root computes, so each `kind: value_input` names a real binding.
- **Wording.** No authoring-viewpoint wording ("in this task", "at the opening") appears in any prerequisite text.
- **Result: PASS.**

### prerequisite_sentences

- **E1: instant ← subscription.** "The instant payout amount is worked out only after the business balance carries the subscription fee entry for the current calendar month, on a tier that charges a monthly subscription and in a month the waiver rule does not waive."
  - Connective: "only after".
  - Waited state: record-visible (a subscription-fee entry for the current month on the balance, in plain words).
  - No tool, policy id, snake_case token or row id. Scope matches the condition.
  - Single write that creates that state: only `business_ext_subscription_month_charge` books a subscription_fee entry. Its own rule says "the month's subscription_fee entry is booked on the first day of the calendar month … at the amount worked out below".
  - Reader derivation: look up the profile tier (Pro and above charge a fee), check the base waiver against last month's volume, look in the ledger for a subscription_fee row with the current billing_period, and if it is missing, book it under the subscription policy. That gives one reading.
- **E2: bank ← refund credit.** "The bank payout amount is fixed only after every refund booked on the profile carries its refund fee credit entry, on a tier that credits part of the transaction fee back on refunds."
  - Connective: "only after".
  - State form, scope "on a tier that credits …", no tokens.
  - Single write: only `business_ext_refund_fee_credit` creates a fee-credit entry against a refunded sale's transaction fee.
  - Reader derivation: list the refunds, look for a business_fee_credit on each refunded sale's transaction_fee row, and if one is missing, credit it under the refund-credit policy. One reading.
- **E3: bank ← chargeback fee.** "The bank payout amount is not fixed until every chargeback debited on the profile carries its chargeback fee entry."
  - Connective: "not until". State form, unscoped, no tokens.
  - Single write: only `business_ext_chargeback_fee_charge` books a chargeback_fee entry.
  - Reader derivation: list the chargebacks, look for a chargeback_fee row whose source is each one, and book any that are missing. One reading.
- **Other checks.**
  - The depended-on rules do not restate any of these sentences.
  - No rule carries a second wording, a tool name or another problem's id.
  - No extended rule states a cross-problem order that does not ground a declared edge.
  - No base rule sentence grounds an edge.
- **Result: PASS.**

### override_declarations

Each extended policy was checked sentence by sentence against its `base_policy_refs`.

- **subscription_month_charge** (refs: subscription_fee, transaction_fees, payouts, buyer_claims).
  - business_subscription_fee s1 is superseded and declared. s2 (waiver) is followed, via "in a month the waiver rule does not waive". s3 (never prorated or refunded) is followed: a percentage relief and a credit are not proration.
  - The other three refs govern no quantity this policy scores, so they are followed by abstention.
  - Outside the policy sentences, `parameter_schema.monthly_subscription_fee` ("Monthly subscription fee for the business tier, USD, charged on the first day of each calendar month.") restates the superseded flat charge. See CG-O1.
- **instant_payout_amount** (ref: payouts).
  - s2's available-balance clause is superseded and declared.
  - The rest of s2 (min_payout_amount, daily limit, instant cap) is inherited and implemented, except that the daily-room quantity departs from `business_msr_payouts_today`. See CG-O2.
  - s1 status, s3 standard/personal free, s4 instant fee formula, s5 auto payout and s6 decline-on-breach are all followed. The capped amount never breaches a limit.
- **chargeback_fee_charge** (refs: buyer_claims, transaction_fees, payouts, subscription_fee).
  - buyer_claims s7's "books a chargeback_fee" clause is superseded and declared. The refunded-if-won clause is inherited.
  - `parameter_schema.chargeback_fee` ("Fee charged on each claim decided for the buyer, USD.") restates the flat fee. The extended rule says in so many words that its amount "takes the place of a flat charge of the tier's chargeback_fee". See CG-O1.
- **refund_fee_credit** (refs: refunds, payouts).
  - business_refunds s5 is superseded and declared. The replacement keeps "the cross_border_fee is never credited back" and drops the fixed-part exclusion, and the extended rule then credits cancel_fixed_pct/return_fixed_pct of the fixed fee.
  - Two base-section sentences not named by the overwrite still state the opposite:
    - `parameter_schema.fee_refund_pct_portion_on_refund`: "Whether the percentage part of the transaction fee is returned in proportion when a sale is refunded (the fixed part is never returned), boolean."
    - `events[business_fee_credit].meaning`: "A fee, or part of it, is credited back — the percentage part of a transaction fee on a refund, …"
  - This is an undeclared override of the fixed-part provision. See CG-F1.
- **bank_payout_amount** (ref: payouts).
  - s2's available-balance clause is superseded and declared. The rest is followed as for the instant payout, with the same daily-room note (CG-O2).
- **Disguised forms.**
  - No 0/1 multiplier zeroes a base-fixed amount.
  - No dropped base branch: the refund credit keeps the "on other tiers no fee is credited back" branch.
  - No author note calls base output a "wrong value".

### factor_ladders

Structure only. Whether each factor bears weight is decided in each task file.

| policy | factor | label | decides | tiers | fall-through = baseline binding | multi-source tier(s) | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- | --- |
| subscription | plan_bundle | parameter | bundle_pct | 3 (30/20/0) | 0 ✓ | no (one wallet field) | wallet |
| subscription | volume_relief | parameter | relief_pct | 3 (30/15/0) | 0 ✓ | volume × tier waiver param | – |
| subscription | tenure_credit | parameter | tenure_credit | 3 (3.0/1.5/0) | 0 ✓ | no | – |
| subscription | relief_window | method | relief_volume | 3 (max / 3-mo avg / month) | relief_net_month (see CG-O4) | yes: profile age ∧ chargeback rows | – |
| instant | settling_sales | method | settling_today | 3 (none / non-in-person / all) | today_sales ✓ | tier ∧ age (same profile row) | – |
| instant | claims_reserve | parameter | claims_reserve_pct | 3 (8/4/0) | 0 ✓ | yes: chargeback rows ∧/⊕ claim rows | – |
| instant | cross_border_keepback | parameter | intl_keep_pct | 3 (4/2/0) | 0 ✓ | intl sales vs all sales | – |
| instant | advance_keepback | parameter | advance_keepback | 3 (whole/25 %/0) | 0 ✓ | status ∧ owed | advance |
| instant | velocity_keepback | parameter | velocity_keepback | 3 (400/150/0) | 0 ✓ | no | – |
| instant | instant_share | method | instant_share | 3 (½ rounded down / ×0.8 rounded down / whole) | MX(0, cleared) ✓ | tier 2: no return ∧ thin payout count | – |
| chargeback | repeat_claims_level | parameter | fee_level | 3 (12 / 35 / tier fee) | P('chargeback_fee') ✓ | no | – |
| chargeback | claim_reason_surcharge | parameter | reason_surcharge | 3 (10/5/0) | 0 ✓ | no | – |
| chargeback | ratio_adjustment | method | ratio_fee | 3 (×2 / ×1.5 rounded up / kept) | fee_level + surcharge ✓ | yes: chargebacks vs sales | – |
| chargeback | claim_size_scaling | method | sized_fee | 3 (×0.5 rounded down / ×0.75 rounded down / kept) | ratio_fee ✓ | no | – |
| chargeback | plan_reduction | parameter | plan_reduction | 3 (5/2.5/0) | 0 ✓ | no | wallet |
| chargeback | seller_response_credit | parameter | response_credit | 3 (8/5/0) | 0 ✓ | yes: response row ∧ date from claim opening | – |
| refund | credited_fee_rate | parameter | credited_pct | 5 (micro / qr / tap / invoice / transaction) | P('transaction_fee_pct') ✓ | amount ∧ channel (same sale row) | – |
| refund | plan_refund_share | method | refund_share | 3 (whole / ceil tenth / exact) | refund/sale ✓ | no | wallet |
| refund | claim_settlement_scaling | method | settled_credit | 3 (×0.5 rounded down / ×0.75 rounded down / kept) | pct_credit ✓ | response row ∧ claim reason | – |
| refund | fixed_fee_return | parameter | fixed_credit_pct | 3 (100/60/0) | 0 ✓ | yes: refund-sale date span ∧ delivery rows | – |
| bank | bank_return_keepback | parameter | return_keepback | 3 (600/250/0) | 0 ✓ | no | – |
| bank | refund_exposure | parameter | refund_keep_pct | 3 (5/2/0) | 0 ✓ | yes: refunds vs sales | – |
| bank | invoice_clearing | method | invoice_clearing | 3 (all / half rounded down / none) | 0 ✓ | no | – |
| bank | ratio_reserve | parameter | ratio_reserve_pct | 3 (8/3/0) | 0 ✓ | yes: chargebacks vs sales | – |
| bank | paylater_keepback | parameter | paylater_keepback | 3 (whole/20 %/0) | 0 ✓ | status ∧ owed | paylater |
| bank | delivery_confirmation_keepback | parameter | delivery_keep_pct | 3 (4/1.5/0) | 0 ✓ | yes: delivery rows vs sale rows | – |

- **Counts per policy.**

  | policy | factors | parameter | method | range 4-6 / ≥ 2 parameter / ≥ 1 method |
  | --- | --- | --- | --- | --- |
  | subscription | 4 | 3 | 1 | ✓ |
  | instant | 6 | 4 | 2 | ✓ |
  | chargeback | 6 | 4 | 2 | ✓ |
  | refund | 4 | 2 | 2 | ✓ |
  | bank | 6 | 5 | 1 | ✓ |

- **Distinct outcomes.** On every tier where the policy applies, no two tiers of one ladder select the same value or method. Checked in particular:
  - credited_fee_rate's five rates on Growth, Pro, Premier and Enterprise;
  - repeat_claims_level's 12 / 35 against every tier's chargeback_fee (10 / 15 / 20).
- **Ladders in the rule.** Every ladder is stated in full in its `rule` (condition and value or method) and implemented in its `decides` binding.
- **Conditions.** No tier condition holds for every customer who reaches the write. Each divides that policy's customers by something a payments operator plausibly weighs: plan bundles, loyalty tenure, dispute exposure, cross-border mix, other-product delinquency, payout velocity, return history, delivery evidence, claim size and reason, refund timing and channel.
- **Fall-through tiers.** The standard values (no discount, no keep-back, tier fee, whole balance) are what such a business publishes as its default.
- **Method labels.** Method tiers are honest where they change the procedure: relief_window chooses among three aggregates, settling_sales chooses which sales count, plan_refund_share changes the share rule. Several other method ladders are "multiply by a number and change the rounding step"; see CG-O5.
- **Multi-source and cross-difficulty coverage per task.**
  - Task 0 (subscription + instant): relief_window, claims_reserve and volume_relief are multi-source; cross-difficulty via wallet (plan_bundle) and advance (advance_keepback).
  - Task 1 (refund + chargeback + bank): fixed_fee_return, seller_response_credit, ratio_adjustment, refund_exposure, ratio_reserve and delivery_confirmation_keepback are multi-source; cross-difficulty via wallet (plan_refund_share, plan_reduction) and paylater (paylater_keepback).
  - The categories read (wallet, advance, paylater) are the products of other difficulties or of the scenario's base account.

### findings

- **CG-F1: SOURCE-POLICY RED (undeclared override). Bears on task 1.**
  - Symptom: two base-section sentences that the overwrite does not name still say the fixed part of the transaction fee is never returned on a refund. The extended rule credits part of it.
  - Root cause: `business_ext_refund_fee_credit.overwrite` names only the business_refunds rule sentence. Two restatements of the same provision elsewhere in the verbatim base section are left standing.
  - Evidence:
    - `business.extended.yaml` line 67: `fee_refund_pct_portion_on_refund: Whether the percentage part of the transaction fee is returned in proportion when a sale is refunded (the fixed part is never returned), boolean.`
    - line 518: `business_fee_credit … meaning: A fee, or part of it, is credited back — the percentage part of a transaction fee on a refund, …`
    - Against these, line 1681: "The fixed-fee credit percentage is cancel_fixed_pct percent when … return_fixed_pct percent when the refund is dated no more than return_days calendar days after the sale … the fixed-fee credit is that percentage of the sale's fixed fee."
    - And line 1682: "The refund fee credit is the claim-settled refund credit plus the fixed-fee credit …"
  - Consequence: in any world where a refund falls within return_days of its sale, the two readings give different credit amounts. The figures are demonstrated against task 1's world in `1.md`.
  - Affected: `business.extended.yaml` parameter_schema line 67, events line 518, extended policy `business_ext_refund_fee_credit.overwrite`.
- **CG-O1: observation.** `parameter_schema.chargeback_fee` (line 72, "Fee charged on each claim decided for the buyer") and `parameter_schema.monthly_subscription_fee` (line 42, "… charged on the first day of each calendar month") are unreplaced restatements of the flat charges that the extended policies supersede. Unlike CG-F1, each extended rule says in its own words that its amount takes the place of the flat charge ("which takes the place of a flat charge of the tier's chargeback_fee"; "at the amount worked out below"). The parameter text also stays literally true as the definition of the tier parameter those rules read. I found no second defensible answer.
- **CG-O2: observation.**
  - The base `business_payouts` s2 caps a payout at daily_payout_limit "together with the day's earlier payouts (business_msr_payouts_today)", and that measure excludes payouts returned by a business_payout_return.
  - Both payout extended rules instead subtract "the payouts already dated on the handling date", with no exclusion for returns. The overwrite does not name this change.
  - Neither task world has a payout dated on its handling date, so there is no consequence.
- **CG-O3: observation.** The `credit_refund_fee_b8556c63` docstring contains an ordering word ("after that sale was refunded"). It points at the business event being credited, not at any edge of a problem tree, and names no other tool. No consequence.
- **CG-O4: observation.** `relief_window` decides `relief_volume`, an input used only inside another factor's tier condition (volume_relief). `baseline.rule` ("list fee … with no percentage off and no credit") says nothing about the relief volume. So the claim that this factor's fall-through ("rolling-month net sales") *is* the baseline cannot be checked against `baseline.rule`: under the baseline the relief volume has no role. The substitution test still moves the score in task 0 (see `0.md`), so I did not strike the factor.
- **CG-O5: observation.** instant_share, ratio_adjustment, claim_size_scaling, claim_settlement_scaling and invoice_clearing are labelled `method`, but their tiers are "multiply by k, then round down/up to whole dollars or cents", with k and the rounding step varying. The rounding step genuinely differs between tiers, so each tier is a different procedure and not merely a different number in one formula. I record these as thin methods, not mislabels. The bank payout's only method factor is invoice_clearing.
- **CG-O6: observation.** The chargeback-fee and bank-payout ratio tiers count chargebacks and sales over "the rolling ratio_window_months months" on the profile. The base measure `business_msr_buyer_won_ratio_90d` counts over 90 days across all of the customer's profiles. These are two separately named quantities, and the extended rules define theirs in full, so the two do not fight over one scored number.

## closing_checklist

Written after both reveals (2026-09-24 23:50 UTC). The difficulty is **not closed**:

- Task 0 carries SOURCE-FACTOR RED T0-F1.
- Task 1 carries SOURCE-POLICY RED T1-F1, the consequence of CG-F1.

Status of the Step 4 items as they stand:

- Per-task files `0.md` and `1.md` correspond one-to-one with `tasks/0.json` and `tasks/1.json`, with this file beside them. This is the first revision.
- Extended policies are fully covered: task 0 {subscription, instant}, task 1 {refund credit, chargeback fee, bank payout}. Scopes are pairwise disjoint and task tools are closed. The uuid8s are independent (see `### action_binding_and_uuids`).
- Trees:
  - task 0 has 1 prerequisite problem and 1 value_input edge;
  - task 1 has 2 prerequisite problems and 2 value_input edges;
  - each has an owner=user root, and the whole-difficulty graph is acyclic.
- Factors: every computation has 4-6 factors with at least 2 parameter and 1 method, a definite baseline different from gold, and every factor bearing weight. The exception is the subscription computation in task 0, where the seeded August fee row equals the scored value (T0-F1).
- Gate re-run on the final form: not performed, because no final form exists yet. The auditor edits no artifact.

## revision_2

### charter_global_frozen (r2)

- Round 2 re-audit by the same independent auditor. Frozen 2026-09-25 00:04 UTC, before any round-2 `tasks/*.json` was opened. The text of revision 1 above is left untouched.
- Inputs:
  - `business.extended.yaml` sha256 `48dd68b7c853f082e15dd828ee6fb302fa7a2b0e067eb56c3b7e4d7f413bcf97` (r1 `d113c23c…`, changed).
  - `task_tools.py` sha256 `aa8b334cf82b1a4274ce7107e3407ab5bcedc29fe0ac89874f7284ecaf8183ba` (r1 `21725cc7…`, changed).
  - Blueprint unchanged: `products/business.yaml` mtime 2026-09-24 20:29 UTC, before round 1. Lines 1-1104 of the charter are still byte-identical to it.
- Because both shared hashes changed, every charter-global section is re-derived in full below rather than carried forward.
- Entry conditions:
  - Gate snapshot `coord/snap/d3_r2.txt` shows every gate green: EXTENDED, TASK TOOL CONTRACT, REPLAY (0.json 11/107, 1.json 13/392), SOLVABILITY, COMPUTE (1.json 3 comps / 16 factors / 308 history rows / 42 branches), GROUNDING, SCOPE. Traceability is deferred.
  - Both r2 view hashes match the brief (c82c0d46…, d726b253…).
- contamination_disclosure: in round 1 I read both task JSONs in full after freezing, so I know the round-1 GT, and it is recorded in my r1 comparison sections. Both worlds changed in the rework (see the task files), so the r1 scored values do not transfer. Every r2 value below is recomputed from the r2 views and the r2 charter. The r2 task JSONs and the worklog stay unread until all r2 derivations are frozen.

### what changed in the charter (located by reading the r2 file end to end against the r1 quotations recorded above)

- **subscription_month_charge:** unchanged (1107-1245).
- **chargeback_fee_charge:** unchanged (now 1469-1657; the offset comes from lines added above it).
- **instant_payout_amount:** one overwrite entry added (lines 1254-1258).
  - Superseded: base `business_payouts` "together with the day's earlier payouts (business_msr_payouts_today) may not exceed daily_payout_limit".
  - Replaced by the extended rule's own cap sentence.
  - Rule, compute and factors are otherwise unchanged.
- **bank_payout_amount:** the same kind of overwrite entry added (lines 1812-1816). Rule, compute and factors are unchanged.
- **refund_fee_credit:** reworked.
  - Overwrite `replaced_by` and rule sentence 1 now read: "… a refund earns a fee credit out of the percentage part of the refunded sale's transaction fee … ; the fixed part of the fee and any cross_border_fee are never credited back …".
  - The fixed-fee sentences are removed, and the `fixed_fee_return` factor is removed with them.
  - A new rule sentence: "The refund timing percentage is late_credit_pct percent when the refund is dated more than late_days calendar days after the sale, mid_credit_pct percent when it is dated more than prompt_days but no more than late_days calendar days after the sale, and full_credit_pct percent when it is dated no more than prompt_days calendar days after the sale."
  - The pct_credit sentence now multiplies by "the refund timing percentage divided by one hundred".
  - The result is now "the claim-settled refund credit, rounded to the nearest cent only at that last step".
  - Params: prompt_days 14, late_days 60, full 100 / mid 60 / late 25.
  - New factor `refund_timing`: parameter, decides refund_timing_pct, ladder 25/60/100, baseline K('full_credit_pct').
- **task_tools.py:**
  - The `credit_refund_fee_b8556c63` docstring opening is now "credits back part of the transaction fee of a refunded sale". The phrase "after that sale was refunded" is gone.
  - All five function bodies are unchanged in substance, checked statement by statement. They still perform no reads other than the profile lookup, and they return no errors or hints.
  - The uuid8s are unchanged.

### policy_conflict_scan (r2)

- Subjects, fee_type/payout_method separation, gates, time anchors, cross-category reads (wallet, advance, paylater), terminal states and task scopes are as in revision 1.
- The new timing tier reads only the refund date and the sale date, which are the same anchors the base refund window uses (`refund_window_days` 180). Its late tier (> 60 days) lies inside that window, so there is no conflict.
- The instant and bank policies each supersede the same base daily-limit clause, each only "for that payout" (instant_card or standard_bank respectively). The base clause keeps governing personal_balance payouts. The merged semantics are unique.
- Result: PASS.

### rule_compute_equivalence (r2)

- **Refund.** Every new binding has a verbatim `compute_basis` quotation:
  - `refund_timing_pct`: the new timing sentence, with `>` late_days, `>` prompt_days, else full;
  - `pct_credit`: "times the refund timing percentage divided by one hundred";
  - `result`: "the claim-settled refund credit, rounded to the nearest cent only at that last step".
- The compute_basis entries for `refund_date` and `sale_date` now quote the timing sentence.
- The removed fixed-fee bindings (`fixed_fee`, `sale_deliveries`, `fixed_credit_pct`) have no remaining rule sentence and no remaining compute. The rule makes no empty promise: "the fixed part of the fee … never credited back" corresponds to the absence of any fixed-fee term.
- Other policies: unchanged, so the result stands as in revision 1.
- Result: PASS.

### action_binding_and_uuids (r2)

- Binding pairs and uuid8s are unchanged.
- Docstrings: none names another tool. The remaining words "before booking", "after the payout/charge/fee/credit" and "once recorded" describe the call's own rounding and receipt, not a position in any sequence. They were present in r1 too.
- Result: PASS.

### prerequisite_graph and prerequisite_sentences (r2)

- The `prerequisite` fields, edges E1-E3, their `policy_source` sentences, forms, conditions, `resolved_by` and kinds are unchanged, and each sentence is still verbatim in its blocked rule.
- The refund-credit rework does not touch E2's waited-on state ("every refund … carries its refund fee credit entry"). The only write of that state is still `credit_refund_fee_b8556c63`.
- The DAG, the four-point tests and the single-reading derivations all stand as in revision 1.
- Result: PASS.

### override_declarations (r2)

- **Refund.** The overwrite's `replaced_by` and the rule now keep the base exclusion of the fixed part and the cross-border fee.
  - `parameter_schema.fee_refund_pct_portion_on_refund` ("(the fixed part is never returned)") and `events.business_fee_credit.meaning` ("the percentage part of a transaction fee on a refund") now agree with the extended rule.
  - So the conflict behind **CG-F1 is gone**. No base sentence and no base-section restatement contradicts a quantity the refund credit computes, as far as the fixed part is concerned.
  - Remaining wording: the same parameter description says the percentage part "is returned in proportion". The extended rule departs from exact proportion through the plan share rounding, the timing percentage and the claim scaling. This is the CG-O1 class, and it was already present in r1 without being noted there. See CG-O7.
- **Instant and bank.** The daily-limit departure from `business_msr_payouts_today` is now declared by name in each policy's `overwrite`. **CG-O2 is closed.**
- **Subscription and chargeback:** unchanged. CG-O1 stands as an observation.

### factor_ladders (r2)

The refund row set in revision 1 is replaced by:

| factor | label | decides | tiers | fall-through = baseline binding | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| credited_fee_rate | parameter | credited_pct | 5 | P('transaction_fee_pct') ✓ | amount ∧ channel (same row) | – |
| plan_refund_share | method | refund_share | 3 | refund/sale ✓ | no | wallet |
| claim_settlement_scaling | method (thin, CG-O5) | settled_credit | 3 | pct_credit ✓ | response row ∧ claim-opening reason (distinct business_claims rows) | – |
| refund_timing | parameter | refund_timing_pct | 3 (25/60/100) | K('full_credit_pct') ✓: the baseline rule applies the whole percentage part times the exact share, i.e. 100 % | no (one date span over two rows) | – |

- Refund computation: 4 factors (2 parameter, 2 method), within bounds.
- The timing ladder is distinct (25/60/100) and stated in full in the rule. Scaling back a fee credit for late refunds is a treatment a payments operator plausibly publishes, and its fall-through (the whole credit for a prompt refund) is the default.
- Task-level multi-source coverage for task 1 now comes from the chargeback and bank computations (ratio_adjustment, seller_response_credit, refund_exposure, ratio_reserve, delivery_confirmation_keepback), plus claim_settlement_scaling. Cross-difficulty coverage is wallet and paylater, as before.
- All other policies are unchanged; revision 1's table and counts stand.

### findings (r2, charter-global)

- **CG-F1: closed.** The extended refund rule no longer credits any part of the fixed fee. The base-section texts that r1 cited (line 67 "(the fixed part is never returned)"; line 518 "the percentage part of a transaction fee on a refund") now agree with it. There is no remaining second reading of the fixed part.
- **CG-O2: closed.** The daily-limit clause is now named in both payout overwrites.
- **CG-O3: closed.** The docstring no longer carries the ordering word.
- **CG-O1, CG-O4, CG-O5, CG-O6:** unchanged artifacts, so the observations stand as recorded in r1. That matches the reworker's "recorded without artifact change".
- **CG-O7 (new, observation, pre-existing since r1).**
  - `parameter_schema.fee_refund_pct_portion_on_refund` says the percentage part "is returned in proportion when a sale is refunded". The extended refund rule departs from exact proportion (Plus/Prime share rounded up to a tenth, Onyx/Summit whole, the timing percentage, the claim multipliers).
  - As with CG-O1, the extended rule and its declared overwrite say in their own words that the credit is "at the amount worked out below". The parameter text reads as the definition of the tier switch and not as a competing amount.
  - No second defensible scored value is shown, so this stays an observation. It was missed in r1; it is not a regression.
- **New defects introduced by the rework:** none found at the charter level.

### closing_checklist (r2)

Written after both r2 reveals (2026-09-25 00:05 UTC). All four relationships PASS for both tasks.

- **Files.** `0.md` and `1.md` correspond one-to-one with `tasks/0.json` and `tasks/1.json`, with this file beside them. Revision 1 is kept intact above `## revision_2` in each file, and every r2 comparison section carries PASS.
- **Scopes.** Coverage of the five extended policies is complete:
  - task 0 = {subscription, instant};
  - task 1 = {refund credit, chargeback fee, bank payout}.
  - The scopes are pairwise disjoint.
- **Tools and uuid8s.** Task tools and GT are closed. The uuid8s are independent and frozen: 2324701e, 0ea58e95, 9ab6815a, b8556c63 and 7d50e7f4, unchanged.
- **Trees.**
  - Task 0: 1 prerequisite problem, 1 value_input edge.
  - Task 1: 2 prerequisite problems, 2 value_input edges.
  - Each tree has an owner=user root, and the difficulty-wide graph is acyclic.
- **Factors.** Every computation declares a self-sufficient baseline giving a definite number different from gold:

  | computation | baseline | gold |
  | --- | --- | --- |
  | subscription | 19.99 | 9.99 |
  | instant | 3,933.02 | 1,356.00 |
  | chargeback | 20.00 | 11.50 |
  | refund | 7.32 | 3.31 |
  | bank | 4,891.54 | 2,097.34 |

  - Each computation has 4-6 factors, with at least 2 parameter and 1 method. Each task has multi-source and cross-difficulty factors.
  - Every ladder has at least three distinct tiers stated in full in its rule.
  - Every factor bears weight on its task's world against an honest baseline.
- **Round-1 RED items: closed.**
  - CG-F1 / T1-F1 (fixed-part undeclared override).
  - T0-F1 (stamp agreeing with the scored value).
- **Round-1 observations.**
  - Closed: CG-O2, CG-O3, T1-O2.
  - Standing without artifact change: CG-O1, CG-O4, CG-O5, CG-O6, T1-O1 and the seed-history note.
  - New, pre-existing, not a regression: CG-O7.
- **Regressions:** none found.
- **Gate re-run on the final form:** the coordinator's `coord/snap/d3_r2.txt` covers the reworked artifacts, and all instantiation-stage gates are green. `check_traceability.py` is still deferred until the KB is published.
- **The difficulty passes the source-layer policy-task audit.**
