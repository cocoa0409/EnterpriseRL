# Policy-task audit — card_billing_payments_and_disputes / charter-global

## charter_global_frozen

- Frozen: written to disk by 2026-09-12T18:50Z (UTC), round 1, before any task's GT was revealed. Nothing in this section is derived from a revealed GT field.
- Auditor: independent erl-task-policy-audit agent (Claude). It did not author the audited artifacts and was given no answers.
- Freeze hashes (sha256, checked against the orchestrator MANIFEST):
  - `env/regional_retail_bank/tasks/card_billing_payments_and_disputes/card.extended.yaml` = `a56e40d65fc96b096f8d37698271658d7c097b342a4cc8548a15b40918c6c362`
  - `env/regional_retail_bank/tasks/card_billing_payments_and_disputes/task_tools.py` = `d83a5ee8c9ca6af1fd84a440513dca45bb0ba24c2433c93afe9f8e6bac77b628`
- Read to build this section: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/card.yaml`, the extended charter, `task_tools.py`, and the compute-DSL helper definitions (`skills/erl-task-instantiate/scripts/check_compute.py`, lines 141-260: `COUNT/SUM` are scoped to the holding and `within_months` means `0 <= MONTHS(posted, now) < n`; `EXISTS/CFIELD` are scoped to the holding's customer; `RND` is Python `round`).
- Masked and not read before every task's derivation was frozen: every task field except `frozen_time`, `user_scenario` and `initial_state` (so `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`). `worklog.md`, sibling difficulties and other scenarios were not read.
- Entry conditions (Step 0): the gate snapshot came with the brief. check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding and check_cross_fire all exited 0. check_traceability is deferred until the KB is published. The masked views and their hashes were supplied, and the view hashes match the files on disk. Input is complete.

### policy_conflict_scan

**The base copy is verbatim.** Lines 1-1524 of the extended charter are byte-identical to `blueprint/products/card.yaml` (`diff` is empty). All ten top-level keys also compare equal as parsed YAML. The only additions are `extended_policies` (6) and `workflows` (1).

**Overlapping subjects among the extended policies:**

| Extended policy | subject | target_tool | computes | owner |
| --- | --- | --- | --- | --- |
| card_ext_autopay_miss_late_fee_ground | card_fee_reversal | reverse_autopay_late_fee_e77f172c | adjustment_reason | agent |
| card_ext_autopay_source_restoration | card_rewards_redeem | restore_overdrawn_checking_with_points_4e4b44ef | reward_points | user |
| card_ext_rewards_balance_payoff | card_rewards_redeem, card_rewards_credit | apply_points_to_card_balance_295c0528 | reward_points | user |
| card_ext_closing_balance_autopay | card_set_autopay | set_closing_card_autopay_dbe1c3a9 | autopay_amount | user |
| card_ext_closing_points_cashout | card_rewards_redeem | cash_out_closing_card_points_6700a44f | reward_points | user |
| card_ext_closure_autopay_carryover | card_close | confirm_card_closure_806ea607 | autopay_option | user |
| (workflow step 0, no extended policy) | card_fee_reversal | refund_closing_annual_fee_cfb04f99 | — (base card_evt_annual_fee) | agent |

- Three policies write `card_rewards_redeem`, and they are told apart by trigger:
  - restoration: an ask to apply points to the balance while the autopay source is overdrawn;
  - payoff: an ask to pay the balance down with points;
  - cash-out: an ask to cash out while closing.
  
  Restoration and payoff fire together by design (restoration is a prerequisite of payoff). Cash-out never overlaps them, because its trigger needs a closing. No two policies reach different conclusions on the same trigger.
- **Time anchors:**
  - fee ground: "less than one whole calendar month before the handling date", with the most recent statement's `payment_due_date`;
  - annual-fee refund: base `annual_fee_refund_window_days` = 30;
  - every other policy: handling time.
  
  No two of these anchors conflict.
- **Cross-category reads.** All of them read `checking_accounts` of the same customer only (the DSL scopes to the customer). The reads are status, negative_since_date and ledger_balance. None of the policies writes checking.
- **Terminal states.** The payoff leaves the card's balance at or above zero when an active checking account exists. The closure leaves status `closed`, with the option decided by the carryover policy. The findings below record where a terminal state conflicts with inherited base text.
- **Claimed scopes of the M = 2 tasks, inferred only from the permitted views and tool contracts:**
  - task 0 is the payoff tree: payoff, fee ground and restoration;
  - task 1 is the workflow tree: workflow, closing autopay, cash-out and carryover.
  
  The two sets are disjoint. Together they cover all 6 extended policies and the single workflow, and exactly one task (task 1) claims the workflow. This inference is re-checked against `charter_scope` only in the closing checklist, after the reveal.

### rule_compute_equivalence

Check 2, policy by policy, in both directions (rule sentence to compute binding, and compute binding back to rule sentence):

- **card_ext_autopay_miss_late_fee_ground.**
  - `fees_in_window` and `reversals_in_window` implement "posted date is less than one whole calendar month before the handling date … counted as the late payment fees posted in that window minus the late payment fee reversals posted in that window". The DSL's `within_months=1` is exactly `0 <= MONTHS < 1`, and the counting rule is taken verbatim from the rule.
  - `covers_minimum` is the first condition.
  - `source_status` is the second. The DSL restricts `EXISTS/CFIELD` to the cardholder's own checking, which matches "of the cardholder".
  - `funded_on_due_date` is the third. It is a string compare of ISO dates, which matches "empty or is a date later than".
  - `payments_on_due_date` is the fourth. `F('payment_due_date')` matches "the payment_due_date of the card's most recent statement".
  - `result` requires all four conditions plus at least one unreversed fee.
  - The rule's "full amount of the fee" is not a compute output. The tool `amount` takes the fee row's amount, per base card_evt_fee_reversal "reversed in full".
  - No binding lacks a basis, and no rule sentence lacks an implementation.
- **card_ext_autopay_source_restoration.**
  - The shortfall is `MX(0, -ledger)` on the named source.
  - Points needed is the ceiling of `RND(shortfall/value, 6)`, which matches "rounded up to the next whole point".
  - Unredeemed is ledger earn − redeem − forfeit.
  - Target is `MX(min, needed)`. It falls back to all unredeemed when the target exceeds them, and pays nothing when unredeemed < min or shortfall = 0.
  - Equivalent in both directions.
- **card_ext_rewards_balance_payoff.**
  - The balance is `F('current_balance')` "after those reversals". This is correct because the reversal tool updates `current_balance`.
  - The cover points are the ceiling of balance/value, and 0 when the balance is 0 or below.
  - The applied points are `MN(unredeemed, cover)` when the customer has an active checking account, and all unredeemed otherwise.
  - The result is 0 when the balance is 0 or below, or when the applied points are below the minimum.
  - Equivalent. The credit amount (points × value, half-up) is not a compute output. It is the base `redemption_value` formula.
- **card_ext_closing_balance_autopay.**
  - The 13-term ledger sum matches the rule's list item for item.
  - It is capped at `last_statement_balance`.
  - It is 0.00 when the balance is 0 or below, or when there is no active checking account.
  - `RND` is applied once, at the end. The DSL's `SUM` also rounds each 2-decimal sum to 2 places, which cannot move a sum of cent values.
  - Equivalent.
- **card_ext_closing_points_cashout.** The receiver is `F('autopay_source_account_id')`. The deposit is all unredeemed points when the receiver is active and unredeemed ≥ min, and 0 otherwise. Equivalent.
- **card_ext_closure_autopay_carryover.** The option is `none` when the balance is 0 or below. When a balance remains, the option is kept if the source is active and set to `none` otherwise. Equivalent.
- **Observation O-1 (rounding convention).** Rules say "rounded half-up"; the DSL `RND` is Python `round` on binary floats. No half-cent value arises in either task (the values are 64.18, 244.42, 291.82 and 132.71), so there is no consequence.

### action_binding_and_uuids

- **(target_tool, computes).** Each pair is claimed by exactly one policy (table above). The workflow step `refund_closing_annual_fee_cfb04f99` has `computed_by: []`. Its parameters come from base card_evt_annual_fee ("reversed in full with adjustment_reason bank_error").
- **uuid8s:**
  - e77f172c, 4e4b44ef, 295c0528, cfb04f99, dbe1c3a9, 6700a44f, 806ea607.
  - All seven are distinct and no two share a prefix or form a sequence. No tail is a modified copy of another tool's, and none shows signs of batch derivation. Nothing on record contradicts independent generation.
- **Tool bodies (`task_tools.py`):**
  - The bodies contain no branch on eligibility, status, window, prerequisite or amount. The only conditional is `_open_cycle`, which is posting-cycle bookkeeping.
  - None of the seven tools refuses, errors or hints when a prerequisite is unresolved.
  - No tool adds a confirmation, review or wait.
- **Observation O-2 (the cross-category redemption trigger is not implemented).**
  - Base event `card_rewards_redeem` declares the trigger `checking:checking_deposit` when `redemption_type: deposit_to_checking` (extended charter lines 783-785).
  - `restore_overdrawn_checking_with_points_4e4b44ef` (task_tools.py lines 93-108) and `cash_out_closing_card_points_6700a44f` (lines 242-257) write only the card-side redemption row and `rewards_balance`. They never credit the receiving checking account or clear `negative_since_date`.
  - The module docstring presents this as a design choice ("exactly one atomic card-ledger or card-account posting").
  - Consequence: after a restoration the DB still shows the source overdrawn, and after a cash-out the checking ledger is unchanged. No agent action can produce the other terminal state, and no scored parameter reads the checking row after these writes. The per-task files record the check. Recorded as an observation.

### prerequisite_graph

Check 7 over the whole graph. The edges are:

- `card_ext_rewards_balance_payoff` → `card_ext_autopay_miss_late_fee_ground`: value_input, gate `balance`, resolved_by reverse_autopay_late_fee_e77f172c.
- `card_ext_rewards_balance_payoff` → `card_ext_autopay_source_restoration`: state_gate, gate `card_transactions.counterparty_account_id`, resolved_by restore_overdrawn_checking_with_points_4e4b44ef.
- `card_ext_closing_points_cashout` → `card_ext_closing_balance_autopay`: value_input, gate `receiver_status`, resolved_by set_closing_card_autopay_dbe1c3a9.
- `card_ext_closure_autopay_carryover` → `card_ext_closing_points_cashout`: state_gate, gate `card_transactions.redemption_type`, resolved_by cash_out_closing_card_points_6700a44f.
- `card_ext_closure_autopay_carryover` → `card_ext_closing_balance_autopay`: value_input, gate `option`, resolved_by set_closing_card_autopay_dbe1c3a9.
- All other policies and the workflow declare `prerequisite: []`.

Results:

- **Filled in and well-formed.** Every policy and the workflow fills in `prerequisite`. Every `problem` is an extended id in this file; none is a base id and none is self-referential. The graph is acyclic: it is two disjoint trees of depth 1 and depth 2.
- **Every `policy_source` is verbatim in the cited `rule`.** Checked mechanically after whitespace normalisation: all 5 are True.
- **Each `condition` agrees with its cited sentence**, neither strengthened nor weakened.
- **`resolved_by` makes each `effect` hold:**
  - the reversal tool lowers `current_balance`;
  - the restoration tool writes a `deposit_to_checking` row whose `counterparty_account_id` is the source;
  - `set_closing_card_autopay` writes `autopay_option` and `autopay_source_account_id`;
  - the cash-out tool writes a `deposit_to_checking` row.
- **`kind` matches `gate`.** Each value_input gate (`balance`, `receiver_status`, `option`) is a real binding of the dependent's compute.
- **Observation O-3 (state_gate gates are field paths).** The two state_gate gates are field paths, not eligibility-entry ids, because extended policies carry no eligibility blocks. Each denotes the procedural precondition its rule sentence states ("must first be deposited", "must already be cashed out").
- **Observation O-4 (world assumptions in general text).**
  - Two `effect` texts assert a world-specific baseline: "instead of 0" on cashout→closing autopay, and "instead of none" on carryover→closing autopay. Both hold only when the card names no active autopay source beforehand.
  - The workflow `order_rationale` likewise states "before step 1 the card names no autopay source". A card carrying an active autopay source satisfies the scenario ("an active rewards credit card") yet falsifies this sentence.
  - These phrasings are authored from the task's viewpoint, but no consequence is demonstrable in either task's world. Recorded as observations.
- **Observation O-5 (the refund→autopay dependency is carried only by workflow order).**
  - The refund → closing-autopay dependency exists only as workflow order and `order_rationale`: step 0's refund lowers the ledger balance that `card_ext_closing_balance_autopay` sizes.
  - No `prerequisite` edge carries it. `card_ext_closing_balance_autopay` declares `[]`, and its rule only says "so any fee already refunded as part of the closing is out of it", which does not require the refund to happen first.
  - The per-task check is in task 1.

### override_declarations

Check 1's finding half. Every extended policy declares `overwrite: []`, so each conclusion below is sentence by sentence against its `base_policy_refs`.

**card_ext_autopay_miss_late_fee_ground** (refs card_evt_fee_reversal, card_evt_payments, card_evt_late_and_returned_payment_fees):
- **card_evt_fee_reversal:**
  - "reversed in full … one card_fee_reversal row whose source_item_id is the fee": followed.
  - "A bank_error reversal applies to any fee billed contrary to this charter, such as …; it has no limit": followed. The extended rule names one more instance of contrary-to-charter billing: the bank's failure to take the autopay debit that card_evt_payments says it takes on the due date. It uses no allowance.
  - "A courtesy_waiver reversal applies only to a late_payment fee", the courtesy count, the prior on-time payments, and active/suspended: not touched. The extended rule defers courtesy to base when its result is `none`.
  - "A fee can be reversed at most once": followed ("has not already been reversed").
  - dispute_final: not applicable.
- **card_evt_payments:**
  - The crediting and cutoff sentences are followed.
  - The autopay sentence ("debits the named PCB checking account on the due date") is the premise of the extended rule, and the autopay-source sentence is its second condition.
  - Observation O-6: the fourth condition inspects only the due date itself. It does not look at the next business day that base's weekend/holiday sentence makes on-time. This bites only when the due date is a non-business day, which is not the case in either task.
- **card_evt_late_and_returned_payment_fees:** the extended rule does not change when or how much a late fee is billed. It only decides the reversal ground. Followed.
- Conclusion: no undeclared override.

**card_ext_autopay_source_restoration** (refs card_evt_rewards, card_evt_payments):
- **card_evt_rewards:**
  - whole points: followed;
  - "at least rewards_redemption_minimum_points per redemption": followed (the target is at least the minimum, and no deposit is made below it);
  - "a deposit to a PCB checking … account of the same customer … at rewards_point_value_cash": followed, into the same customer's source;
  - "Redemption is allowed only while the account is active": inherited.
- **card_evt_payments:** the autopay-source sentence is the premise. Followed.
- Conclusion: no undeclared override.

**card_ext_rewards_balance_payoff** (refs card_evt_rewards, card_evt_payments):
- **card_evt_rewards:** statement credit is an allowed type, and whole points and the minimum are followed. The number of points is a quantity base leaves to the request, and the extended rule fixes it without contradicting base.
- **card_evt_payments:** "A payment larger than the balance creates a credit balance that is refunded on request". The extended branch "no active checking → all unredeemed" can create a credit balance, which is consistent with base.
- Conclusion: no undeclared override.

**card_ext_closing_balance_autopay** (refs card_evt_payments, card_closure):
- **card_evt_payments:** "a fixed amount but never more than the statement balance" is followed by the cap at last_statement_balance. The active same-customer source rule is followed. "Setting up or changing autopay is the cardholder's own instruction" is followed (owner user).
- **card_closure:** "autopay continues until the balance reaches zero". Observation O-7: the extended rule makes the closing instruction a fixed_amount instruction. On a card already carrying a different, valid autopay option, that replaces the instruction base says "continues". Neither task's world exercises this: task 1's card carries `autopay_option none`.
- Conclusion: no conflict demonstrable in any task world.

**card_ext_closing_points_cashout** (refs card_evt_rewards, card_closure, card_evt_payments):
- **card_evt_rewards** — "Points are redeemed only in whole points, at least rewards_redemption_minimum_points per redemption, by one of rewards_redemption_types: a statement credit, a deposit to a PCB checking or savings account of the same customer, or a gift card, each at rewards_point_value_cash per point":
  - the extended rule handles the receiving account differently and does not declare it: "into the PCB checking account named on the card's closing autopay instruction … when the card names no autopay source account, or the named account is not active, this policy makes no deposit and the result is 0";
  - base allows a deposit to any PCB checking account of the same customer;
  - the extended rule zeroes the quantity whenever the card names no active autopay source, even when the customer holds an active checking account that base would accept;
  - this is the **0/1 multiplier** shape: an existence condition multiplied onto a points quantity that base has already fixed. → **Finding F-1**.
- **card_closure** — "Unredeemed points are forfeited at closure": followed.
- **card_evt_payments**: nothing is contradicted.

**card_ext_closure_autopay_carryover** (refs card_closure, card_evt_rewards, card_evt_payments):
- **card_closure** — "Closing a card is the cardholder's own decision: the agent registers a card_requests row of request_type account_closure in pending_customer_confirmation status, and the account closes only after the cardholder confirms":
  - neither the extended rule nor the workflow keeps the agent's registration of a `card_requests` row;
  - the workflow's step list ends with the cardholder's `confirm_card_closure_806ea607` and has no registration step;
  - no task or share tool can create a `card_requests` row (share_tools.py has only `find_card_requests`; task_tools.py has none);
  - the base sentence is not named in any `overwrite`. → **Finding F-2**.
- **card_closure** — "A balance does not prevent closure … autopay continues until the balance reaches zero": followed for the zero-balance → none branch.
  - Observation O-8: base event `card_close` gives the field semantics "autopay_option: Unchanged while a balance remains". The extended branch "a balance remains but the card names no autopay source, or the source is not active → none" changes an existing non-none option to none while a balance remains.
  - This is demonstrable only on a card whose option is not `none` while its source is missing or inactive. Neither task's world has such a card: in task 1, when step 1 is skipped the option is already `none`.
- **card_evt_rewards** — "a cardholder closing the card must redeem before the closure is confirmed": followed, as the state_gate.

**card_wf_rewards_card_closure:**
- Step 0 cites `card_evt_fee_reversal` only. Observation O-9: the governing base sentence for the refund is card_evt_annual_fee's "When the cardholder closes the account within annual_fee_refund_window_days … reversed in full with adjustment_reason bank_error", which card_closure repeats. The parameters are nonetheless unique.

### workflow_shape (check 6, charter-level half; the task-level half is in 1.md)

- Exactly one workflow, `card_wf_rewards_card_closure`.
- It has 4 synchronous write steps: agent, user, user, user. Three steps are `owner=user`, and each can be completed in the same consultation.
- The dataflow has two `object_binding` entries:
  - step 1 → 2: `card_accounts.autopay_source_account_id` → `checking_account_id`;
  - step 1 → 3: `autopay_option` → `autopay_option`.
  
  Both correspond verbatim to the tool arguments.
- **Observation O-10 (missing zero-wait fields and dataflow rows).**
  - The workflow has no `requires_external_wait` field and no `zero_wait_proof` field. Its keys are `dataflow, id, order_rationale, prerequisite, scenario, steps`. The only zero-wait statement is the last sentence of `order_rationale`.
  - The step 0 → 1 dependency (the balance the refund lowers) has no dataflow row, and neither does the step 2 → 3 dependency (the points state).
  - Zero-wait holds in substance, as argued per step in task 1, so no consequence is demonstrable. Recorded as an observation.

### findings

**F-1: SOURCE-POLICY. An undeclared 0/1 override of base card_evt_rewards by card_ext_closing_points_cashout. Bears on task 1.**
- **Symptom.** For a cardholder closing a card who asks to cash points out to checking, base and extended reach different conclusions on `reward_points` whenever the card names no active autopay source.
- **Root cause.** The extended rule ties the receiving account to "the PCB checking account named on the card's closing autopay instruction" and returns 0 otherwise. Base permits a deposit to any PCB checking account of the same customer. `overwrite: []`.
- **Evidence.**
  - Base card_evt_rewards rule (extended charter lines 1390-1394): "…by one of rewards_redemption_types: a statement credit, a deposit to a PCB checking or savings account of the same customer, or a gift card, each at rewards_point_value_cash per point…".
  - card_ext_closing_points_cashout rule (lines 1825-1834): "…as one deposit_to_checking redemption into the PCB checking account named on the card's closing autopay instruction… when the card names no autopay source account, or the named account is not active, this policy makes no deposit and the result is 0."
  - Compute `result: "0 if (below_minimum or receiver_status != 'active') else unredeemed"`.
- **Consequence.** It is demonstrated in task 1's opening world; see `1.md`. The value_input edge cashout → closing_balance_autopay bears weight only through this undeclared restriction.
- **Affected artifact.** card.extended.yaml › extended_policies › card_ext_closing_points_cashout (rule, compute.result, overwrite), the prerequisite edge on it, and workflow order_rationale sentence 2.

**F-2: SOURCE-POLICY. An inherited base agent write is silently dropped from the closure SOP and has no executing tool. Bears on task 1.**
- **Symptom.** The inherited base card_closure procedure includes an agent-owned `card_requests` registration. The workflow's closure path, and every tool in the difficulty, omit it.
- **Root cause.**
  - card_ext_closure_autopay_carryover lists card_closure in `base_policy_refs` with `overwrite: []`, so the base procedure is inherited in full.
  - The workflow `card_wf_rewards_card_closure` is still authored as the complete synchronous SOP ("…and the cardholder confirms the closure").
  - Its four steps contain no registration, and no tool writes `card_requests`.
- **Evidence.**
  - card_closure rule (extended charter lines 1517-1518): "the agent registers a card_requests row of request_type account_closure in pending_customer_confirmation status, and the account closes only after the cardholder confirms."
  - The workflow steps (lines 1964-1967).
  - task_tools.py: seven tools, none writing `card_requests`.
  - share_tools.py lines 425-440: `find_card_requests` is read-only, and no share write touches `card_requests`.
- **Consequence.** It is demonstrated in task 1's world; see `1.md`.
- **Affected artifact.** card.extended.yaml › card_ext_closure_autopay_carryover (overwrite) and workflows › card_wf_rewards_card_closure › steps; task_tools.py (no registration tool).

**Observations O-1 to O-10 (above).** None of them demonstrates a consequence against either task's world at charter level. Task files re-check the ones that touch their world: O-2, O-5, O-6 and O-7/O-8 in their respective tasks.

## closing_checklist

Written after both reveals, at about 2026-09-12T18:55Z. Nothing above this heading was changed after the reveal.

- **Per-task files.**
  - `0.md` and `1.md` correspond one-to-one with `tasks/0.json` and `tasks/1.json`, and this file sits beside them.
  - Round 1, no earlier revision.
  - Each file carries a frozen derivation that was hashed before the reveal, followed by a `source_gt_comparison`.
- **Verdicts:**
  - task 0: **PASS**. Policy self-consistency PASS, problem tree PASS, unique solution PASS.
  - task 1: **SOURCE-POLICY RED**. F-1 is the undeclared 0/1 override in card_ext_closing_points_cashout. F-2 is the undeclared drop of base card_closure's agent registration of a `card_requests` row. Problem tree PASS; unique solution PASS.
- **Coverage and scope** (confirmed against the revealed `charter_scope`):
  - task 0 = {card_ext_autopay_miss_late_fee_ground, card_ext_autopay_source_restoration, card_ext_rewards_balance_payoff}, workflows [], tools {e77f172c, 4e4b44ef, 295c0528};
  - task 1 = {card_ext_closing_balance_autopay, card_ext_closing_points_cashout, card_ext_closure_autopay_carryover}, workflows [card_wf_rewards_card_closure], tools {cfb04f99, dbe1c3a9, 6700a44f, 806ea607}.
  - The two scopes are pairwise disjoint across the whole problem trees and jointly cover all 6 extended policies. There is exactly one workflow, claimed only by task 1.
  - Task tools and GT are closed: every GT write tool is in its task's scope, and every scoped tool is used.
  - All seven uuid8s are distinct (§ action_binding_and_uuids).
- **Problem trees:**
  - Task 0 has 2 prerequisites, 1 of them value_input, and no cycle.
  - Task 1 has 2 root prerequisites plus 1 nested, 2 of them value_input, and no cycle.
  - The difficulty-wide `prerequisite` graph is two disjoint DAGs. No cross-task reference exists.
- **Gates.** The artifacts are byte-identical to the gate snapshot supplied in the brief. Hashes re-checked at 18:53:45Z: charter `a56e40d6…`, tools `d83a5ee8…`, `0.json` `9243947b…`, `1.json` `4a0a62ff…`. The instantiation gates were therefore not re-run by this auditor, per Step 0.
- **Difficulty result: NOT PASSED at the source layer.**
  - Task 1 carries SOURCE-POLICY RED on F-1 and F-2.
  - Task 0 passes on its own evidence.
  - The observations O-1 to O-10 (here), O-T0-1 to O-T0-3 (`0.md`) and O-T1-a to O-T1-d (`1.md`) are recorded and are not grounds for rework.

## revision_2

### charter_global_frozen (revision 2)

- Written before any round-2 task GT was read.
- Auditor: the same independent erl-task-policy-audit agent as round 1.
- Inputs:
  - `card.extended.yaml` sha256 `0d0299c581f22596970a0c76f318c3e1d9ca395111026119d4cff322a4cd371d`, changed from round 1's `a56e40d6…`, so this section is re-derived in full;
  - `task_tools.py` `d83a5ee8…b628`, unchanged;
  - `share_tools.py`, `db_schema.json` and `products/card.yaml`, all unchanged.
- The round-2 masked views match the MANIFEST hashes and are byte-identical to the round-1 views (`cmp`).
- The post-rework gate snapshot came with the coordinator's message: all 7 gates OK, traceability deferred. Input is complete.
- Round-1 text above this heading is left untouched.

### What changed in the charter (located by re-reading every extended policy and the workflow)

- **Base section (lines 1-1524).** Still byte-identical to `blueprint/products/card.yaml`: `diff` is empty and all 10 top-level keys compare equal.
- **Policies unchanged on re-read.** `card_ext_autopay_miss_late_fee_ground`, `card_ext_autopay_source_restoration`, `card_ext_rewards_balance_payoff` and `card_ext_closing_balance_autopay` sit at the same line spans as round 1 (1530-1815), and their rule, compute, compute_basis and prerequisite are unchanged. Their round-1 conclusions carry forward.
- **`card_ext_closing_points_cashout`** (lines 1817-1871):
  - It now declares `overwrite: [{base_policy: card_evt_rewards, superseded_clause: "a deposit to a PCB checking or savings account of the same customer", replaced_by: "A closing cash-out is made only as a deposit to a PCB checking account of the cardholder whose status is active, the account the cardholder names"}]`.
  - The rule no longer ties the receiving account to the closing autopay instruction.
  - `prerequisite` is now `[]`: the edge to `card_ext_closing_balance_autopay` is gone.
  - The compute now reads `active_checking = CFIELD('checking','status',status='active')`, and `result = 0 if (below_minimum or not receiver_active) else unredeemed`.
- **`card_ext_closure_autopay_carryover`** (lines 1873-1949):
  - It now declares `overwrite: [{base_policy: card_closure, superseded_clause: "the agent registers a card_requests row of request_type account_closure in pending_customer_confirmation status, and the account closes only after the cardholder confirms", replaced_by: "No separate closure request is registered by the agent: the cardholder's own confirmation on the card account is the closure record, and the account closes at that confirmation and not before"}]`.
  - The same sentence is added to the rule.
  - The `effect` of the edge to closing autopay is reworded, with no "instead of none".
  - The compute is unchanged.
- **Workflow `card_wf_rewards_card_closure`:**
  - The scenario says the points are cashed out "into an active PCB checking account the cardholder names", and that the confirmation closes the card "with no separate closure request registered".
  - The step-2 role is reworded.
  - Dataflow 1→2 is removed; 1→3 is kept.
  - In `order_rationale`, step 1 before step 2 is now "by this SOP's sequencing … a swap would reach the same terminal state; the order is fixed so that every correct handling follows one procedure".
  - New fields: `requires_external_wait: false` and `zero_wait_proof`.

### policy_conflict_scan (revision 2)

- The subject/tool/computes table is the same as round 1, and the three `card_rewards_redeem` writers are still told apart by trigger.
- The cash-out's receiving account is now "an active PCB checking account the cardholder names". It no longer depends on the card's autopay fields, so it has no subject overlap with `card_ext_closing_balance_autopay`.
- The cross-category reads are still of the same customer's checking account only.
- **Scope inference from the views and contracts:**
  - task 0 = {fee ground, restoration, payoff};
  - task 1 = {workflow, closing autopay, cash-out, carryover}.
  
  They are disjoint, jointly complete, and there is one workflow.

### rule_compute_equivalence (revision 2)

- The four unchanged policies are carried forward from round 1 § rule_compute_equivalence.
- **card_ext_closing_points_cashout, rule to compute:**
  - "When the cardholder holds no PCB checking account whose status is active, no closing cash-out can be made and the result is 0" maps to `receiver_active` (customer-scoped `CFIELD`).
  - The ledger count of unredeemed points maps to `earned − redeemed − forfeited`.
  - The minimum guard maps to `below_minimum`.
  - "all of the card's unredeemed points" maps to `result`.
- **card_ext_closing_points_cashout, compute back to rule:** no binding lacks a rule sentence.
- **Observation R2-O-1 (named account not checked).**
  - "the account the cardholder names" constrains the tool argument `checking_account_id`, not the computed quantity.
  - The compute tests that *some* active checking account exists, not that the *named* one is active. A cardholder with one active and one inactive checking account who names the inactive one would get `result = unredeemed` from the compute, while the rule forbids that deposit.
  - Not demonstrable in either task: task 1's customer holds exactly one checking account, and it is active.
- **Observation R2-O-2 (pre-existing, not a regression).**
  - Pass-through bindings have no `compute_basis` key of their own: `option`/`source_negative_since` in the fee ground, `point_value`/`unredeemed`/`minimum_points` in the restoration and payoff, and `unredeemed`/`minimum_points` in the cash-out.
  - The sentence each implements is quoted verbatim under a sibling binding: `earned` for the ledger count, and `covers_minimum`/`funded_on_due_date` for the autopay fields.
  - This was present in round 1 and is unchanged. No consequence.

### action_binding_and_uuids (revision 2)

`task_tools.py` is unchanged (same hash), so round 1 § action_binding_and_uuids carries forward: one policy per `(target_tool, computes)` pair, seven distinct uuid8s, and no tool that judges a prerequisite. O-2 (the deposit tools do not credit checking) still stands as an observation.

### prerequisite_graph (revision 2)

- **Edges:**
  - payoff → fee ground (value_input, `balance`);
  - payoff → restoration (state_gate);
  - carryover → cash-out (state_gate, `card_transactions.redemption_type`);
  - carryover → closing autopay (value_input, `option`).
  
  Every policy and the workflow fills in `prerequisite`.
- **Well-formed.** Every `problem` is an extended id in this file, none is a base id and none is self-referential. The graph is acyclic: two depth-1 trees.
- **Checked mechanically:**
  - every `policy_source` is verbatim in the cited rule (4/4 True);
  - each value_input gate is a real binding (`balance`, `option`).
- **Condition and effect.** Each `condition` agrees with its cited sentence. The reworded carryover `effect` ("writes autopay_option fixed_amount and an active checking source … while a balance remains, that option is the one kept") is true of `set_closing_card_autopay_dbe1c3a9` and the carryover compute, and it asserts no world-specific baseline.
- **O-3 (state_gate gates are field paths)** is unchanged. It is an observation.

### override_declarations (revision 2)

- **card_ext_closing_points_cashout vs card_evt_rewards:**
  - The `superseded_clause` is verbatim in the base rule (mechanical check True), and `replaced_by` is verbatim in the extended rule (True).
  - Merged semantics: a closing cash-out goes only to a PCB checking account of the cardholder that is active and that the cardholder names. Savings, statement credit, gift card and travel are "not a closing cash-out under this policy". That wording scopes the policy rather than forbidding base's other redemption types, so no second conclusion arises.
  - The 0-branch now fires only when the customer holds no active checking account, which the declared `replaced_by` covers ("whose status is active").
  - Remaining base sentences: "whole points, at least rewards_redemption_minimum_points" is followed, "Redemption is allowed only while the account is active" is inherited, and "a cardholder closing the card must redeem before the closure is confirmed" is followed.
  - card_closure and card_evt_payments: no conflict.
- **card_ext_closure_autopay_carryover vs card_closure:**
  - The `superseded_clause` is verbatim in base (True), and `replaced_by` is verbatim in the extended rule (True).
  - Merged semantics: no `card_requests` row, and the card closes at the cardholder's confirmation. That is unique.
  - The rest of base card_closure is inherited: a balance does not prevent closure, the balance remains payable, points are forfeited at closure, the refund of an annual fee inside the window, and closed accounts are never reopened.
  - O-8 (the base event field "Unchanged while a balance remains" vs the extended branch "source not active → none") is unchanged and still not demonstrable.
- **The other four extended policies.** Their text is unchanged, so the round-1 conclusions (no undeclared override; O-6, O-7) carry forward.
- **Workflow.** The step-0 citation (O-9) is unchanged. It is an observation.

### workflow_shape (revision 2)

- One workflow, with 4 synchronous write steps (agent, user, user, user).
- `requires_external_wait: false` and `zero_wait_proof` are now present. The proof's step-by-step inputs are true of the charter and tool contracts: step 0 needs the fee row and the call; step 1 needs step 0's credit, the last statement balance and an active checking account; step 2 needs the points and an active checking account; step 3 needs steps 1 and 2.
- The dataflow is 1→3 `autopay_option` → `autopay_option`, which matches the tool argument.
- The removal of dataflow 1→2 is correct, because step 2 no longer consumes step 1's output.
- **Observation R2-O-3 (dataflow rows still missing).** The value dependency step 0 → step 1 (the balance the refund lowers) and the state dependency step 2 → step 3 still have no dataflow rows. This is the dataflow half of round-1 O-10, unchanged. No consequence.
- **Observation R2-O-4 (step 1 before step 2 has no policy basis).**
  - The adjacent order is now supported only by "this SOP's sequencing". `order_rationale` itself states "neither step's value depends on the other, so a swap would reach the same terminal state".
  - That is true: the two steps write disjoint fields, and the scorer compares DB hashes.
  - The fixed order has no policy basis beyond the SOP, but both orders yield one terminal state. No consequence.

### findings status (revision 2)

| Item | Round-1 verdict | Revision-2 status | Evidence |
| --- | --- | --- | --- |
| F-1 | SOURCE-POLICY RED (task 1) | **closed at charter level** | Declared overwrite on card_evt_rewards (clause verbatim). The autopay-source 0/1 multiplier is removed from the rule and compute. The receiving-account condition is now one that base (as overwritten) and the extended rule agree on. The per-task check is in `1.md` revision_2. |
| F-2 | SOURCE-POLICY RED (task 1) | **closed at charter level** | Declared overwrite on card_closure (clause verbatim). The rule and the workflow scenario say that no request is registered. The inherited procedure and the SOP now give one write set. |
| O-4 | observation | closed | The "instead of 0" edge is deleted, the "instead of none" effect is reworded, and the order_rationale no longer asserts a world baseline. |
| O-10 | observation | partly closed | The `requires_external_wait` / `zero_wait_proof` fields are present. The dataflow rows for 0→1 and 2→3 remain absent (R2-O-3). |
| O-1, O-2, O-3, O-5, O-6, O-7, O-8, O-9 | observations | unchanged | Same text and same tools. |
| New | — | R2-O-1, R2-O-2 (pre-existing), R2-O-3, R2-O-4 | All observations. None is demonstrable in either task's world. |

No new charter-level defect with a demonstrable consequence was found.

### closing_checklist (revision 2)

Written after both round-2 reveals, at about 2026-09-12T19:08Z. Nothing in the revision_2 charter-global section above was edited after the reveal.

- **Per-task files.** `0.md` and `1.md` each carry a `revision_2` section: a frozen derivation, hashed at 19:06:14Z before the reveal, followed by a comparison.
  - Round-1 text is untouched.
  - Both revision-2 derivations disclose that the auditor had already seen round-1 GT. The blind evidence of record remains the round-1 frozen derivations, which revision 2 re-checked only against what changed.
- **Verdicts (revision 2):**
  - task 0: **PASS**. Policy self-consistency PASS, problem tree PASS, unique solution PASS. Unchanged from round 1.
  - task 1: **PASS**. Policy self-consistency PASS, with F-1 and F-2 verified closed; problem tree PASS; unique solution PASS. Round 1 was SOURCE-POLICY RED.
- **Coverage and scope** (round-2 `charter_scope`):
  - task 0 = {fee ground, restoration, payoff} with tools {e77f172c, 4e4b44ef, 295c0528};
  - task 1 = {closing autopay, cash-out, carryover} + workflow `card_wf_rewards_card_closure`, with tools {cfb04f99, dbe1c3a9, 6700a44f, 806ea607}.
  - The scopes are disjoint across the whole problem trees and jointly cover all 6 extended policies and the one workflow. Exactly one task claims the workflow.
  - Tools and GT are closed, and the uuid8s are unchanged and distinct.
- **Problem trees:**
  - Task 0 has 2 prerequisites, 1 of them value_input.
  - Task 1 has 2 prerequisites, 1 of them value_input.
  - Both are acyclic. The difficulty-wide graph is two disjoint depth-1 DAGs, with no cross-task edge.
- **Gates.** The post-rework gate snapshot came with the coordinator's message: all 7 gates OK, traceability deferred.
  - At reveal the artifacts matched the snapshot hashes: charter `0d0299c5…`, tools `d83a5ee8…`, `0.json` `69caeda5…`, `1.json` `0430fc01…`.
  - The auditor did not re-run the gates, per Step 0.
- **Difficulty result (revision 2): PASSED at the source layer.**
  - Every round-1 RED is closed. No new defect with a demonstrable consequence was found, and nothing regressed.
  - The remaining items are observations only: O-1, O-2, O-3, O-5 to O-9, R2-O-1 to R2-O-4, O-T0-1, O-T0-3, O-T1-a, O-T1-b and O-T1-d.

## revision_3

### charter_global_frozen (revision 3)

- Written at about 2026-09-12T21:30Z, before any round-3 task GT was read.
- Auditor: the same independent agent.
- Inputs:
  - `card.extended.yaml` `775c4f9454ee33e0009d67ee7a2d0ba7ccc952f74275e4bb5fe27c2ca8990fc0`, changed from `0d0299c5…`;
  - `task_tools.py` `e5d430db2b109e67d378ffdc525fded241a19b9155030edb619c93a1c746c485`, changed from `d83a5ee8…`.
  
  Both changed, so every charter-global conclusion is re-derived below.
- The blueprint files are unchanged: their mtimes predate round 1, and `products/card.yaml` is `24ae1354…`.
- The round-3 views match the MANIFEST and are byte-identical to the round-1 views.
- The post-rework gate snapshot came with the coordinator's message: all 7 OK.
- **Additional input read at the coordinator's direction:** the KB audit reports `env/regional_retail_bank/audits/policy_kb/card_billing_payments_and_disputes/0.md` and `1.md`, for items N1, N2, N3 and N5.
- **Disclosure.** Those reports quote scored values. This auditor was already non-blind to this difficulty's GT from rounds 1 and 2.
- Earlier revisions above are untouched.

### What changed (located by re-reading every extended policy, the workflow, and every tool body and docstring)

- **Base section.** Still byte-identical to `blueprint/products/card.yaml`: all 10 top-level keys are equal, and the base event trigger `card_rewards_redeem → checking:checking_deposit` (lines 783-785) is still present and not overwritten.
- **`task_tools.py`:**
  - All seven function bodies are identical to rounds 1 and 2 (checked by `ast.unparse` of each body without its docstring), with the same signatures, owners and uuid8s.
  - Only docstrings changed. The module docstring and the `restore_overdrawn_checking_with_points_4e4b44ef` and `cash_out_closing_card_points_6700a44f` docstrings now say that a deposit redemption "is recorded on the card with its receiving checking account" and that the tool "does not itself post an entry on the checking account's own ledger".
- **`card_ext_autopay_source_restoration`:**
  - The ordering word "first" is removed ("are redeemed as a deposit_to_checking redemption into that same checking account").
  - It adds: "This card policy records the redemption on the card only, as a card_rewards_redeem entry that names that checking account as the receiving account and carries the cash value; the matching entry on the checking account's own ledger is not posted by this card policy, and nothing in this policy reads or waits for it."
  - The compute and compute_basis are unchanged.
- **`card_ext_closing_balance_autopay`:** "recorded before the closure" is removed. The compute is unchanged.
- **`card_ext_closing_points_cashout`:**
  - "before the closure is confirmed" is removed.
  - The overwrite `replaced_by`, and the rule, now read: "Outside a closing, points may still be redeemed as a deposit to a PCB checking or savings account of the same customer at rewards_point_value_cash per point; a closing cash-out, however, is made only as a deposit to a PCB checking account of the cardholder whose status is active, the account the cardholder names".
  - It adds the same card-only recording sentence.
  - The compute is unchanged.
- **`card_ext_closure_autopay_carryover`:** unchanged. So are `card_ext_autopay_miss_late_fee_ground` and `card_ext_rewards_balance_payoff`.
- **Workflow.** The scenario wording reads "cashed out on the card to an active PCB checking account the cardholder names". The steps, dataflow, order_rationale, `requires_external_wait` and `zero_wait_proof` are unchanged.

### policy_conflict_scan (revision 3)

- Subjects, tools and computes are the same as round 2. The three `card_rewards_redeem` writers are still told apart by trigger.
- **N3 resolution.** Redemption by deposit outside a closing now has one answer in every text that speaks to it:
  - the overwrite keeps "a deposit to a PCB checking or savings account of the same customer" in force outside a closing;
  - every rewards tier's `rewards_redemption_types` lists deposit_to_checking and deposit_to_savings;
  - the restoration's deposit_to_checking on a card that is not closing is covered.
  
  These no longer conflict.
- **Scope inference.** Unchanged: task 0 is the payoff tree, and task 1 is the workflow tree. The scopes are disjoint and complete, with one workflow.

### rule_compute_equivalence (revision 3)

- **All six compute blocks are unchanged**, and every `compute_basis` string is still verbatim in its rule (mechanical check: no failure).
- **Sentences added to rules:**
  - The card-only recording sentence (restoration, cash-out) states the tool effect. It governs no computed quantity, so it needs no binding and makes no empty promise.
  - The "Outside a closing …" clause (cash-out) grants a permission outside this policy's trigger. It is not a quantity of this compute.
- **Sentences removed** ("first", "before the closure is confirmed", "recorded before the closure") removed no quantity. No binding depended on them.
- **Round-2 observations** R2-O-1 (the compute checks that some active checking exists, not the named one) and R2-O-2 (pass-through bindings) are unchanged.

### action_binding_and_uuids (revision 3)

- The `(target_tool, computes)` pairs are unchanged. The seven uuid8s are unchanged and distinct.
- The bodies are unchanged, so no tool judges any prerequisite.
- **N1 / O-2 re-assessed:**
  - The charter now states, in both deposit policies, that the card policy records the redemption on the card only and does not post or read the checking-side entry. The two tool docstrings say the same.
  - The base event trigger `checking:checking_deposit` remains. It is base text, kept verbatim and not overwritten, so the charter still declares a checking-side deposit event that nothing in the environment writes.
  - Because the extended text scopes itself ("not posted by this card policy"), the two statements no longer contradict each other. Neither yields a different agent action, parameter or reachable terminal state.
  - **Status:** the N1 contradiction is resolved at the extended/tool layer. The residual base trigger stays as observation O-2.
- **R3-O-1 (new, observation).** The receipt gloss in both deposit tools still says `receiving_account_id (text reference number of the checking account credited)`, beside the new sentence that the tool does not post on the checking ledger. This is a wording tension with no consequence.

### prerequisite_graph (revision 3)

- The edges are unchanged:
  - payoff → fee ground (value_input, `balance`);
  - payoff → restoration (state_gate);
  - carryover → cash-out (state_gate);
  - carryover → closing autopay (value_input, `option`).
- The graph is acyclic, and every `problem` is an extended id.
- Every `policy_source` is verbatim in its rule (4/4).
- The conditions and effects are unchanged from revision 2.
- **N2 re-assessed.** Each ordering now lives only in the rule of the dependent policy (payoff, carryover) and in the workflow's `order_rationale`. The depended-on policies' own rules no longer restate "first" or "before the closure".
  - One residual restatement remains: base card_evt_rewards "so a cardholder closing the card must redeem before the closure is confirmed". It is verbatim base and cannot be edited, and it was not introduced by the extension.
  - Removing the words changes no trigger, eligibility or value: restoration is still triggered by the payoff request, and the cash-out and closing autopay are still required before closure by carryover's rule.
  - **Status:** closed at the extended layer. The base residual is recorded, but it is not a defect of this charter.

### override_declarations (revision 3)

- **card_ext_closing_points_cashout → card_evt_rewards.**
  - The `superseded_clause` is verbatim in base, and `replaced_by` is verbatim in the extended rule.
  - Merged semantics:
    - outside a closing, a deposit to a PCB checking or savings account of the same customer is allowed at the cash value, which restates base;
    - a closing cash-out goes only to an active PCB checking account the cardholder names.
  - The merged semantics are unique in both situations the texts address.
  - **R3-O-2 (new, observation).** During a closing, a *savings* deposit is granted by no text: it is not "outside a closing", and "a savings deposit … is not a closing cash-out under this policy". The single remaining reading is that it is not available during a closing, while statement credit, gift card and travel remain available under base. Neither task exercises this: task 1's customer holds no savings account and asks for cash to checking.
- **card_ext_closure_autopay_carryover → card_closure.** Unchanged from revision 2, and unique.
- **Other policies.**
  - The restoration's new sentence scopes the card policy's own write. It contradicts no base policy sentence; the base event trigger is covered under N1 / O-2 above.
  - The closing autopay's removed words change no base relation.
  - The round-1/2 conclusions for the fee ground and payoff carry forward.

### workflow_shape (revision 3)

- Unchanged from revision 2:
  - one workflow;
  - 4 synchronous steps (agent, user, user, user);
  - `requires_external_wait: false` and `zero_wait_proof` present and true of the charter and tools;
  - dataflow 1→3 correct.
- R2-O-3 (dataflow rows for 0→1 and 2→3 still absent) and R2-O-4 (the step-1/step-2 order is fixed by SOP sequencing and commutes) are unchanged. Both are observations.
- **N5 re-assessed** (the published runbook exposes task 1's whole route):
  - The framework requires exactly one workflow task per difficulty, and a workflow is itself policy text.
  - The existence of every prerequisite is conveyed by policy text rather than by the customer, which is what the problem-tree relationship requires.
  - The persona still raises only the root.
  - No source change was made, and none is needed for any of the three relationships. Recorded as a design observation, as the KB report does.

### findings status (revision 3)

| Item | Status | Evidence |
| --- | --- | --- |
| F-1 | still closed | The cash-out overwrite is declared, the compute still reads any active checking (not the autopay fields), and there is no edge to closing autopay. |
| F-2 | still closed | The carryover overwrite is unchanged, and no tool writes `card_requests`. |
| N1 (KB report) | resolved at the extended/tool layer; residual base trigger = O-2 (observation) | Restoration and cash-out rules plus the three docstrings. |
| N2 (KB report) | closed at the extended layer; base "must redeem before the closure is confirmed" remains (verbatim base) | Mechanical check: ordering words now appear only in the payoff rule. |
| N3 (KB report) | closed | The `replaced_by` keeps non-closing deposits. It is consistent with `rewards_redemption_types` and the restoration. |
| N5 (KB report) | no source change; design observation | See workflow_shape. |
| R2-O-1, R2-O-2, R2-O-3, R2-O-4, O-1, O-3, O-5 to O-9 | unchanged observations | — |
| New | R3-O-1, R3-O-2 | Observations only. Neither is demonstrable in either task's world. |

No new charter-level defect with a demonstrable consequence was found, and nothing regressed.

### closing_checklist (revision 3)

Written after both round-3 reveals, at about 2026-09-12T21:33Z. The revision_3 charter-global section above was not edited after the reveal.

- **Per-task files.** `0.md` and `1.md` each carry a `revision_3` section: a frozen derivation, hashed at 21:30:28Z before the reveal, followed by a comparison. It discloses non-blindness from rounds 1-2 and from the KB reports. Earlier revisions are untouched.
- **Verdicts (revision 3):**
  - task 0: **PASS**. Policy self-consistency, problem tree and unique solution all PASS.
  - task 1: **PASS**. Policy self-consistency, problem tree and unique solution all PASS. F-1 and F-2 remain closed.
- **KB-report items.**
  - N1: resolved at the extended/tool layer; the residual base trigger is observation O-2.
  - N2: closed at the extended layer.
  - N3: closed.
  - N5: design observation, no source change needed.
  - None of them yields a demonstrable consequence under the three relationships.
- **Coverage and scope.** Round-3 `charter_scope` is unchanged from round 2: disjoint, complete over 6 extended policies plus 1 workflow, and one workflow task. The tools are closed, and the uuid8s are unchanged and distinct.
- **Trees.** Task 0 has 2 prerequisites, 1 of them value_input. Task 1 has 2 prerequisites, 1 of them value_input. The difficulty-wide graph is acyclic, with no cross-task edge.
- **Gates.** The orchestrator's post-rework snapshot shows all 7 OK. At reveal the artifacts matched the MANIFEST hashes: charter `775c4f94…`, tools `e5d430db…`, `0.json` `30016e7c…`, `1.json` `6b5210e0…`. The auditor did not re-run the gates, per Step 0.
- **Difficulty result (revision 3): PASSED at the source layer.**
  - No new defect with a demonstrable consequence was found, and nothing regressed.
  - The new observations are R3-O-1 and R3-O-2, alongside the carried observations.
