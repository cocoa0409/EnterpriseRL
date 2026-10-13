# Policy-task audit — consumer_credit_servicing / charter-global

## charter_global_frozen
- Freeze time: 2026-10-08T07:15:38Z. Auditor: independent erl-task-policy-audit agent (round 1; resumed after an account cut-off, no earlier report existed on disk).
- Frozen inputs (sha256, re-verified on read):
  - `tasks/consumer_credit_servicing/card.extended.yaml` af1fbccd3a7611616943f37e9a3d5ece4eef1b05e6492582644d31fa36eff7f0
  - `tasks/consumer_credit_servicing/task_tools.py` 82a16bf99e9f2f44869d6ef8ec144414679d39ba1bf133339845d6985f182e76
  - blueprint: `blueprint.yaml`, `db_schema.json`, `share_tools.py`, `products/card.yaml` (plus `products/special.yaml` for the semantics of the special-order ledger the charter reads)
- Fields used: the charter (base + `extended_policies`), the tool contracts and bodies, the share-tool contracts, and the DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (`MONTHS`, `DAYS`, `_within`, `LATEST`, `CFIELD`, `X*`).
- Masked and unread while writing this section: all of `tasks/*.json` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure). Nothing here comes from a revealed GT.
- Entry conditions: the gate snapshot came with the brief (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK, CACHE-DIFF INFO; TRACEABILITY NOT OK, which the coordinator says is expected because the KB is not yet rendered). The masked views came with their hashes and both matched (`task_0.blind.json` 773ef8ed…, `task_1.blind.json` 3ab7c35e…). Each view holds only frozen_time, user_scenario and initial_state.

### policy_conflict_scan
- Base copy: lines 1–1438 of the extended file match `blueprint/products/card.yaml` byte for byte. The only difference is one trailing blank line, and the YAML loads equal.
- There are four extended policies, each with its own subject and target tool:
  - `card_ext_refund_credit`: subject card_return_credit_posted, state_due, tool `post_refund_return_credit_59e816eb` (agent).
  - `card_ext_promo_autopay`: subject card_autopay_changed, on_request, tool `set_autopay_payoff_plan_7f80aff1` (user).
  - `card_ext_late_fee`: subject card_fee_assessed, state_due, tool `post_missed_payment_late_fee_0b17ca39` (agent).
  - `card_ext_good_standing_payment`: subject card_payment_posted, on_request, tool `authorize_phone_payment_1fdda3b1` (user).
- Overlapping subjects: card_fee_assessed is also the subject of base card_evt_payment_posting (phone payment fee) and card_evt_returned_payment (returned payment fee). card_ext_late_fee concerns fee_type late_fee only, so the two do not compete for the same quantity. card_payment_posted also appears in the base posting and allocation policies, and the extended rule inherits both. Details are under override_declarations.
- Triggers and time anchors:
  - The late fee "posts on the day after the due date" (extended), matching the base wording.
  - The refund credit runs on a 3-month window. The good-standing payment uses a "last month" window. Both use the `_within` convention 0 ≤ MONTHS(d, today) < N, which is the rule's wording "dated less than N full months before today".
  - Plan due dates are counted from the first due date after today.
  - No two extended policies anchor the same quantity on different clocks.
- Cross-category reads:
  - refund_credit reads special (special_order_events refunds and credits).
  - promo_autopay reads special (special_orders balance_due by status).
  - late_fee reads install (install_charges payments).
  - good_standing reads no other category.
  - Each read is declared in `cross_category`, and the blueprint grants this difficulty only the card category for writes.
- Scope:
  - The prerequisite graph has exactly two components: {card_ext_promo_autopay ← card_ext_refund_credit} and {card_ext_good_standing_payment ← card_ext_late_fee}. With M=2, each task's tree must be one component.
  - The two trees are disjoint and jointly cover all four extended policies. Which task claims which tree is confirmed per task from its user_scenario (task 0 asks for an autopay payoff plan; task 1 asks for a good-standing payment).
  - Every extended subject (card_return_credit_posted, card_autopay_changed, card_fee_assessed, card_payment_posted) is among the event types the blueprint claims for this difficulty.

### rule_compute_equivalence
Every compute binding of all four policies was checked against its `compute_basis` quotation and its rule sentence, in both directions.

- **card_ext_refund_credit**: equivalent on every binding.
  - prog_refunds: XSUM over special refunds, refund_method ridgeline_consumer_credit, 3 months. Matches "total of the special order refunds issued to the Ridgeline Consumer Credit tender … in the last 3 months".
  - posted_credits: return credits in 3 months. Matches.
  - uncredited: floored at 0. Matches.
  - refund_date: XLATEST, unwindowed. The rule says "latest of those refund dates", meaning the windowed set. Whenever the window is non-empty, the unwindowed latest equals the windowed latest. When the window is empty, uncredited is 0 and nothing posts. So the two are equivalent.
  - allowance_rate: three tiers, verbatim.
  - delay_credit_date, cancel_credit_date, clock_start: the latest credit of each type is tested against the refund date, as the rule's "the latest … credit … is dated on or before the latest refund date" reads.
  - days_late, flat_courtesy (30 / 14 day boundaries), so_spend (purchase_channel special_order, 12 months), allowance_multiplier, interest_allowance, allowance, result: all verbatim.
- **card_ext_promo_autopay**: equivalent on the task worlds, with two latent gaps (observations O-1 and O-2 below).
  - Equivalent: promo_posted, promo_credits, promo_payments (full amount), promo_balance, end6/12/24, plan_end, latest_due, drafts, margin, addon (> 0 vs ≥ 500 tiers), cushion, whole_dollar_draft (ceiling), result.
  - due_dates_total = MONTHS(latest_due, plan_end) + 1 − (1 if the latest due date is not after today). This equals the rule's count only while the latest statement's due date is no more than one month before today. That holds whenever statements are monthly, and it holds on both task worlds.
  - O-1: `open_order_due` uses `CFIELD('special','balance_due', status=…)`, which returns the first matching order's field only. The rule says "the balance due on the customer's special orders that are in production, shipped or ready totals". With two orders in one status, compute would count one of them.
- **card_ext_late_fee**: equivalent on every binding.
  - fee_level: three tiers verbatim. The returned_6 test is repeated in tier 2, which is redundant but harmless.
  - Also verbatim: balance_add, autopay_6, lapse_fee (int() = round down for positive sums; fall-through unrounded, as the rule's "taken as it stands"), project_payments (XCOUNT install_payment_received, payment_method ridgeline_consumer_credit, 12 months by charge_date), project_relief, min_due cap gated on P('late_fee_capped_at_min_due'), MX(0, …).
  - The rule's first sentence (when a fee is owed) is eligibility, not compute. That is correct.
- **card_ext_good_standing_payment**: equivalent on the task worlds, with one latent gap (observation O-3 below).
  - Equivalent: stmt_* (latest statement), open_disputed (billing_dispute, status submitted), recent_credits (1 month), owed_minimum formula, paid_since, unpaid_min, period_late_fee, utilization and bridge_rate (25/50 % thresholds), last_payment_date / payment_gap / bridge_days (> 30 → statement date; 15–30 → payment date; else due date), returned_24 / cushion, result.
  - O-3: the rule says "The owed minimum **on a revolving card** is recomputed when a billing dispute … is still open". The compute binding `owed_minimum` never tests that the account is a revolving card. On a Project Loan with an open dispute it would apply the revolving formula with floor 0 and percentage 0, giving past-due only, while the rule gives that statement's printed minimum.
- No compute binding invents a basis absent from its rule, and no rule sentence lacks a compute binding. Every `factors[].ladder` tier is a rule sentence and a branch of its `decides` binding, and vice versa. The only exception is the O-3 condition fragment.

### action_binding_and_uuids
- (target_tool, computes) pairs are all distinct: (post_refund_return_credit_59e816eb, amount), (set_autopay_payoff_plan_7f80aff1, autopay_fixed_amount), (post_missed_payment_late_fee_0b17ca39, amount), (authorize_phone_payment_1fdda3b1, amount). No base policy claims a tool of this module.
- Docstrings: a word-boundary search for before, after, first, then, until and prior over `task_tools.py` returns nothing. No docstring names another tool or states a sequence position.
- Function bodies:
  - All four tools check nothing about eligibility or prerequisites.
  - The two agent tools find the account by id and write.
  - The two user tools look up `account_last4` and return `not_found` only for unknown digits.
  - None refuses, errors or hints when a prerequisite is unresolved.
- uuid8s: 59e816eb, 7f80aff1, 0b17ca39, 1fdda3b1. They are pairwise distinct, share no prefix or suffix, and show no sequence. Nothing suggests batch derivation.
- Observation O-4: `authorize_phone_payment_1fdda3b1` posts no phone-payment-fee row. Base card_evt_payment_posting requires a fee row of phone_agent_payment_fee_usd on tiers where it is nonzero (Classic and Preferred, 9.95), and no tool of this difficulty posts one. This has no consequence on a Premier account (fee 0.00).

### prerequisite_graph
- `prerequisite` is filled on all four policies: refund_credit [], late_fee [], promo_autopay one edge, good_standing one edge.
- Edge E1: card_ext_promo_autopay → card_ext_refund_credit.
  - kind value_input, gate `promo_credits` (an existing compute binding), form state, no fallback_reason (correct for state form).
  - policy_source: "The plan's fixed draft amount is not worked out until every refund a Ridgeline selling program has issued to the account stands on the account as a return credit." It appears verbatim at rule sentence 2 (yaml line 1619).
  - resolved_by `post_refund_return_credit_59e816eb` = refund_credit's target_tool.
  - effect: the credit carries the deferred plan code, so promo_credits rises. True of the tool body: it writes the plan_code it is given.
- Edge E2: card_ext_good_standing_payment → card_ext_late_fee.
  - kind value_input, gate `period_late_fee` (an existing binding), form state.
  - policy_source: "The good-standing amount is fixed only after the late fee owed for the missed due date stands on the account." It appears verbatim at rule sentence 2 (yaml line 1939).
  - resolved_by `post_missed_payment_late_fee_0b17ca39` = late_fee's target_tool.
  - effect: the fee line is dated today, so the last-month late fees rise. True: the tool writes transaction_date = today.
- Both `problem` fields point at extended ids in this file, never at a base policy or at the policy itself. The graph is acyclic: two disjoint edges, and both leaves have empty prerequisites. No authoring-viewpoint phrasing ("in this task", "at the opening") appears in any prerequisite field.
- Condition strength:
  - E2: the condition ("carries a late fee line for the statement period whose due date passed with its minimum unpaid") is the state the sentence names.
  - E1: the condition is narrower than the sentence. See O-5 under prerequisite_sentences.

### prerequisite_sentences
- **Four-point test, E1:**
  - (a) "not … until" joins the policy's own result ("the plan's fixed draft amount") to what it waits on.
  - (b) What it waits on is a record-visible state ("every refund … stands on the account as a return credit") with no tool or performer.
  - (c) No tool name, policy id, snake_case token or row id.
  - (d) Strength: see O-5.
- **Four-point test, E2:**
  - (a) "only after".
  - (b) "the late fee owed for the missed due date stands on the account" is a state.
  - (c) Clean.
  - (d) The scope matches the condition.
- **One write per state:**
  - E1: only `post_refund_return_credit_59e816eb` creates card_return_credit_posted rows in this difficulty. No base tool exists here, and the share tools are reads plus verify/transfer.
  - E2: only `post_missed_payment_late_fee_0b17ca39` creates late-fee rows.
- **Derivations:**
  - E1: the reader sees the sentence, then the records (a special_refund_issued line with refund_method ridgeline_consumer_credit and no card_return_credit_posted on the card). card_ext_refund_credit's own rule ("When a Ridgeline selling program has issued a refund … and the account does not yet carry it, one return credit is posted for it") then gives the resolving write. This is a single reading.
  - E2: the reader sees the sentence, then the records (the latest statement's due date passed with payments short of its minimum and no late_fee line for that period). card_ext_late_fee's rule ("When the payments credited from a statement's date through its due date total less than that statement's minimum payment due, one late fee is owed …") then gives the write. This is a single reading.
- Neither depended-on rule restates the blocked sentence. Neither blocked rule carries a second wording, a tool name or another problem's id. No other extended rule states a cross-problem order that grounds no declared edge.
- Base rule sentences that state cross-problem orders (card_evt_billing_dispute "fees caused solely by the disputed amount are reversed separately under card_evt_fee_correction"; card_evt_courtesy_waiver "the correction applies instead") ground no edge of either tree. They are noted only.
- **O-5 (observation):** E1's sentence is broader than its condition.
  - The sentence covers "every refund a Ridgeline selling program has issued to the account", with no program restriction and no window.
  - The `condition` and the refund-credit compute cover only special-order refunds to the RCC tender dated in the last 3 months.
  - On a world with an installation, rental or order refund to the card, or a special refund older than 3 months that was never credited, the sentence would say "not yet", while card_ext_refund_credit's amount formula (uncredited = special refunds in 3 months − credits) would give 0.
  - Neither task world carries such a refund. Task 0's only other refund went to a bank card. So this is not demonstrable on a task.

### override_declarations
- **card_ext_refund_credit vs card_evt_return_credit:**
  - The amount sentence ("The credit amount is the refund decided under the selling program's own rules") is declared superseded.
  - Followed, sentence by sentence: same account; reference the original purchase, plan_code and merchant_reference; credits per purchase never above the purchase amount (inherited, and not exceeded on the task world); accepted statuses; promotional credit reduces the promo balance; Project Loan draw restoration (not in play); credit-balance refund (not in play).
  - Not an override but worth noting: the uncredited refund subtracts *all* return credits of the last 3 months, including merchandise returns unrelated to any program refund. No consequence on the task worlds.
- **card_ext_promo_autopay vs card_autopay_management / card_evt_promo_financing / card_evt_payment_allocation** (overwrite: []):
  - Autopay management: the fixed-amount draft as the greater of the fixed amount and the minimum is restated. The status and option set are inherited.
  - O-6: the rule's due-date count does not apply the base sentence "A change made at least autopay_change_lead_days business days before the next payment due date applies to that due date, and a later change applies from the following due date". The plan counts the first due date after today even when it is within 3 business days. This is latent: on task 0 the next due date is 2026-11-09.
  - Allocation: the base says the part up to the minimum is "applied at the bank's discretion" and only the excess follows excess_allocation. The extended rule counts each promo-allocated payment "at its full amount". The base leaves the minimum part undetermined rather than fixing a contrary value, so this is a resolution, not an undeclared override. It is recorded as O-7 because the rendered base sentence invites a reader to subtract only the excess. The per-task file shows the number that reading would give.
- **card_ext_late_fee vs card_evt_late_fee / card_evt_payment_posting / card_evt_returned_payment:**
  - The fee-amount sentence (first/repeat by lookback, cap) is declared superseded by the extended algorithm.
  - Inherited and followed: posting the day after the due date; reference to the statement row and period; no fee when the minimum is 0.00; a returned payment does not count as credited; one fee per period; the single-event rule.
  - The superseded base measure excluded late fees reversed as posting_error. The extended "a late fee was charged" counts are not restricted that way. Latent; neither world has a reversal.
- **card_ext_good_standing_payment vs card_evt_payment_posting / card_evt_payment_allocation / card_evt_statement_minimum / card_evt_billing_dispute** (overwrite: []):
  - The base allocation sentence fixes excess_allocation (a parameter of the user tool, not computed by the extended rule). The dispute exclusion from the minimum agrees with the base statement-minimum rule ("Any amount under an open billing dispute is left out of the balance used for the minimum").
  - The base posting rules are inherited: cutoff, debit authorization, payment ≤ current_balance, and the phone fee (O-4).
  - No conflict is found that bears on the scored quantity.

### factor_ladders
Every policy declares 4 factors. Every ladder has 3 tiers including the fall-through, pairwise disjoint as stated. The `decides` targets are inputs (not `result`), the binding sets are disjoint within each policy, and every tier is stated in the rule and implemented in compute.

| policy | factor | label | honest label? | multi-source | cross-difficulty |
|---|---|---|---|---|---|
| refund_credit | allowance_rate | parameter | yes (APR / 12 / 6) | no (variant + tenure, one account row) | — |
| refund_credit | late_posting_clock | method | yes (anchor date: the count reads a different record) | yes (credit date vs refund date, distinct ledger rows) | special |
| refund_credit | flat_courtesy | parameter | yes | no | — |
| refund_credit | allowance_multiplier | **method** | **no**: tiers 2 / 1.5 / 1 are constants in one unchanged expression `(interest_allowance + flat_courtesy) * allowance_multiplier` | no | — |
| promo_autopay | plan_horizon | **method** | **no**: tiers are MX(1, n−2) / MX(1, n−1) / MX(1, n), one formula with the constant 2 / 1 / 0 | tier 1 single-source | — |
| promo_autopay | plan_margin | parameter | yes | no | — |
| promo_autopay | spending_addon | parameter | yes | no | — |
| promo_autopay | open_order_cushion | parameter | yes | no | special |
| late_fee | fee_level | parameter | yes | yes (late fee OR returned; no late fee AND no returned AND tenure) | — |
| late_fee | balance_addon | parameter | yes | no | — |
| late_fee | lapse_treatment | method | borderline yes: tiers 1–2 are floor(x·c) with c = 0.5 / 0.75 and the fall-through is unrounded x, so the rounding treatment changes (O-8) | no | — |
| late_fee | project_relief | parameter | yes | no | install |
| good_standing | owed_minimum_basis | method | yes (recompute on a reduced balance vs printed minimum) | yes | — |
| good_standing | bridge_rate | parameter | yes | no (one ratio) | — |
| good_standing | bridge_days | method | yes (anchor date) | yes (payment row vs statement row) | — |
| good_standing | representment_cushion | parameter | yes | no | — |

- **Counts after the honesty test:**
  - refund_credit: 3 parameter, 1 method. Bounds hold once the multiplier is relabelled, but the label itself is dishonest (F-1).
  - promo_autopay: 4 parameter, **0 method**. It fails the ≥ 1 `method` bound (F-2).
  - late_fee: 3 parameter, 1 method (borderline).
  - good_standing: 2 parameter, 2 method.
  - Per tree: tree {refund, promo} has a multi-source factor (late_posting_clock) and cross-difficulty factors (late_posting_clock and open_order_cushion, both reading special). Tree {late_fee, good_standing} has multi-source factors (fee_level, owed_minimum_basis, bridge_days) and a cross-difficulty factor (project_relief, reading install).
- **Distinct outcomes:**
  - fee_level: tier 1 (P late_fee_repeat_usd) and the fall-through (P late_fee_first_usd) select the same value, 39.00, on every Project Loan tier. That is latent (O-9): both task accounts are revolving (Preferred, Premier), where the values are 43 / 25 / 32.
  - All other ladders are distinct on every tier.
- **Baselines:**
  - Every factor's `baseline` equals its fall-through tier and is what `baseline.rule` states. Examples: refund rate 6 % and days from the refund date with no courtesy or multiplier; promo 5 %, all due dates, no add-on or cushion; late fee first fee capped; good standing printed minimum, APR, days from the due date, no cushion.
  - Every `baseline.rule` sentence is a rule sentence, and each is self-sufficient for a definite number.
- **Realism:**
  - **F-3:** late_posting_clock's non-fall-through tiers start the clock from "the latest vendor-delay credit / order-cancellation credit applied to **one of the customer's special orders**". The condition is not tied to the special order whose refund is being credited. A card servicer settling a late-posting allowance on refund R does not weigh a cancellation credit on an unrelated order, whose own refund may have gone to another tender. The per-task demonstration is in 0.md.
  - The other conditions are ones the line of business plausibly weighs: tenure and tier for goodwill rates and margins; days late; spend loyalty; recent returns and late fees for plan risk; open orders; balance; autopay history; utilization; payment timing; prior returns.
  - O-10: a utilization-tiered "interest bridge" rate and a re-presentment cushion that grows with prior returns are unusual, but they are not shown to be treatments no issuer would publish.

### findings
- **F-1 SOURCE-FACTOR (mislabelled effect), bears on task 0.** card_ext_refund_credit factor `allowance_multiplier` is labelled `method`. Its ladder values are `K('mult_high')` = 2, `K('mult_mid')` = 1.5 and `1`, substituted into the unchanged binding `allowance: "RND((interest_allowance + flat_courtesy) * allowance_multiplier, 2)"`. The tiers change a number, not the algorithm. Affected: card.extended.yaml, card_ext_refund_credit.factors[3].effect (yaml lines 1565–1579).
- **F-2 SOURCE-FACTOR (mislabelled effect, so the method bound fails), bears on task 0.** card_ext_promo_autopay factor `plan_horizon` is labelled `method`. Its tiers are `MX(1, due_dates_total - K('early_returned'))` (2), `MX(1, due_dates_total - K('early_late'))` (1) and `MX(1, due_dates_total)` (0): one formula with a substituted constant. With no other `method` factor in the policy, the computation has 0 honest `method` factors against a floor of 1. Affected: yaml lines 1691–1705 and compute `drafts` (line 1659).
- **F-3 SOURCE-FACTOR (unreal ladder condition), bears on task 0.** card_ext_refund_credit factor `late_posting_clock`, rule sentence: "when the latest vendor-delay credit applied to one of the customer's special orders is dated on or before the latest refund date, the clock starts on that delay-credit date; when that does not hold but the latest order-cancellation credit applied to one of the customer's special orders is dated on or before the latest refund date, the clock starts on that cancellation-credit date". The tier conditions range over every special order of the customer, not the refunded one. Affected: rule sentence 7 (yaml line 1476), compute delay_credit_date / cancel_credit_date (lines 1492–1493; XLATEST is unscoped by order).
- Observations O-1 to O-10, recorded above. None is demonstrable as a consequence on either task's world (each task file shows its own non-impact):
  - O-1: CFIELD reads the first order only.
  - O-2: the due-date count assumes monthly statements.
  - O-3: the revolving-card condition is absent from compute.
  - O-4: no phone-fee write exists.
  - O-5: the E1 sentence is broader than its condition.
  - O-6: autopay lead days are not applied to the plan's first due date.
  - O-7: promo payments are counted at full amount.
  - O-8: lapse_treatment is a borderline method.
  - O-9: fee_level tiers coincide on Project Loans.
  - O-10: unusual but not demonstrably unreal ladders.

## closing_checklist
Written 2026-10-08T07:22:36Z, after both reveals. The section above was frozen pre-reveal (sha256 5a0442a6…) and is unchanged.

- **Per-task files:** 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json, alongside this file. This is round 1, so there are no older revisions. Each file carries a frozen blind derivation, then source_gt_comparison.
  - **Task 0: SOURCE-FACTOR RED** (F-2; also F-1 and F-3). Policy, tree and unique solution PASS.
  - **Task 1: PASS** on all four relationships.
- **Coverage and scope:**
  - charter_scope: task 0 = {card_ext_refund_credit, card_ext_promo_autopay}, task 1 = {card_ext_late_fee, card_ext_good_standing_payment}.
  - Pairwise disjoint and jointly complete over the 4 extended policies and 4 task tools.
  - uuid8s are independent and frozen (§ action_binding_and_uuids).
- **Trees:** each has 1 prerequisite problem and 1 value_input edge, each root is an owner=user write, there is no cycle, and the difficulty-wide graph is a DAG of two disjoint edges.
- **Factors:**
  - Every computation declares 4 factors and a self-sufficient baseline (fall-backs 364.07, 1670.00, 32.00 and 155.38, each ≠ gold). Every factor bears weight on its task's world.
  - **Not met:** card_ext_promo_autopay has 0 honest `method` factors (F-2). allowance_multiplier is mislabelled (F-1). late_posting_clock's tier conditions are unscoped to the refunded order (F-3).
- **Gates:**
  - The auditor did not re-run the instantiation gates (the coordinator supplies them).
  - Artifact hashes are unchanged since the gate snapshot and through this audit: card.extended.yaml af1fbccd…, task_tools.py 82a16bf9…, tasks/0.json af5edf87…, tasks/1.json 4f1cdbdb….
  - TRACEABILITY remains NOT OK pending the KB render, per the brief.
- **Result:** the difficulty **does not pass** the source-layer audit while task 0 is SOURCE-FACTOR RED.

## revision_2

### charter_global_frozen (revision_2)
- Freeze time: 2026-10-08T09:02:25Z. Written before any round-2 `tasks/*.json` was opened. Auditor: same independent auditor, round 2.
- Inputs:
  - card.extended.yaml sha256 79842f447fcbc128f7a2b6d7ea936991d64499c0bdb2da63a9697b1fb94ffd31 (changed from af1fbccd…), so every charter-global section is **re-derived** here, not carried forward.
  - task_tools.py 82a16bf9… (unchanged), so § action_binding_and_uuids is carried forward by reference on that hash.
  - Base copy: lines 1–1438 still match `blueprint/products/card.yaml` (re-diffed; only the trailing blank line differs).
  - Masked views r2: task_0 773ef8ed…, task_1 3ab7c35e…, identical to round 1 and re-verified.
- Gate snapshot cited from the brief: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE OK; CACHE-DIFF INFO; TRACEABILITY NOT OK (pending KB).
- The round-1 text above is left untouched.

### what changed in the charter (auditor's own reading of all four extended policies, yaml lines 1441–2076)
- **card_ext_refund_credit:**
  - allowance_multiplier is relabelled `effect: parameter`, with values K('mult_high') / K('mult_mid') / 1.
  - late_posting_clock is rewritten. Rule sentence 7 now reads: "when the refunds to the Ridgeline Consumer Credit tender in the 3 months are the payout of vendor-delay credits, that is, the vendor-delay credits the special order program applied in the same 3 months total exactly the same amount as those refunds, the clock starts on the latest of those delay-credit dates; when that does not hold but the order-cancellation credits applied in the same 3 months total exactly the same amount as those refunds, the clock starts on the latest of those cancellation-credit dates; otherwise the clock starts on the latest refund date."
  - New bindings delay_credits / cancel_credits (XSUM over 3 months). clock_start tests `RND(credits − prog_refunds, 2) == 0`.
- **card_ext_promo_autopay:**
  - The prerequisite sentence (rule sentence 2) and policy_source now read: "The plan's fixed draft amount is not worked out until every special order refund issued to the Ridgeline Consumer Credit tender in the customer's name in the last 3 months stands on the account as a return credit."
  - plan_horizon tiers are now: due dates halved and rounded **up**; due dates × 0.75 rounded **down**; all due dates (never fewer than 1). Params early_returned/early_late are replaced by half/three_quarter.
- **card_ext_late_fee:** lapse_treatment tier 2 now reads "multiplied by 0.75 and rounded **up** to a whole dollar" (compute ceiling). Tier 1 stays rounded down and the fall-through unrounded.
- **card_ext_good_standing_payment:**
  - Rule sentence 5 now reads "The owed minimum on a revolving card (a tier with a minimum-payment percentage above zero) …".
  - Compute owed_minimum adds `and P('min_payment_pct_of_balance') > 0` to both recompute branches.
- Nothing else in the four policies differs from the round-1 reading: params, other compute bindings, baselines, inputs, overwrite blocks and the E2 edge.

### policy_conflict_scan (revision_2)
- Unchanged in substance. Four extended policies, two disjoint trees jointly covering them, and the same cross-category reads (special, special, install, none).
- The changes add no overlap of subject, trigger or quantity.

### rule_compute_equivalence (revision_2)
- **refund_credit late_posting_clock:**
  - delay_credits and cancel_credits are XSUM over the 3-month window, as in "applied in the same 3 months total".
  - Equality is tested to the cent, as in "exactly the same amount".
  - delay_credit_date / cancel_credit_date stay unwindowed XLATEST while the rule says "the latest of those delay-credit dates". The tier is entered only when the windowed total is > 0, and no credit is dated after today, so the unwindowed latest is the windowed latest. They are equivalent.
  - The fall-through is the refund date. All other refund bindings are unchanged and equivalent.
- **promo_autopay drafts:**
  - `-((-(n*0.5))//1)` = ceiling, as in "halved and rounded up to a whole number".
  - `int(n*0.75)` = floor for n ≥ 0, as in "multiplied by 0.75 and rounded down".
  - `MX(1, …)` everywhere, as in "never fewer than 1". Equivalent.
  - O-1 (CFIELD first order) and O-2 (due-date count assumes monthly statements) are unchanged and still latent.
- **late_fee lapse_fee:** tier 2 `-((-(x*0.75))//1)` = ceiling, as in "rounded up". Equivalent.
- **good_standing owed_minimum:** both recompute branches now require P('min_payment_pct_of_balance') > 0, as in "a revolving card (a tier with a minimum-payment percentage above zero)". The rule applies "the same way" to the return-credit branch, and compute applies the same test there. **O-3 is closed.**
- No compute basis is invented and no rule promise is left empty.

### action_binding_and_uuids (revision_2)
- Carried forward by reference: task_tools.py hash unchanged (82a16bf9…), and the four (target_tool, computes) pairs and target_tool fields are unchanged in the yaml.
- O-4 (no phone-fee write) is unchanged.

### prerequisite_graph (revision_2)
- E1 policy_source is changed and is verbatim at rule sentence 2 (yaml line 1623).
- condition, kind, gate (promo_credits), form, resolved_by and effect are unchanged and valid. E2 is unchanged.
- The graph is acyclic, and `prerequisite` is filled everywhere.

### prerequisite_sentences (revision_2)
- **E1, four-point test:**
  - (a) "not … until".
  - (b) State form: "every special order refund issued to the Ridgeline Consumer Credit tender in the customer's name in the last 3 months stands on the account as a return credit". No action or performer.
  - (c) No tool, id or snake_case token.
  - (d) The scope now equals the condition: special-order refunds, RCC tender, 3 months. **O-5's sentence/condition mismatch is closed.**
- Residual: card_ext_refund_credit's trigger sentence still names "a Ridgeline selling program" while its amount counts special-order refunds only. This is now internal to the leaf policy and does not touch the edge. Observation O-5r.
- One write (post_refund_return_credit_59e816eb) brings the state about. The derivation is unchanged, with a single reading.
- E2 is unchanged and passes.

### override_declarations (revision_2)
- Unchanged: refund amount and late-fee amount are declared. O-6 (autopay lead days) and O-7 (full-amount promo payments) remain observations.
- The changed clock tiers and draft tiers are extended-only quantities that base never governs.

### factor_ladders (revision_2)
| policy | factor | label | honest? | multi-source | cross-difficulty |
|---|---|---|---|---|---|
| refund_credit | allowance_rate | parameter | yes | no | — |
| refund_credit | late_posting_clock | method | yes (anchor record changes) | yes (credit totals vs refund totals, distinct ledger rows) | special |
| refund_credit | flat_courtesy | parameter | yes | no | — |
| refund_credit | allowance_multiplier | **parameter** | **yes (F-1 closed)** | no | — |
| promo_autopay | plan_horizon | method | **yes, by the same standard applied to lapse_treatment in round 1**: the three tiers now use three different rounding treatments (ceiling, floor, none) of differently scaled counts, a change of rounding mode, which check 2 treats as a convention distinct from a parameter value. F-2 closed; see O-11 | tier 1 single-source | — |
| promo_autopay | plan_margin / spending_addon | parameter | yes | no | — |
| promo_autopay | open_order_cushion | parameter | yes | no | special |
| late_fee | fee_level / balance_addon | parameter | yes | fee_level yes | — |
| late_fee | lapse_treatment | method | yes: floor-half / ceiling-0.75 / unrounded, three rounding treatments (O-8 acted on and now unambiguous) | no | — |
| late_fee | project_relief | parameter | yes | no | install |
| good_standing | owed_minimum_basis / bridge_days | method | yes | yes | — |
| good_standing | bridge_rate / representment_cushion | parameter | yes | no | — |

- **Counts:**
  - refund_credit: 3 parameter + 1 method.
  - promo_autopay: 3 parameter + 1 method.
  - late_fee: 3 parameter + 1 method.
  - good_standing: 2 parameter + 2 method.
  - Every policy has 4 factors. Per tree, there is ≥ 1 multi-source and ≥ 1 cross-difficulty factor (unchanged).
- **Realism:**
  - F-3 is closed. The clock tiers now hold only when the card-tender refunds *are the payout of* the delay (or cancellation) credits, tested by equal totals in the same 3-month window. That ties the credit to the refund being credited; an unrelated order's credit of a different amount can no longer start the clock.
  - The other conditions and outcomes are as in round 1.
- **Distinct outcomes:**
  - O-9 (fee_level coincides on Project Loans) is unchanged.
  - plan_horizon's tiers are distinct methods. On a 3-due-date world, however, tier 1 (⌈1.5⌉ = 2) and tier 2 (⌊2.25⌋ = 2) give the same count (O-11).
- **Baselines:** all fall-through tiers equal their baseline, and the baseline.rule sentences are unchanged.

### findings (revision_2)
- **F-1: closed.** allowance_multiplier is now labelled `parameter` (yaml line 1570).
- **F-2: closed.** plan_horizon's tiers now differ in rounding treatment (yaml lines 1629, 1663, 1695–1705), which meets the method standard applied in round 1. The count of honest `method` factors in card_ext_promo_autopay is 1.
- **F-3: closed.** late_posting_clock's tiers are tied to the refunds by the payout test (yaml lines 1476, 1492–1496, 1539–1553).
- **O-3: closed.** **O-5: closed** for the edge; residual O-5r recorded. **O-8: resolved** (now unambiguous).
- **New observation O-11:** plan_horizon's method label rests solely on rounding direction and scale. On any world with 3 plan due dates, tier 1 and tier 2 both give 2 drafts, so the ladder cannot tell a returned-payment account from a late-fee account there. This is not a RED: the methods are distinct as stated, and the factor still bears weight against its baseline.
- Unchanged observations: O-1, O-2, O-4, O-6, O-7, O-9 and O-10.
- **No new RED.**

### closing_checklist (revision_2)
Written 2026-10-08T09:04:30Z, after both round-2 reveals. The revision_2 charter-global sections above were frozen pre-reveal (sha256 45a1850a…).

- **Per-task files:** 0.md and 1.md each carry the round-1 text untouched plus a `revision_2` with a frozen derivation, then the comparison. Both now PASS.
  - Task 0: PASS (round 1: SOURCE-FACTOR RED; F-1, F-2 and F-3 closed).
  - Task 1: PASS (round 1: PASS).
- **Coverage and scope:**
  - Extended policies are fully covered.
  - Scopes are disjoint: task 0 {refund_credit, promo_autopay}, task 1 {late_fee, good_standing}.
  - Task tools and GT are closed.
  - The uuid8s are independent and frozen (task_tools.py unchanged).
- **Trees:** each has 1 prerequisite problem, 1 value_input edge and an owner=user root write. The difficulty-wide graph is a DAG.
- **Factors:**
  - Every computation has a self-sufficient baseline (fall-backs 364.07, 1670.00, 32.00, 155.38 ≠ gold).
  - Each has 4 factors with ≥ 2 parameter and ≥ 1 honest method.
  - Each tree has ≥ 1 multi-source and ≥ 1 cross-difficulty factor with seeded rows.
  - Every ladder has 3 tiers stated in its rule, and every factor bears weight on its world.
- **Gates:** not re-run by the auditor. The coordinator's round-2 snapshot (all OK except TRACEABILITY, pending KB; CACHE-DIFF INFO) was taken on the final form: card.extended.yaml / task_tools.py prefixes 79842f44 82a16bf9 , unchanged through this audit.
- **Open observations** (not grounds for rework): O-1, O-2, O-4, O-5r, O-6, O-7, O-9, O-10, O-11.
- **Result:** the difficulty **passes** the source-layer audit (TRACEABILITY to be re-judged after the KB render).
