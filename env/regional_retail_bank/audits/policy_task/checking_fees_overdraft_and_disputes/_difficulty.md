# Policy-task audit — checking_fees_overdraft_and_disputes / charter-global

## charter_global_frozen

- Charter: `env/regional_retail_bank/tasks/checking_fees_overdraft_and_disputes/checking.extended.yaml` sha256 `e0472aea4fae9ecb35d3689208866aa3c4540de7b0ef3d422cd9af44b2273241` (matches the orchestrator MANIFEST).
- Tool module: `env/regional_retail_bank/tasks/checking_fees_overdraft_and_disputes/task_tools.py` sha256 `b8ef325356f86f4c55b3a98eed5e600b1ecc8f5c66c05d3be111fdf15da8758f` (matches MANIFEST).
- Freeze time: 2026-09-12T19:05Z (UTC). Auditor: Claude, erl-task-policy-audit subagent, round 1. The auditor did not write any of the audited artifacts.
- Read to build this section: the charter above, `task_tools.py`, `blueprint/blueprint.yaml`, `blueprint/share_tools.py`, `blueprint/products/{checking,savings,auto}.yaml` (grep of the fields used), the compute DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py::build_env`, and the two masked views (frozen_time / user_scenario / initial_state only) listed in the orchestrator MANIFEST, whose hashes were re-verified (`6c4352c6…6ce`, `336f80ab…813f`).
- Explicitly masked and NOT read when writing this section: `tasks/0.json`, `tasks/1.json` and every masked field (design_rationale, db_closure*, solvability_contract, evaluation_criteria, prerequisite_closure, charter_scope, required_documents, computations); `env/regional_retail_bank/worklog.md`; any other difficulty's tasks or audits; any other scenario. No search was run over a directory containing `tasks/*.json`.
- Nothing in this section is derived from a revealed GT.

Entry conditions (Step 0): the brief supplied the instantiation-gate snapshot (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire — all exit 0; check_traceability deferred until KB publication), the masked views with hashes, and the masked-field list. Entry is complete. The deferred `check_traceability` is noted, not treated as missing input.

Base copy check: lines 1–1921 of the extended charter are byte-identical to `blueprint/products/checking.yaml` (`diff` empty; every top-level key compares equal after YAML load). The base section is verbatim.

### policy_conflict_scan

Structured policy surface: 17 base policies + 6 extended policies + 1 workflow.

| Extended policy | subject | target_tool | computes | trigger | base_policy_refs |
| --- | --- | --- | --- | --- | --- |
| checking_ext_transfer_fee_source_error_refund | checking_fee_refund | refund_transfer_fee_error_033d9cbf | amount | state_due | fee_refund, electronic_dispute, overdraft_protection_transfer |
| checking_ext_autopay_dispute_provisional_credit | checking_provisional_credit | post_dispute_provisional_credit_5453b90d | amount | state_due | electronic_dispute (one declared overwrite) |
| checking_ext_cycle_close_relationship_refund | checking_fee_refund | refund_same_day_maintenance_fee_e9518b99 | amount | on_request | fee_refund, electronic_dispute, maintenance_and_statement_fees, agg_relationship_balance |
| checking_ext_uncovered_item_fee_refund | checking_fee_refund | refund_uncovered_overdraft_fee_6b0f4e50 | amount | state_due | fee_refund, electronic_dispute, overdraft_protection_transfer, overdraft_and_returned_item_fees |
| checking_ext_uncovered_episode_extended_fee_refund | checking_fee_refund | refund_extended_overdraft_fee_22b46ecc | amount | state_due | fee_refund, electronic_dispute, overdraft_protection_transfer, extended_overdraft_fee |
| checking_ext_private_client_entry_conversion | checking_change_product | convert_checking_tier_696add48 | variant_name | on_request | product_change, agg_relationship_balance, open_and_funding |

Overlapping subjects: four extended policies share `checking_fee_refund`; each is bound to a distinct fee_code-specific tool (overdraft_transfer / monthly_maintenance / overdraft_item / extended_overdraft are hard-coded in the tool bodies), so no two policies can write the same refund row. They all specialise the base `checking_evt_fee_refund` bank_error ground; none contradicts another extended policy.

Relationship-balance basis: the two root policies (cycle_close, conversion) define the same four-part basis as each other; both differ from the base basis (see override_declarations, finding F1).

Time anchors: every extended policy is evaluated at `frozen_time`; the only extended clock rule is cycle_close's "close of business on the cycle closing date, after every posting made to the account during that business day, and before the refund of the maintenance fee itself posts", which is compatible with base `checking_agg_relationship_balance` ("taken at close of business on the measurement date … For the maintenance fee waiver the measurement date is the statement cycle closing date") and base "Pending deposits that have not posted do not count".

Cross-category read boundaries: savings (tier parameter `overdraft_protection_source_eligible`, `current_balance`, `status`), cd (`principal_balance`, `status`), mortgage (`principal_balance`, `status`), auto (`monthly_payment`, `autopay_enrolled`, `autopay_source_account_id`). All are readable through share lookups (`find_savings_accounts`, `find_cd_certificates`, `find_mortgage_loans`, `find_auto_loans`) plus the savings product charter. No write crosses a category.

Terminal states: refunds and the provisional credit are additive ledger postings (`task_tools.py` bodies add `amount` to `ledger_balance`), the conversion changes only `variant_name`. The provisional-credit tool also sets `dispute_status=provisional_credited`, which is the status the base closure policy already names.

Scope exclusivity / completeness (from the charter alone): the workflow binds exactly {transfer_fee, autopay, cycle_close}; the other prerequisite graph binds {uncovered_item, uncovered_episode, conversion}. The two groups are disjoint and together cover all six extended policies. Whether the two tasks claim exactly these groups is confirmed per task after the reveal.

### rule_compute_equivalence

Check 2, per extended policy. The compute DSL semantics used: SUM/COUNT/MAX/LATEST are auto-scoped to the target checking account; CPARAM/CFIELD filter the customer's cross-category rows and return the FIRST match; RND is Python `round` (banker's rounding on exact .xx5 ties).

- transfer_fee: `source_id` = LATEST overdraft-transfer counterparty ⇐ "most recent overdraft protection transfer entry"; `source_eligible` = CPARAM of that savings row's current tier ⇐ "read from that savings account's current tier"; `charged` = MAX fee ⇐ "largest overdraft transfer fee entry … every such fee being charged at one tier amount"; `wrong_amount`, `result` match the two bank-error grounds. Equivalent. Note: if the source savings row is not found CPARAM returns None, `None == False` is False, so compute refunds nothing where the rule is silent (observation O3).
- autopay: `claimed` = SUM of claimed_amount over submitted disputes, where the rule speaks of "the account's dispute in submitted status" (singular); `item` = LATEST ach_debit ⇐ "the account's most recent ACH debit, which is the debit that dispute names"; `cap = MX(0, item - scheduled) if scheduled > 0 else item`. **Mismatch**: the rule applies the third figure only "when the disputed item is an ACH debit PCB itself collected from this checking account for the owner's PCB auto loan under an enrolled autopay instruction"; the compute applies it whenever any autopay-enrolled auto loan funded from this checking exists, whatever the disputed item is (finding F4). Also `compute_basis.result` splices two non-adjacent rule sentences, so it is not one verbatim quotation (observation O4).
- cycle_close: `fee` = SUM monthly_maintenance within_months=1 ⇐ "posted on the account within the last month"; own/savings/cd/mortgage parts and threshold match the rule's four-part sum (which itself deviates from base, F1); `relationship` basis sentence is a timing sentence, not a formula, but the timing is implemented by evaluating on the post-credit ledger. Equivalent to its own rule.
- uncovered_item: `link_*`, `item` = MAX check_paid ⇐ "largest paid check on the account", `fee` = MAX overdraft_item fee, `covered`, `de_minimis`, `result`. Equivalent to its own rule (the rule's proxies deviate from base, F3).
- uncovered_episode: same structure plus `wrong_amount`. Equivalent to its own rule.
- conversion: parts match; `result` = target tier iff relationship ≥ target_entry_min else current tier. Equivalent to its own rule (its decision sentence drops inherited gates, F2). Params `target_entry_min 250000.00` and `target_includes_mortgage true` equal the Private Client variant's `entry_relationship_balance_min` and `relationship_balance_includes_mortgage`.
- Rounding: every rule says "rounded half-up"; RND is banker's rounding. All inputs are 2-dp money, so no tie at the third decimal can arise from these formulas (observation O5).
- No compute invents a window, tier, cap or filter that its own rule lacks; the one empty promise is autopay's conditional third figure (F4).

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one extended policy (6 policies, 6 distinct tools). Each tool's body writes exactly one event of the policy's subject (fee_code and adjustment_reason hard-coded per refund tool; the provisional-credit tool writes `checking_provisional_credit` and sets the dispute to `provisional_credited`; the conversion tool writes only `variant_name`).
- Docstrings add no confirmation, review, wait or eligibility procedure; every tool says it "does not check" the fee / dispute / qualification. Function bodies contain no branch on eligibility, status, date or prior refunds (`task_tools.py` lines 40–55, 82–94, 121–133, 160–172, 199–211, 234–237).
- uuid8s: `033d9cbf`, `5453b90d`, `e9518b99`, `6b0f4e50`, `22b46ecc`, `696add48` — pairwise distinct, no shared prefix or suffix, no sequential or adjacent pattern, none reused across tools. No evidence of batch derivation. PASS.
- Workflow step bindings: every step's `tool` equals the `target_tool` of the policy in its `computed_by`, and the step subject is covered by that policy's subject. Step `base_policy_refs` are incomplete relative to the events they realise: steps 0–1 omit `checking_evt_overdraft_protection_transfer` (listed in the policy's own base refs), step 3 omits `checking_evt_maintenance_and_statement_fees` and `checking_agg_relationship_balance` (observation O6).

### prerequisite_graph

- Every extended policy and the workflow carry `prerequisite` (four `[]`, two with edges; workflow `[]`).
- Edges: cycle_close → transfer_fee (value_input, gate own_part); cycle_close → autopay (value_input, own_part); conversion → uncovered_item (value_input, own_part); conversion → uncovered_episode (value_input, own_part). Every `problem` names an extended policy in this file, none names a base policy or itself. The graph is acyclic (two stars of depth 1, no shared nodes).
- `policy_source` of all four edges is verbatim present in the cited rule (machine-checked by substring test): cycle_close "Before the relationship waiver is judged for a maintenance fee dated the current business day, every credit the bank already owes on the account is posted first, namely a provisional credit that has fallen due on a submitted dispute and a refund of any fee charged in error, because pending credits that have not posted do not count"; conversion "Before the Private Client entry test is applied, every credit the bank already owes on the account, such as the refund of a fee charged in error, is posted first, because pending credits that have not posted do not count."
- `gate: own_part` exists as a compute binding in both roots; `kind: value_input` is correct because each resolving tool adds its amount to `ledger_balance`, which `own_part` reads (`MX(0, F('ledger_balance'))` / `0 if F('ledger_balance') < 0 else F('ledger_balance')`).
- `resolved_by` tools genuinely raise the ledger (tool bodies `ctx.update("checking_accounts", …, ledger_balance=new_balance)`), so `effect` holds.
- Conditions agree with the cited sentence edge by edge (each is an instance of "a refund of any fee charged in error" or "a provisional credit that has fallen due"). The declared edge set is narrower than the sentence: the cycle_close sentence reaches every fee-error refund policy (including uncovered_item and uncovered_episode) and the conversion sentence ("every credit the bank already owes … such as …") also reaches transfer_fee and autopay, but those edges are not declared (observation O7; per-task bite checked in each task file).
- No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") in any `prerequisite` field. The workflow's `order_rationale` does state a world fact as general text ("the later transfer fee was charged before the dispute's provisional credit deadline") and the step list hard-codes two transfer-fee refunds (observation O8).
- Every edge is discoverable from rule text; none exists only in the `prerequisite` field. PASS on acyclicity and quotability.

### override_declarations

Check 1, sentence by sentence against each `base_policy_refs` entry; conclusion per sentence, judged on the quantity that is finally scored.

**checking_ext_transfer_fee_source_error_refund** (`overwrite: []`)
- fee_refund "A fee is refunded in full, never in part, as one checking_fee_refund row whose source_item_id is the fee row and whose amount equals that fee's amount." — HANDLED DIFFERENTLY. Extended: "The amount charged is taken as the largest overdraft transfer fee entry on the account, every such fee being charged at one tier amount … refunded in full … at the amount charged … one refund per fee entry" (compute `charged = MAX(...)`). Each refund's amount is the account-wide maximum, not that fee's own amount (anonymous intermediate factor). Undeclared → F3.
- fee_refund bank_error ground, "no time limit", "does not count toward any courtesy limit", "refunded at most once", courtesy gates as fallback — FOLLOWED.
- overdraft_protection_transfer "The savings tier must have overdraft_protection_source_eligible true in the savings charter" (a gate on the link) — FOLLOWED in substance (a transfer from an ineligible tier is contrary to the charter). The extended rule's per-transfer source is "the savings account named as the counterparty on the account's most recent overdraft protection transfer entry", whereas each base transfer row carries its own `counterparty_account_id` — HANDLED DIFFERENTLY (all fees judged by the latest transfer's source). Undeclared → F3. Eligibility "read from that savings account's current tier" vs the tier when the link was recorded — HANDLED DIFFERENTLY where the tier changed since (observation-grade, folded into F3).
- electronic_dispute — no sentence governs transfer fees; nothing to follow.

**checking_ext_autopay_dispute_provisional_credit** (one declared overwrite)
- electronic_dispute amount sentence — DECLARED and replaced; merged semantics unique (min of claimed, item, and the above-scheduled part when the item is the auto-loan autopay debit).
- electronic_dispute "An electronic-transaction dispute is a claim the owner files about a debit …" and the dispute row's `disputed_txn_id` fix the disputed item per dispute — HANDLED DIFFERENTLY: extended "its disputed item is the account's most recent ACH debit, which is the debit that dispute names" selects the latest ACH debit of the account, and `claimed` sums every submitted dispute. Undeclared anonymous intermediates → F3.
- notice window, business-day deadline, new-account substitution, submitted-only, one credit per dispute, reversal rules — FOLLOWED (inherited; trigger state_due).

**checking_ext_cycle_close_relationship_refund** (`overwrite: []`)
- agg_relationship_balance "Every checking rule that speaks of a relationship balance uses one basis, the measure checking_msr_relationship_balance" and the measure "Sum over the customer's holdings of: ledger_balance of each checking account not closed or charged_off (negative balances counted as zero), current_balance of each savings account not closed, principal_balance of each certificate not closed, and, only when the tier's relationship_balance_includes_mortgage is true, principal_balance of each mortgage loan in active, delinquent or forbearance status." — HANDLED DIFFERENTLY: extended "The relationship balance is the sum of four parts: this checking account's ledger balance, counted as zero when negative; the current_balance of the owner's active savings account; the principal_balance of the owner's active certificate; and … the principal_balance of the owner's active mortgage loan". Other checking accounts, dormant savings, grace_period certificates and delinquent/forbearance mortgages are dropped, and CFIELD keeps only the first active row of each category. Undeclared → F1.
- agg_relationship_balance measurement date (cycle closing date) and "Pending deposits that have not posted do not count" — FOLLOWED; the owed-credits-first sentence elaborates it without contradicting it.
- maintenance_and_statement_fees: waivers are alternatives, never prorated, tier at cycle close, status gate, one per cycle, "A fee assessed although a waiver was met is a bank error and is refunded under checking_evt_fee_refund" — FOLLOWED (extended judges one waiver and defers the others explicitly).
- fee_refund bank_error — FOLLOWED.

**checking_ext_uncovered_item_fee_refund** (`overwrite: []`)
- overdraft_and_returned_item_fees "Each item paid into overdraft incurs overdraft_fee_per_item as a checking_fee row with fee_code overdraft_item whose source_item_id is that debit" — HANDLED DIFFERENTLY: "The item that carried the fee is taken as the largest paid check on the account, and the fee as the largest overdraft item fee entry on the account" (proxy instead of the fee's `source_item_id`; one account-wide fee instead of each fee). Undeclared → F3.
- overdraft_protection_transfer "one transfer is made for that item in the exact amount of the shortfall … the transfer is made only if the savings current_balance at that moment covers the whole shortfall" — HANDLED DIFFERENTLY: extended judges coverage by today's link and today's `current_balance` against the whole item amount ("whose current_balance is at least the amount of the item that carried the fee"). Undeclared → F3.
- de minimis item rule — FOLLOWED. End-of-day de minimis, daily limit, wrong-amount grounds — not restated; base fee_refund still grants them as bank_error ("this policy refunds nothing" is scoped to this policy) — no conflict.

**checking_ext_uncovered_episode_extended_fee_refund** (`overwrite: []`)
- extended_overdraft_fee episode definition (begins on `negative_since_date`) — HANDLED DIFFERENTLY for the episode-opening item: "The item is taken as the largest paid check on the account"; coverage test as in the previous policy; fee "taken as the largest extended overdraft fee entry". Undeclared → F3.
- "A tier whose extended_overdraft_fee is 0.00 writes no row", one per episode, wrong-amount as bank_error — FOLLOWED.

**checking_ext_private_client_entry_conversion** (`overwrite: []`)
- agg_relationship_balance basis — HANDLED DIFFERENTLY exactly as in cycle_close (this account only; active savings / certificate / mortgage only). Undeclared → F1.
- product_change "The customer must meet the target tier's entry gate on the conversion date, except the opening deposit, and the conversion must not breach checking_agg_multi_holding for the target tier" and "At most one customer-requested conversion is recorded per account per statement cycle" — HANDLED DIFFERENTLY: extended "When the relationship balance is at or above target_entry_min the tier recorded is Private Client Checking" states the relationship test as sufficient; the target entry gate's `age_at_least` and `accounts_of_this_tier_below`, the portfolio cap and the once-per-cycle limit never enter the decision sentence or the compute (dropped branch). Undeclared → F2.
- product_change "The account must be active" — FOLLOWED ("the owner of an active checking account"). "No fee … does not restart the early closure window" — FOLLOWED (tool posts no fee).
- open_and_funding age sentence — see F2.

### findings

- **F1 — SOURCE-POLICY RED (undeclared override, relationship-balance basis).** Symptom: two extended policies compute a relationship balance on a basis the base forbids them to change. Root cause: cycle_close (charter lines 2030–2034) and conversion (lines 2205–2209) redefine the sum as four single-row "active" parts of this account, with `overwrite: []`, while base `checking_agg_relationship_balance` (line 938) says "Every checking rule that speaks of a relationship balance uses one basis" and the measure (line 875) sums every non-closed checking/savings/certificate holding and active, delinquent or forbearance mortgages. Demonstrated divergence in one situation: take a customer whose savings account is `dormant` (not closed) with balance 2,847.30 and otherwise the holdings of task 0 after its owed credits (checking 1,944.38; certificate 10,212.64; Interest Checking threshold 15,000): base sum 15,004.32 → waiver met → refund 15.00; extended sum 12,157.02 → refund 0.00. Same pattern for a delinquent mortgage in the conversion. Affected: compute bindings `own_part/savings_part/cd_part/mortgage_part` and rule sentences of both policies. Bears on tasks 0 and 1 (demonstration against each world in the task files).
- **F2 — SOURCE-POLICY RED (dropped branch, conversion gates).** Symptom: the conversion's decision sentence makes the relationship test sufficient. Evidence: line 2210 "When the relationship balance is at or above target_entry_min the tier recorded is Private Client Checking" vs base lines 1828–1831 / 1855. Demonstrated divergence: a customer already holding two Private Client Checking accounts (tier cap 2) with relationship ≥ 250,000: base → conversion refused (breaches checking_agg_multi_holding); extended rule and compute → `Private Client Checking` recorded. Bears on task 1.
- **F3 — SOURCE-POLICY RED (anonymous intermediate object selection).** Symptom: four extended policies replace the base per-item linkage (a fee's own amount and `source_item_id`; a transfer's own counterparty; a dispute's own `disputed_txn_id`; balance at posting against the shortfall) with account-wide proxies (MAX, LATEST, "largest paid check", SUM of submitted disputes, today's balance against the whole item). Demonstrated divergence (transfer_fee): an Everyday Checking account with two transfer fees of 10.00 and 12.00 from an ineligible source: base refunds 10.00 and 12.00 (each "amount equals that fee's amount"); extended refunds 12.00 and 12.00. (uncovered_item): a linked eligible savings that held 500.00 when a check overdrew the account by 386.40 but holds 300.00 today: base — the transfer would have covered the 386.40 shortfall, so the fee is contrary to the charter; extended — 300.00 < item amount, refund 0.00. Bears on task 0 (transfer_fee, autopay) and task 1 (uncovered_item, uncovered_episode).
- **F4 — SOURCE-POLICY RED (rule/compute mismatch, autopay cap).** Evidence: rule line 1984 ("when the disputed item is an ACH debit PCB itself collected … for the owner's PCB auto loan") and lines 1988–1989 ("When the owner has no auto loan paid by autopay from this checking account, the third figure does not apply") vs compute line 2001 `cap: "MX(0, item - scheduled) if scheduled > 0 else item"`. Demonstrated divergence: the disputed item is a 300.00 utility ACH debit, claimed 300.00, owner has an autopay auto loan from this checking with monthly_payment 486.20: rule → the third figure does not apply → 300.00; compute → cap 0.00 → 0.00. Bears on task 0.
- **O3–O8 — observations** (no second answer demonstrable at charter level): O3 transfer_fee compute silent-None branch; O4 autopay `compute_basis.result` spliced quotation; O5 RND is banker's rounding while rules say half-up (no tie reachable with 2-dp inputs); O6 workflow steps' `base_policy_refs` incomplete; O7 declared prerequisite edges narrower than the owed-credits sentences; O8 workflow `order_rationale` and step list encode one world's facts (two transfer fees; fee before dispute deadline) as general text.
- **Workflow shape (check 6) — evaluated in `0.md`**, the task that claims the workflow.

## closing_checklist

Written after both reveals (tasks/0.json revealed 19:07Z, tasks/1.json 19:08Z, both after the 19:06:36Z pre-reveal hash record of this file and the two task files). Nothing above this heading was changed after the reveals.

**Status: NOT CLOSED.** Step 4 requires all three relationships to PASS for every task; they do not:
- task 0 (`0.md`): SOURCE-POLICY RED (charter-global F1, F3, F4; no second answer in its own world) + SOURCE-CHAIN RED (T0-C1, persona) + unique solution PASS.
- task 1 (`1.md`): SOURCE-POLICY RED (charter-global F1, F2, F3; no second answer in its own world) + problem tree PASS + unique solution PASS.

Checklist items, for the record:
- Audit files: `_difficulty.md`, `0.md`, `1.md` correspond one-to-one with tasks 0 and 1; first revision (no older revision exists). Every comparison section is present; not every one carries a PASS (see above).
- Coverage and scope: task 0 `charter_scope` = {transfer_fee_source_error_refund, autopay_dispute_provisional_credit, cycle_close_relationship_refund} + workflow `checking_wf_owed_credits_before_waiver_review` + tools {033d9cbf, 5453b90d, e9518b99}; task 1 `charter_scope` = {uncovered_item_fee_refund, uncovered_episode_extended_fee_refund, private_client_entry_conversion}, no workflow, tools {6b0f4e50, 22b46ecc, 696add48}. Pairwise disjoint over whole problem trees; jointly cover all six extended policies and all six task tools. Exactly one workflow, claimed by task 0 only. Task tools and GT closed (every GT write uses one of the six tools; every tool is used). uuid8s independent (`### action_binding_and_uuids`).
- Problem trees: task 0 — 2 prerequisites, 2 value_input edges, acyclic; task 1 — 2 prerequisites, 2 value_input edges, acyclic. Union of all `prerequisite` edges in the difficulty: two disjoint stars, acyclic, no cross-task edge.
- Workflow shape (check 6): owner=user step absent and `dataflow` empty (T0-W1, T0-W2, observation grade); `requires_external_wait: false` and `zero_wait_proof` present in task 0 `solvability_contract.gold_actions[0..3]`.
- Instantiation-stage gates: not re-run by the auditor (Step 0 assigns the gate runs to the orchestrator). The snapshot supplied with the brief (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire — all OK; check_traceability deferred to KB publication) was taken on the same artifact hashes audited here (charter `e0472aea…`, tools `b8ef3253…`, tasks `83175439…`, `963d1b1b…`). A re-run on the final form is still owed once the reds are addressed.

## revision_2

### charter_global_frozen (revision_2)

- Charter `checking.extended.yaml` sha256 `093543979b98d1ba6fa146289f69770ef81c20357224dc4cf9c21e8ae5901510` (changed from round 1 `e0472aea…`) → every charter-global section is re-derived in full below. `task_tools.py` sha256 `b8ef325356f86f4c55b3a98eed5e600b1ecc8f5c66c05d3be111fdf15da8758f` (unchanged; the tool-contract conclusions of round 1 are carried forward on that hash). Both match the round-2 MANIFEST.
- Round-1 text above is left untouched (hash of this file before this append: `88f8efae…43c2`).
- Written 2026-09-12T19:31Z (UTC) by the same auditor, before any round-2 task JSON was opened. Read: the charter, the round-2 masked views (hashes re-verified: `d0f9ee16…203e`, `6ab1e855…ebf`), `blueprint/products/checking.yaml` (for base-clause verbatim checks). Masked: `tasks/0.json`, `tasks/1.json` (round-2 content), `worklog.md`, other difficulties and scenarios.
- contamination_disclosure (applies to this revision as a whole): the auditor read the round-1 GT of both tasks during round 1 (after the round-1 freeze). Round-1 conventions (read set, identity arguments, statement_cycle convention, round-1 values) are therefore known. The round-2 GT has not been read. The coordinator's message named item ids only, no values.
- Base copy: lines 1–1921 still byte-identical to `blueprint/products/checking.yaml` (`diff` empty).

### policy_conflict_scan (revision_2)

Same six extended policies, same subjects, target tools, `computes` and triggers as round 1; one workflow. Changes that matter:
- Four policies now declare overwrites: autopay (electronic_dispute amount clause), cycle_close and conversion (agg_relationship_balance first sentence), uncovered_item and uncovered_episode (overdraft_protection_transfer coverage clause). Every `superseded_clause` is verbatim in the named base rule and every `replaced_by` is verbatim in the extended rule (substring test).
- The three fee-refund policies now review only "the account's most recently posted" fee of their code and send earlier fees to base `checking_evt_fee_refund`; each refunds "that fee's own amount" and refuses a fee that already has a refund entry.
- The two roots now name their prerequisites by policy id ("the refund of an overdraft transfer fee that checking_ext_transfer_fee_source_error_refund finds charged in error, and every provisional credit that checking_ext_autopay_dispute_provisional_credit finds fallen due"; "the refunds that checking_ext_uncovered_item_fee_refund and checking_ext_uncovered_episode_extended_fee_refund find owed").
- Overlapping `checking_fee_refund` subjects still resolve to distinct fee-code-specific tools; no two extended policies disagree on the same quantity. The two roots share one (now declared) relationship basis. Scope partition from the charter: {transfer_fee, autopay, cycle_close} + workflow vs {uncovered_item, uncovered_episode, conversion}: disjoint and complete.

### rule_compute_equivalence (revision_2)

Every `compute_basis` value is now a verbatim substring of its rule (round-1 O4 closed).
- transfer_fee: fee_id = LATEST overdraft_transfer fee ⇐ "most recently posted overdraft transfer fee"; transfer_id = the fee's source_item_id; source_id = that transfer's counterparty; `source_eligible` None when the source savings is not on record ⇐ "When the source savings account is not on the customer's record, the eligibility condition cannot be established and only the amount condition is judged" (round-1 O3 closed); already_refunded; fee's own amount. Equivalent.
- autopay: dispute_id = LATEST submitted by notice_date; item = the dispute's `disputed_txn_id` row; cap only when that row's counterparty is an autopay auto loan funded from this checking (`CFIELD('auto', …, auto_loan_id=item_counterparty, autopay_enrolled=True, autopay_source_account_id=HID)`) ⇐ "only when the disputed item is a debit whose counterparty is the owner's PCB auto loan with autopay enrolled from this checking account" and "When the disputed item is any other debit, the third figure does not apply" (round-1 F4 closed). **New gap**: dispute_id does not filter on the credit being due, while the rule says the one-at-a-time, latest-first order applies "When more than one submitted dispute on the account is owed a credit" and then states generally "The dispute under review is therefore the account's submitted dispute with the latest notice_date" (finding N1).
- cycle_close: fee_id restricted to `posted_date=NOW` ⇐ "posted on the account on the current business day"; per-status sums (applied/active/dormant savings, applied/active/grace_period certificate, active/delinquent/forbearance mortgage, first row per status via CFIELD) ⇐ the declared replaced_by; already_refunded. Equivalent.
- uncovered_item: fee's own source item; current link and current balance vs whole item (declared); de minimis; already_refunded. Equivalent.
- uncovered_episode: ext fee; opening item identified through the latest overdraft_item fee when `DAYS(od_date, ext_date) == extended_overdraft_trigger_days` ⇐ the new identification sentence; declared coverage test; wrong amount; already_refunded. Equivalent to its own rule (the identification rule is an inference, observation R2-O3).
- conversion: compute still yields the target tier whenever relationship ≥ target_entry_min; the rule now states the inherited gates explicitly ("The other conditions of checking_product_change are inherited unchanged and must also hold … where any of them fails, no conversion is written whatever the relationship balance") and conditions the result on them ("When the inherited conditions hold and …"). The gates are base eligibility (`must_be_active`, `target_entry_gate`) and, as in every other extended compute of this charter, are not encoded in the value formula (observation R2-O2).
- Rounding: rules now say 2-dp inputs need no rounding; RND on 2-dp values is exact (round-1 O5 closed). Vacuous-branch note: with no fee row, uncovered_item evaluates `de_minimis = 1` and uncovered_episode `wrong_amount = 1`, but the result multiplies a 0.00 fee amount (observation R2-O4, no effect).

### action_binding_and_uuids (revision_2)

Tool module unchanged (hash above): six tools, six distinct uuid8s, no eligibility branches — round-1 conclusion carried forward. Workflow: step tools equal the `target_tool` of their `computed_by` policies. Step `base_policy_refs` unchanged and still incomplete (steps 0 and 3 as in round-1 O6; steps 1–2 list only electronic_dispute, which is complete for them) — O6 not closed, as the reworker declares.

### prerequisite_graph (revision_2)

Same four edges (cycle_close → transfer_fee, cycle_close → autopay, conversion → uncovered_item, conversion → uncovered_episode), all value_input on `own_part`, acyclic, no base or self targets. Every `policy_source` is verbatim in its root rule. The edge set now equals what the owed-credit sentences name, because those sentences enumerate the policies by id (round-1 O7 closed). No authoring-viewpoint phrasing in `prerequisite`. Workflow `order_rationale` is now stated in general terms (round-1 O8 addressed; the step list still fixes one transfer refund and two dispute credits, which is inherent to a fixed step list).

### override_declarations (revision_2)

- transfer_fee (`overwrite: []`): base fee_refund "whose amount equals that fee's amount" — FOLLOWED ("at that fee's own amount"); per-transfer source — FOLLOWED (fee → source item → counterparty); earlier fees — deferred to base, no conflict. No undeclared override. Round-1 F3 (transfer part) closed.
- autopay: amount clause DECLARED; disputed item = the dispute's named transaction — FOLLOWED; claimed = that dispute's own claimed_amount — FOLLOWED. Round-1 F3 (autopay part) and F4 closed. New: the latest-notice-first sentence can withhold a due credit (N1).
- cycle_close: agg_relationship_balance first sentence DECLARED; the rest of the base policy (negative balance counts zero; mortgage only for flagged tiers and only active/delinquent/forbearance; card/auto/box never count; measurement date = cycle closing date; pending deposits do not count) is compatible with the replaced_by. Merged semantics unique (the "first on the customer's record" tie-break is the lookup order). Round-1 F1 closed for this policy.
- uncovered_item / uncovered_episode: coverage clause DECLARED (current link, current balance, whole item); item = the fee's own source item — FOLLOWED. Round-1 F3 closed for both.
- conversion: agg_relationship_balance first sentence DECLARED (F1 closed); inherited gates now restated and made necessary in the decision sentence (F2 closed at rule level; compute residue R2-O2).

### findings (revision_2)

Round-1 charter findings: F1 CLOSED, F2 CLOSED (observation residue R2-O2), F3 CLOSED (observation residue R2-O3), F4 CLOSED; O3, O4, O5, O7 CLOSED; O8 ADDRESSED; O6 NOT CLOSED (unchanged, observation).

- **N1 — SOURCE-POLICY RED (new in this revision; rule/compute gap and contradiction with base, autopay dispute selection).** Evidence: rule (charter lines 1986–1991) "A provisional credit owed … is posted … once the dispute is still submitted after its provisional credit deadline. When more than one submitted dispute on the account is owed a credit, they are credited one at a time, the dispute with the latest notice_date first … The dispute under review is therefore the account's submitted dispute with the latest notice_date"; compute line 2004 `dispute_id: LATEST('checking_disputes', 'checking_dispute_id', date_field='notice_date', dispute_status='submitted')` (no due-date filter); base `checking_evt_electronic_dispute` "A provisional credit is owed when the dispute is still submitted once provisional_credit_business_days business days have passed". Demonstrated divergence: an account has dispute A (notice 2026-08-10, due 2026-08-24) and dispute B (notice 2026-08-27, not due until 2026-09-11), frozen date 2026-08-28. Reading 1 (latest-first only among owed disputes): credit A now. Reading 2 (the "therefore" sentence taken as written): the dispute under review is B, which is not owed, so nothing is posted and A's credit, owed under base, is withheld. The compute selects B and outputs B's amount, contradicting both the rule's owed condition and reading 1. Bears on task 0 (its policy); consequence against task 0's world is checked in `0.md` revision_2.
- R2-O2 — observation: conversion compute does not encode the inherited gates (see rule_compute_equivalence).
- R2-O3 — observation: the episode-opening item is inferred from the latest overdraft-item fee posted exactly `extended_overdraft_trigger_days` before the extended fee. On a day with several overdraft items, or where the opening item carried no fee (de minimis), the inferred item may not be the opener. No base sentence identifies the opener, so this is not an override.
- R2-O4 — observation: vacuous `de_minimis`/`wrong_amount` flags when no fee row exists; results stay 0.00.
- R2-O5 — observation: the autopay cap now depends on the ACH debit's `counterparty_account_id` naming the auto loan. The base event text defines that field as "The PCB account on the other side of an internal transfer, otherwise empty", while the share lookup describes it as any "other PCB account (… loan …) on the other side of a transfer". A seed that leaves it empty on an autopay debit (as round 1 did) would switch the cap off.
- Workflow shape: T0-W1 (no owner=user step) NOT CLOSED as declared; T0-W2 re-judged in `0.md` revision_2.

### closure of round-1 items (revision_2, written after the round-2 reveals at 19:33Z)

| Round-1 item | Reworker claim | Auditor verdict |
| --- | --- | --- |
| F1 SOURCE-POLICY RED | closed | CLOSED (declared overwrite in both roots, verbatim, merged semantics unique) |
| F2 SOURCE-POLICY RED | closed | CLOSED at rule level; compute residue R2-O2 (observation) |
| F3 SOURCE-POLICY RED | closed | CLOSED (own-row linkage; coverage deviation declared); residue R2-O3 (observation) |
| F4 SOURCE-POLICY RED | closed | CLOSED |
| T0-C1 SOURCE-CHAIN RED | closed | CLOSED (see `0.md` revision_2) |
| O3, O4, O5, O7 | closed | CLOSED |
| O8 | addressed | ADDRESSED (fixed step count inherent to a workflow) |
| O6 | not closed | **WITHDRAWN** — auditor error in round 1. The instantiate contract requires a step's `base_policy_refs` to list the base policies whose `subject` contains the step's subject. For `checking_fee_refund` those are exactly {checking_evt_fee_refund, checking_evt_electronic_dispute}; for `checking_provisional_credit` exactly {checking_evt_electronic_dispute}. The steps list exactly these. |
| T0-W1 | not closed | NOT CLOSED (observation) |
| T0-W2 | closed | NOT GENUINELY CLOSED (observation R2-T0-W2, see `0.md`) |
| per-task observations | various | see each task file's revision_2 findings |

New in revision_2: **N1 (SOURCE-POLICY RED, charter-global, autopay dispute selection)**; observations R2-O2…R2-O5, R2-T0-O1, R2-T0-W2. Nothing regressed: every round-1 PASS (problem-tree structure, load-bearing edges, zero-wait, tool neutrality, uuid8s, acyclicity, unique solutions) still holds on the round-2 artifacts.

### closing_checklist (revision_2)

**Status: NOT CLOSED** — the charter still carries one SOURCE-POLICY RED (N1), which lies in task 0's claimed policy.
- task 0: SOURCE-POLICY RED (charter-global N1; no second answer in its own world) · problem tree PASS · unique solution PASS.
- task 1: PASS · PASS · PASS.

Checklist items:
- Report files correspond one-to-one with tasks 0 and 1. Round-1 text is preserved above every `## revision_2` heading; pre-append hashes are recorded in each revision_2 header.
- Scope (round-2 `charter_scope`): task 0 = {transfer_fee, autopay, cycle_close} + the workflow + tools {033d9cbf, 5453b90d, e9518b99}; task 1 = {uncovered_item, uncovered_episode, conversion} + tools {6b0f4e50, 22b46ecc, 696add48}. Disjoint, jointly complete, exactly one workflow claimed by exactly one task, every tool used, uuid8s independent.
- Problem trees: each task has 2 prerequisites, 2 value_input edges, acyclic; the union is two disjoint stars.
- Gates: not re-run by the auditor; the orchestrator's post-rework snapshot (all OK, traceability deferred) matches the audited hashes. A re-run on the final form is owed once N1 is resolved.

## revision_3

### charter_global_frozen (revision_3)

- Charter sha256 `6143dfbb5c361d27ff676840872064ab6b67759e62a526165a2fa6368b009fa4` (changed from round 2 `09354397…`) → charter-global sections re-derived. `task_tools.py` `b8ef3253…758f` unchanged → tool-contract conclusions carried forward on that hash. Both match the round-3 MANIFEST.
- Pre-append hash of this file `e8bb4f92…a871`; all earlier text untouched. Base copy (lines 1–1921) still byte-identical to `blueprint/products/checking.yaml`.
- Written before any round-3 task JSON was opened. Same auditor. The round-3 views were verified by hash: task 0 `7c93bd10…4937` (changed), task 1 `6ab1e855…ebf` (identical to round 2).
- contamination_disclosure: the round-1 and round-2 GT of both tasks were read in earlier rounds (after those rounds' freezes). The round-3 GT has not been read.

### what changed in the charter (revision_3)

| Policy | Change |
| --- | --- |
| transfer_fee | `wrong_amount` guarded by `fee_amount > 0` |
| autopay | now applies only when the account has exactly one submitted dispute; with two or more, "the provisional credit on each of them is decided under checking_evt_electronic_dispute alone, and this policy posts nothing"; due-ness inherited explicitly ("never before"); new sentence that an autopay collection for the owner's own PCB auto loan "is a transfer between the owner's PCB accounts, so the debit names that loan as its counterparty"; the latest-notice-first sentence is removed |
| cycle_close | owed credits are now "the refund of every overdraft transfer fee charged in error, the most recent one as checking_ext_transfer_fee_source_error_refund finds it and any earlier one under checking_evt_fee_refund, and the provisional credit that checking_ext_autopay_dispute_provisional_credit finds owed"; fee refunds in posting order, all before the dispute credit; two ledger waivers added (cycle ACH direct-deposit total, cycle debit-card purchase count), `not_offered` excluded |
| uncovered_item | `de_minimis` guarded by `item > 0` |
| uncovered_episode | `wrong_amount` guarded by `ext_amount > 0` |
| conversion | unchanged |
| workflow | four steps: earlier transfer-fee refund (base, `computed_by: []`), most recent transfer-fee refund, one provisional credit, maintenance refund; `dataflow: []` with an explanation that the consumed quantity is the account-record ledger balance |

### policy_conflict_scan / rule_compute_equivalence / override_declarations (revision_3)

- Every `compute_basis` value is verbatim in its rule. Every `superseded_clause` is verbatim in its base policy and every `replaced_by` is verbatim in the extended rule. Every `policy_source` is verbatim in its root rule. All re-checked by substring test.
- **autopay:**
  - The compute gates the result on `submitted_count == 1`. The dispute, claimed amount, item and counterparty are that one dispute's own. The cap is applied only when the item's counterparty is the autopay auto loan funded from this checking.
  - Rule and compute are equivalent. Due-ness is base eligibility (`credit_due`), as for every state_due policy.
  - The declared overwrite now applies only while this policy applies. With two or more submitted disputes, "decided under checking_evt_electronic_dispute alone" leaves the base amount clause in force. The merged semantics are unique through the word "alone" (observation R3-O1).
- **cycle_close:**
  - The ledger-waiver windows use `within_months=1`. That equals "the day after the previous cycle closing date through the current business day" whenever the current business day is the cycle-close day of month, which the rule's trigger requires.
  - The added waivers restate base `checking_evt_maintenance_and_statement_fees` alternatives, with no change of quantity. The remaining base waivers (minimum daily balance, age, military, employee) are deferred explicitly. No undeclared override.
  - The earlier transfer fees are sent to base `checking_evt_fee_refund`. Its bank_error ground ("assessed contrary to the checking charter") together with the unscoped charter sentence "An overdraft protection transfer may be drawn only from a savings account whose savings tier has overdraft_protection_source_eligible true in the savings charter" decides them. There is no compute for that write (observation R3-O2).
- **transfer_fee, uncovered_item, uncovered_episode:** the guards remove the vacuous flags (round-2 R2-O4 closed). Their round-2 conclusions are otherwise unchanged.
- **conversion:** unchanged. R2-O2 (compute omits the inherited gates) remains an observation.
- **Overlapping subjects, scope partition, cross-category reads:** as in revision_2. {transfer_fee, autopay, cycle_close} + workflow vs {uncovered_item, uncovered_episode, conversion}: disjoint and complete.

### prerequisite_graph (revision_3)

Same four value_input edges on `own_part`, acyclic, no base or self targets.

The cycle_close → transfer_fee edge has the condition "Every overdraft transfer fee charged in error on the account has been refunded". Its `policy_source` names both the extended policy (most recent fee) and base `checking_evt_fee_refund` (earlier fees). The node therefore includes one base-governed write, which is allowed because the edge still points at an extended policy.

### findings (revision_3)

| Item | Status |
| --- | --- |
| N1 (SOURCE-POLICY RED) | **CLOSED** — the multi-dispute selection is removed. The policy acts only on a single submitted dispute, and due-ness is inherited unchanged. |
| R2-O4 | CLOSED (guards) |
| R2-O5 | CLOSED — the rule now states that an autopay collection for the owner's own PCB loan is a transfer between the owner's PCB accounts. That is exactly the case the base field text "The PCB account on the other side of an internal transfer" covers. |
| R2-O2 | unchanged, observation |
| R2-O3 | unchanged, observation |
| T0-W1 | NOT CLOSED, observation (as declared) |
| R2-T0-W2 | addressed. `dataflow: []` with an accurate explanation; the dataflow structure cannot express an account-record side effect. Observation. |
| O6 | withdrawn (revision_2) |

New observations:
- **R3-O1 — observation.** The autopay cap now switches on the number of submitted disputes. The same autopay dispute gets 486.20 when it is the only submitted dispute. It gets 972.40 under base alone as soon as a second, unrelated dispute is submitted. With two or more disputes, the cycle_close owed-credit list ("the provisional credit that checking_ext_autopay_dispute_provisional_credit finds owed") names none. Base credits posted that day would still count, because the relationship is taken "after every posting made to the account during that business day". Divergent only in multi-dispute worlds. No contradiction, because "alone" fixes which clause applies.
- **R3-O2 — observation.** Earlier transfer fees have no compute. Their bank-error status is reached through base's generic ground plus the extended policy's unscoped eligibility sentence, while that same policy says it "reviews the account's most recently posted overdraft transfer fee" only. The inference is sound; a reader who takes the eligibility sentence as scoped to the most recent fee would refund nothing for an earlier fee. Bite checked in `0.md` revision_3.

No new SOURCE-POLICY RED found in revision_3.

R3-O2 grading note (same revision, pre-reveal): the scoped reading is not equally defensible. It has to treat a fee charged on a transfer that the charter says "may be drawn only from" an eligible tier as "assessed" in conformity with the charter. That contradicts the base link requirement ("The savings tier must have overdraft_protection_source_eligible true in the savings charter") and the extended policy's own ground for the identical most recent fee. It also makes the root rule's "every overdraft transfer fee charged in error … any earlier one under checking_evt_fee_refund" empty for the most common earlier error. Hence observation, not RED.

### closing_checklist (revision_3, written after the round-3 reveals at 19:52Z)

**Status: CLOSED at the source layer.** Every task now passes all three relationships:
- task 0: policy self-consistency PASS · problem tree PASS · unique solution PASS;
- task 1: PASS · PASS · PASS.

Checklist:
- Report files correspond one-to-one with tasks 0 and 1. Revisions 1–3 are preserved in order; every revision's pre-append hash is recorded; every revision_3 comparison section carries a PASS.
- Scope (round-3 `charter_scope`):
  - task 0: {transfer_fee, autopay, cycle_close} + the workflow + tools {033d9cbf, 5453b90d, e9518b99};
  - task 1: {uncovered_item, uncovered_episode, conversion} + tools {6b0f4e50, 22b46ecc, 696add48}.
  - Pairwise disjoint over whole problem trees and jointly complete over the six extended policies. Exactly one workflow, claimed by task 0 only. Every task tool used by GT. uuid8s independent and frozen.
- Problem trees:
  - task 0: 2 prerequisite problems (N1 resolved by two refunds, N2 by one credit), 2 value_input edges, acyclic;
  - task 1: 2 prerequisites, 2 value_input edges, acyclic;
  - the difficulty-wide edge set is two disjoint stars, no cycle, no cross-task edge.
- Instantiation-stage gates: the orchestrator's post-rework snapshot (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK; traceability deferred to KB publication) was taken on the audited final form (charter `6143dfbb…`, tools `b8ef3253…`, tasks `d370b841…`, `639a9826…`). The auditor did not re-run gates (Step 0 assigns that to the orchestrator). `check_traceability` remains owed after KB publication.

Open observations (not grounds for rework under this skill's RED threshold, recorded for the record):
- T0-W1: the workflow has no owner=user step; the check-6 requirement is unmet, with a blueprint blocker stated in the rationale.
- R2-T0-W2: `dataflow: []`, with an accurate explanation.
- R2-O2: conversion compute omits the inherited gates.
- R2-O3: the episode-opener inference.
- R3-O1: the autopay cap depends on the number of submitted disputes.
- R3-O2: earlier transfer fees are decided by base without a compute.
- R3-T0-O1: the "check the account records" deflection.

## revision_4

### charter_global_frozen (revision_4)

- Charter sha256 `4b7564e615216aefa2faa5f49c79a09d2267e3bb216731a740087aca644ab1ce` (changed from round 3 `6143dfbb…`) → charter-global sections re-derived in full. `task_tools.py` `b8ef3253…758f` unchanged → tool conclusions carried forward on that hash. Both match the round-4 MANIFEST. Base copy still byte-identical to `blueprint/products/checking.yaml`.
- Pre-append hash of this file `8cf052d6…3035`; earlier revisions untouched.
- Written before any round-4 task JSON was opened. Same auditor.
- contamination_disclosure:
  - The round-1 to round-3 GT of both tasks was read in earlier rounds.
  - Before writing this revision, and as directed by the coordinator, the auditor read the render-layer audit reports `audits/policy_kb/checking_fees_overdraft_and_disputes/0.md` and `1.md`. They quote scored values and five source-layer problems, P1–P5.
  - This revision is therefore not blind. It verifies P1–P5 and re-checks the rest of the charter.

### relation to revision_2 / revision_3 (auditor miss, recorded honestly)

Under the self-consistency criterion, an `overwrite` retires its base clause for the whole charter, so every retirement must leave the whole domain governed. On that criterion the charters of rounds 2 and 3 carried three SOURCE-POLICY REDs that this audit did not record:
- P1: the universal relationship-balance clause was retired while each replacement covered only its own determination. The ordinary cycle-close waiver, the Private Client opening test and the Private Client downgrade were left without a basis.
- P2: the base transfer-coverage clause was retired with replacements scoped to refund decisions, leaving live transfers without a coverage condition.
- P3: the two-or-more-disputes branch was delegated to a base policy whose only amount clause the overwrite retires. Revision_3 graded this as observation R3-O1, reasoning that the word "alone" restored the base clause; that reasoning did not hold under this criterion.

The revision_2 closure of F1 ("declared, merged semantics unique") and the revision_3 verdicts "policy self-consistency PASS" for both tasks were therefore wrong at charter level. The per-task scored answers were not affected: all three gaps were untriggered in both worlds. P4 and P5 below were also not raised by this audit before.

### P1–P5 verification (revision_4)

| Item | Verdict | Evidence |
| --- | --- | --- |
| **P1** relationship-balance basis | **CLOSED** | Both overwrites of the `checking_agg_relationship_balance` first sentence now open their `replaced_by` with "Outside the determinations of checking_ext_cycle_close_relationship_refund and checking_ext_private_client_entry_conversion, every checking rule that speaks of a relationship balance keeps the one basis, the measure checking_msr_relationship_balance: …" and then give their own determination's basis. See the domain sweep below. |
| **P2** transfer coverage for live transfers | **CLOSED** | Both overwrites of the transfer clause now begin "Outside the refund decisions of checking_ext_uncovered_item_fee_refund and checking_ext_uncovered_episode_extended_fee_refund, an overdraft protection transfer is made only if the savings current_balance at that moment covers the whole shortfall, and a partial transfer is never made." Live transfers, and base refund decisions on earlier fees, keep the base condition. |
| **P3** amount for two or more submitted disputes | **CLOSED** | The autopay `replaced_by` now reads "On an account with two or more disputes in submitted status, the provisional credit amount of each dispute stays the dispute's claimed_amount, but never more than the disputed item's amount. On an account with exactly one submitted dispute, …". Every count of submitted disputes has an amount rule, and the rule's "decided under checking_evt_electronic_dispute alone" now lands on a live clause. |
| **P4** "every" vs most-recent-only | **CLOSED** | The conversion rule now reads "the refund of every overdraft item fee and every extended overdraft fee charged in error on the account, the most recent of each as checking_ext_uncovered_item_fee_refund and checking_ext_uncovered_episode_extended_fee_refund find them and any earlier one under checking_evt_fee_refund, is posted first". That is the new `policy_source` of both edges, so the conditions "Every … charged in error" now match their source. The cycle_close root was already worded this way for transfer fees. |
| **P5** once-per-cycle conversion limit | **CLOSED** | The rule adds "The checking records keep no dated history of conversions apart from the account's current tier, so the once-per-cycle limit is judged on the conversions recorded during the current contact together with any the owner reports having made earlier in the cycle; when neither shows one, the limit holds." The limit is now decidable from reachable evidence (the contact's own writes and a caller statement); this is an evidence rule, not a change to the base limit. |

Whole-domain sweep for the retired relationship-balance clause. Every base rule that speaks of a relationship balance now has exactly one basis:

| Rule | Basis |
| --- | --- |
| `checking_agg_relationship_balance` (the remaining sentences) | measure |
| `checking_open_and_funding` (Private Client opening test) | measure |
| `checking_evt_maintenance_and_statement_fees`, ordinary cycle-close waiver and any later-questioned fee | measure |
| cycle_close (same-day questioned fee) | its declared basis |
| `checking_product_change`, downgrade after 3 cycles and non-Private-Client conversions | measure |
| conversion (Private Client entry test) | its declared basis |

Whole-domain sweep for the retired transfer clause:

| Case | Condition |
| --- | --- |
| Live transfers | base at-the-moment / shortfall condition |
| Refund decisions of the two extended policies (most recent fee) | declared current-link / current-balance / whole-item test |
| Base `checking_evt_fee_refund` decisions on earlier fees | base condition (outside the two extended decisions) |

### rule_compute_equivalence / action_binding / prerequisite_graph (revision_4)

- Every `compute_basis` value, `superseded_clause`, `replaced_by` and `policy_source` is verbatim (substring test).
- Computes unchanged from round 3. The autopay `claim_part` basis now quotes the exactly-one sentence, and the compute's `submitted_count == 1` gate matches the rule.
- Tools unchanged; six distinct uuid8s. The workflow is unchanged: T0-W1 still has no owner=user step, and `dataflow: []` with its explanation.
- Graph unchanged: four value_input edges on `own_part`, acyclic. Conditions agree with the widened sources (P4).
- No authoring-viewpoint wording found.

### findings (revision_4)

No SOURCE-POLICY RED remains in the round-4 charter. Observations:

- **R4-O1 — boundary between the restored basis and the scoped determinations.**
  - For a same-day questioned maintenance fee, the proposition "the relationship waiver was met for this cycle" can be evaluated on two bases:
    - the base cycle-close waiver clause with the measure (which, as restored, applies to "every checking rule" outside the extended determination);
    - cycle_close's own narrower basis. Because the extended basis sums a subset of the measure's holdings, its value is never above the measure's.
  - In a world where the extended sum is below the threshold and the measure's is at or above it (for example a second active savings account), base maintenance's "A fee assessed although a waiver was met is a bank error and is refunded under checking_evt_fee_refund" would favour a refund; cycle_close refunds nothing.
  - Graded as not an equally defensible second answer. cycle_close claims the judgement of that waiver for that fee ("When an owner questions a monthly maintenance fee dated the current business day … the relationship waiver of the tier is judged on …"). Its closing carve-out sends only "the remaining waivers of the tier" back to base, so base does not re-decide the relationship waiver for that fee.
  - The same structure holds for the transfer coverage test: the extended policies claim the refund decision on the most recent fee, and the goodwill-only fallback excludes a base bank-error re-decision.
  - Untriggered in both worlds, where each holding is single and both bases coincide.
- **R4-O2 — earlier overdraft-item and extended fees.** They are decided under base with the restored at-the-moment / shortfall condition. The extended policies justify their own test by saying those inputs "are not carried on the checking record". They can be reconstructed from the savings ledger (`find_savings_transactions`), so the base test stays decidable. Untriggered: one fee of each kind in task 1.
- **R3-O1 remainder.** With two or more submitted disputes, cycle_close's owed-credit list ("the provisional credit that checking_ext_autopay_dispute_provisional_credit finds owed") names none. The base credits then owed would still count if posted that day, because the relationship is taken "after every posting made to the account during that business day". Observation, untriggered.
- **Carried observations:** R2-O2, R2-O3, R3-O2, T0-W1, R2-T0-W2.

### closing_checklist (revision_4, written after the round-4 reveals at 21:39Z)

**Status: CLOSED at the source layer.**
- task 0: PASS · PASS · PASS;
- task 1: PASS · PASS · PASS.
- The round-4 charter carries no SOURCE-POLICY RED. P1–P5 are closed, and every retired base clause now leaves its whole domain governed (sweeps in `### P1–P5 verification (revision_4)`).
- The revision_3 closure is superseded: it was reached without the whole-charter retirement criterion and missed P1–P3 (see `### relation to revision_2 / revision_3`).

Checklist:
- Report files map one-to-one to tasks 0 and 1. Revisions 1–4 are preserved, each with its pre-append hash.
- Scope unchanged from revision_3: disjoint, jointly complete, one workflow claimed by task 0, all six tools used, uuid8s independent.
- Problem trees unchanged: 2 prerequisites and 2 value_input edges each, acyclic; the difficulty-wide edge set is two disjoint stars.
- Gates: the orchestrator's post-rework snapshot (all OK) matches the audited hashes (charter `4b7564e6…`, tools `b8ef3253…`, tasks `0fe61049…`, `3a33e709…`). The auditor did not re-run the gates.
- The render layer must re-render and re-audit the three retired-clause documents: the restored "outside" sentences and the ≥2-dispute amount are new source atoms.

Open observations (not grounds for rework under the RED threshold): R4-O1, R4-O2, R3-O1 remainder, R3-O2, R2-O2, R2-O3, R3-T0-O1, T0-W1, R2-T0-W2.

## revision_5

Auditor: a new, independent auditor session (Claude, erl-task-policy-audit, re-audit round 5). It has no link to the auditor of revisions 1–4 and did not write any of the audited artifacts. Revisions 1–4 above are left exactly as they were.

### charter_global_frozen

- Freeze time: 2026-09-13T17:4xZ (the three revision_5 frozen blocks were all on disk by 17:50:16Z, per `date -u` run straight after the last append). Everything in this `charter_global_frozen` block was written before either task's masked fields were read and before any earlier revision or KB-audit report was opened.
- Inputs, with hashes checked against the orchestrator's `MANIFEST.sha256`:
  - `checking.extended.yaml` sha256 `f1179eda9d5beaf994e433a2b6850a01fe9a923df775f9f89efbd3fb8566b923`
  - `task_tools.py` sha256 `b8ef325356f86f4c55b3a98eed5e600b1ecc8f5c66c05d3be111fdf15da8758f`
  - `blueprint/products/checking.yaml` sha256 `635b57c4…6046`; `blueprint/products/savings.yaml` sha256 `8f308ff1…a40a`
  - `task_0.masked.json` `664748699b2c…7e63b4` (from 0.json `a6dea81a…2d85`); `task_1.masked.json` `354bee71a0ba…b991c2` (from 1.json `d7593431…de6a`)
- Fields read: blueprint.yaml, db_schema.json, share_tools.py, products/{checking,savings}.yaml (savings only for `overdraft_protection_source_eligible`), the lifecycle state lists of products/{cd,mortgage,auto}.yaml, the extended charter, task_tools.py, the masked views (`frozen_time`, `user_scenario`, `initial_state` only), `erlbench/scoring.py`, the compute evaluator in `skills/erl-task-instantiate/scripts/check_compute.py` (used only for DSL semantics), and the instantiate skill's workflow template (`references/product_extended.yaml`, lines 200–275).
- Fields masked and left unread until the freeze: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, every earlier revision of these audit files, and `audits/policy_kb/`.
- Why this section is re-derived in full: the rework changed the root rules, so the charter hash almost certainly differs from the one revision 4 recorded. The brief also asks for a fully independent pass. So nothing here is carried forward.

#### policy_conflict_scan

- **Base copy.** Lines 1–1922 of the extended charter (everything before `extended_policies:`), diffed against `blueprint/products/checking.yaml`, match except for one trailing blank line. The base section is a verbatim copy.
- **Claimed objects.** There are 6 extended policies, 1 workflow and 6 task tools. Each `(target_tool, computes)` pair belongs to exactly one policy:
  - `checking_ext_transfer_fee_source_error_refund` → `refund_transfer_fee_error_033d9cbf` / amount
  - `checking_ext_autopay_dispute_provisional_credit` → `post_dispute_provisional_credit_5453b90d` / amount
  - `checking_ext_cycle_close_relationship_refund` → `refund_same_day_maintenance_fee_e9518b99` / amount
  - `checking_ext_uncovered_item_fee_refund` → `refund_uncovered_overdraft_fee_6b0f4e50` / amount
  - `checking_ext_uncovered_episode_extended_fee_refund` → `refund_extended_overdraft_fee_22b46ecc` / amount
  - `checking_ext_private_client_entry_conversion` → `convert_checking_tier_696add48` / variant_name
- **Overlapping subjects.** All five refund and credit policies write `checking_fee_refund` or `checking_provisional_credit`. Each one is restricted by fee code, or by the dispute, to a different object:
  - most recent `overdraft_transfer` fee
  - the single submitted dispute
  - the `monthly_maintenance` fee posted on NOW
  - most recent `overdraft_item` fee
  - most recent `extended_overdraft` fee

  Every tool hard-codes its own `fee_code`. So no two policies can decide the same row. Base `checking_evt_fee_refund` still governs the *earlier* fees of each code, and each ext rule says so in its first sentence. That is a partition, not a conflict.
- **Triggers and time anchors.**
  - Credit-due and notice-window timing is inherited unchanged from base `checking_evt_electronic_dispute` (policy 2: "Whether and when the credit is owed is inherited unchanged").
  - The extended-overdraft episode anchor is inherited from `checking_evt_extended_overdraft_fee`.
  - The relationship-balance measurement date matches base `checking_agg_relationship_balance` (cycle closing date for a waiver, frozen date for a conversion). The only change is the composition, which is declared (see override_declarations).
  - No two policies set different anchors for the same quantity.
- **Cross-category reads.** Savings: `overdraft_protection_source_eligible` (tier parameter), `current_balance`, `status`. CD and mortgage: `principal_balance`, `status`. Auto: `monthly_payment`, `autopay_enrolled`, `autopay_source_account_id`. Every read goes into a checking write only. No write crosses into another category.
- **Scope exclusivity and completeness, inferred from the charter alone since `charter_scope` is masked.** The prerequisite graph has two components:
  - {`cycle_close_relationship_refund` → `transfer_fee_source_error_refund`, `autopay_dispute_provisional_credit`}. The workflow's `computed_by` union is exactly these three policies.
  - {`private_client_entry_conversion` → `uncovered_item_fee_refund`, `uncovered_episode_extended_fee_refund`}.

  Together the two components cover all 6 policies, and they share no node. The actual `charter_scope` fields are compared after the reveal.
- **Cross-component coupling (reworker flag 1).** Both root rules define "a credit the bank already owes" in general terms:
  - Policy 3: "any fee refund due on the bank_error ground or as a dispute_final refund, whatever the fee and whichever policy decides it, and any provisional credit that has fallen due on a submitted dispute, whichever policy sets its amount".
  - Policy 6: "a fee refund the bank owes on the bank_error ground or as a dispute_final refund, of any fee and under whichever policy decides it, or a provisional credit that has fallen due on a submitted dispute, however its amount is set".

  So policy 3's rule also reaches refunds decided by policies 4/5, and policy 6's rule reaches credits decided by policies 1/2. Neither root declares an edge to the other component. As charter text this is an under-declared general dependency (finding C-O1). Whether it bites is purely a question of each world; that is checked per task.

#### rule_compute_equivalence

Every binding was checked against its `compute_basis` quotation and the rule, both directions. DSL semantics come from `check_compute.build_env`:
- SUM, COUNT and LATEST are scoped to the holding.
- CPARAM and CFIELD filter on `customer_id = owner` and return the first match.
- `within_months=1` means `MONTHS(date, NOW) == 0`.

- **transfer_fee_source_error_refund.**
  - `fee_id`, `transfer_id`, `source_id`, `already_refunded` and `result` each map to a quoted clause.
  - `source_eligible` is CPARAM on the savings tier. It returns None when the source is not the owner's, which leaves only `wrong_amount` live. That is exactly the rule's "When the source savings account is not on the customer's record … only the amount condition is judged".
  - `wrong_amount` uses `P('overdraft_transfer_fee')`, the tier on the frozen date, where the rule says only "the checking tier's". This makes a difference only if the tier changed between the fee and the review (C-O3).
  - No invented basis. No empty promise.
- **autopay_dispute_provisional_credit.**
  - `submitted_count`, `dispute_id`, `claimed`, `item_id`, `item` and `item_counterparty` are all quoted.
  - `scheduled` = CFIELD auto `monthly_payment` with `auto_loan_id = counterparty`, `autopay_enrolled = True`, `autopay_source_account_id = HID`. That implements "the owner's PCB auto loan with autopay enrolled from this checking account".
  - `cap = MX(0, item − scheduled)` when a scheduled payment exists, else `item`. That implements "never less than zero" and "When the disputed item is any other debit, the third figure does not apply".
  - `result` = the minimum of the figures that apply when exactly one dispute is submitted, else 0 ("this policy posts nothing").
  - The due and notice gates stay as base eligibility (trigger `state_due`), not compute. That is consistent.
- **cycle_close_relationship_refund.**
  - `fee_id` is restricted to `posted_date = NOW`.
  - `own_part = MX(0, F('ledger_balance'))` is read at handling time. That implements "after every posting made to the account during that business day, and before the refund of the maintenance fee itself posts".
  - The savings/cd/mortgage status lists match the rule. Taking the first CFIELD match per status implements "only the first on the customer's record is counted".
  - The ledger waivers are guarded for `not_offered`.
  - `within_months=1` equals the rule's cycle ("day after the previous cycle closing date through the current business day") whenever NOW is the cycle closing date and the cycle day exists in both months. It can drift for cycle days 29–31 (C-O4).
  - `threshold` has no `not_offered` guard. For Access or Student Checking (`waiver_relationship_balance: not_offered`) the comparison `relationship >= 'not_offered'` is undefined, whereas the rule says a not_offered waiver "is not used" (C-O2).
  - `inputs.history` lists only the `debit_card_pos` count, while compute also counts `debit_card_international` (declaration omission, C-O4).
- **uncovered_item_fee_refund.** Every binding is quoted. `covered` applies the declared override: current link, current `current_balance` compared with the whole item. `de_minimis` is `0 < item ≤ overdraft_item_de_minimis`. `result` is correct.
- **uncovered_episode_extended_fee_refund.** Every binding is quoted. `opens_episode` requires `DAYS(od_date, ext_date) == extended_overdraft_trigger_days`, which implements "posted exactly … calendar days before". `covered` is gated on `opens_episode`, and `wrong_amount` is independent of it. That implements "otherwise … only the amount ground below is judged".
- **private_client_entry_conversion.** `own_part`, `savings_part`, `cd_part` and `mortgage_part` (gated on `K('target_includes_mortgage')`) are all quoted. `result` = `target_tier` when relationship ≥ `target_entry_min`, else the current tier ("nothing is written"). The inherited gates (active, age, tier cap, multi-holding, once per cycle) are eligibility, not compute. The params `target_entry_min` 250000.00 and `target_includes_mortgage` true equal Private Client Checking's `entry_relationship_balance_min` and `relationship_balance_includes_mortgage`.

#### action_binding_and_uuids

- Each task tool is owned by one target policy. The one tool shared with a base-ground decision is `refund_transfer_fee_error_033d9cbf`: workflow step 0 uses it with `computed_by: []` to refund an earlier transfer fee under base `checking_evt_fee_refund`. That is the same business event (`checking_fee_refund`, bank_error, `fee_code overdraft_transfer`), so there is one business reading.
- Function bodies: every tool writes exactly its documented rows. The provisional-credit tool also sets `dispute_status = provisional_credited`, which is base semantics. No tool checks eligibility, status, amount, earlier refunds or qualification. All six docstrings say so. No confirmation, wait or review step is added.
- uuid8s: `5453b90d`, `033d9cbf`, `e9518b99`, `6b0f4e50`, `22b46ecc`, `696add48`. They are pairwise distinct, share no prefix or suffix, and show no sequence. They look independently generated.
- All six tools are `owner="agent"`. The module has no `owner="user"` tool (bears on W-1).

#### prerequisite_graph

- `prerequisite` is present on all 6 policies and on the workflow. Policies 1, 2, 4 and 5, and the workflow, have `[]`. Policy 3 → {policy 1, policy 2}. Policy 6 → {policy 4, policy 5}. No edge points at a base policy or at itself. The graph is acyclic. Adding the undeclared cross-component links of C-O1 (3→4, 3→5, 6→1, 6→2) would still be acyclic, because 1, 2, 4 and 5 have no out-edges.
- `policy_source` quotes, each located verbatim in the cited rule:
  - 3→1: "the refund of every overdraft transfer fee charged in error, the most recent one as checking_ext_transfer_fee_source_error_refund finds it and any earlier one under checking_evt_fee_refund" (rule lines 2051–2053).
  - 3→2: "the provisional credit that checking_ext_autopay_dispute_provisional_credit finds owed" (line 2053).
  - 6→4 and 6→5: "the refund of every overdraft item fee and every extended overdraft fee charged in error on the account, the most recent of each as … find them and any earlier one under checking_evt_fee_refund" (line 2303).
- `condition` wording: each condition ("Every … charged in error on the account has been refunded before …" / "The provisional credit that has fallen due … has been posted before …") says the same as the rule's "every credit the bank already owes on the account is posted first". It is neither strengthened nor weakened. The 3→1 condition covers every erroneous transfer fee, including earlier ones that base decides. The rule sentence does too, so this is not a strengthening by the field.
- `kind` and `gate`: all four edges are `value_input` with gate `own_part`, and `own_part` exists as a compute binding in both roots. `resolved_by` names the target tool of the cited policy. Each such tool raises `ledger_balance` by the amount posted, which makes `effect` ("raises the account's ledger balance, so own_part … rise") hold.
- No authoring-viewpoint wording ("in this task", "at the opening") appears in any prerequisite entry.

#### override_declarations

Sentence by sentence against each `base_policy_refs` entry:
- **policy 1 (transfer_fee_source_error_refund), `overwrite: []`.**
  - `checking_evt_fee_refund`: full refund, bank_error, no time limit, refund once. All followed.
  - `checking_evt_overdraft_protection_transfer`, "The savings tier must have overdraft_protection_source_eligible true": followed and restated as a draw restriction.
  - `checking_evt_electronic_dispute`: no overlapping quantity.
  - Dropped-branch check: the base bank_error grounds for a transfer fee also include "beyond … daily max". Policy 1's selector judges only ineligible-source and wrong-amount, then says "otherwise this policy refunds nothing". The phrase "this policy" leaves base in force, so that is coexistence, not a replacement (C-O5).
- **policy 2 (autopay_dispute_provisional_credit).** The one base sentence it replaces ("The provisional credit amount is the dispute's claimed_amount, but never more than the disputed item's amount.") is declared. `replaced_by` covers both the ≥2-submitted and =1-submitted branches, so the merged amount is unique. Every other `checking_evt_electronic_dispute` sentence (channels, notice window, business-day due date, new-account substitution, submitted only, one credit, reversal, dispute_final) is inherited.
- **policy 3 (cycle_close_relationship_refund).**
  - Replaces the basis sentence of `checking_agg_relationship_balance`. Declared.
  - Remaining `checking_agg_relationship_balance` sentences followed: measurement at close of business on the cycle closing date, negative counted as zero, mortgage only when the tier flag is true, pending deposits excluded.
  - `checking_evt_maintenance_and_statement_fees`: waivers are alternatives, not prorated, not_offered unusable, "A fee assessed although a waiver was met is a bank error". Followed. The other waivers are left to base by name.
  - `checking_evt_fee_refund`: bank_error, full refund, once. Followed.
  - No anonymous factor or 0/1 multiplier replaces a base-fixed amount: the refund is the fee's own amount or nothing, which is base's rule.
- **policy 4 (uncovered_item_fee_refund).**
  - Replaces "the transfer is made only if the savings current_balance at that moment covers the whole shortfall, and a partial transfer is never made." for its refund decision (current link, whole item). Declared.
  - `checking_evt_overdraft_and_returned_item_fees`: "a covered item is not an overdraft and carries no overdraft-item fee", de minimis. Followed.
  - Base bank_error grounds not in its selector (daily limit, end-of-day de minimis, wrong amount): coexistence (C-O5).
- **policy 5 (uncovered_episode_extended_fee_refund).** Same declared replacement as policy 4, applied to the item that opened the episode. `checking_evt_extended_overdraft_fee`: episode anchored on `negative_since_date`, posted at +trigger days, once per episode. Followed. Wrong-amount ground kept.
- **policy 6 (private_client_entry_conversion).**
  - Replaces the `checking_agg_relationship_balance` basis sentence. Declared.
  - `checking_product_change`: active, target entry gate except deposit, multi-holding, no fee, once per cycle. All inherited. The added evidence rule for once-per-cycle ("judged on the conversions recorded during the current contact together with any the owner reports") supplies an evidence source; it changes no quantity.
  - `checking_open_and_funding`: age and relationship entry gates inherited.
- **Author "wrong value" signals.** None of the rules or bases calls base's output a wrong value.
- **Result.** No undeclared override was found. Every declared override leaves a unique merged meaning.

#### findings

- **C-O1 (observation; bears on tasks 0 and 1).** The general definition of "credit the bank already owes" in both roots reaches policies claimed by the other task, with no `prerequisite` edge (quotes above). In any world where such a credit exists, the tree read from the policy would be larger than the declared one and would cross task scopes. A consequence can only be shown against a world, so each task file checks whether those links are empty.
- **C-O2 (observation; no task bears it).** Policy 3's `threshold` has no `not_offered` guard. Compute is undefined for tiers that do not offer the relationship waiver (Access, Student).
- **C-O3 (observation).** Policy 1's `wrong_amount` compares against the tier on the frozen date. Base service fees use the tier in force on the day of service. This diverges only after a tier change.
- **C-O4 (observation).** Policy 3's `within_months=1` stands in for the statement cycle and can drift for cycle days 29–31. Policy 3's `inputs.history` omits the `debit_card_international` count.
- **C-O5 (observation).** In policies 1, 4 and 5, "otherwise this policy refunds nothing" leaves base bank_error grounds for the same most-recent fee (daily-limit, end-of-day de minimis, and for policy 1 the transfer-fee daily max) outside the ext selector. "This policy" keeps base in force, so the pair is coexistence, not an undeclared override. A demonstration needs a world where such a ground fires on the most recent fee; each task file checks this.
- **W-1 (check 6, owner=user clause: FAIL — recorded as a standing non-conformance observation, not a RED).**
  - Check 6 and the instantiate template (`references/product_extended.yaml`: "at least one step must be `owner: user`") require a customer-owned workflow step. The workflow has four `owner: agent` steps, and its `order_rationale` says "The procedure has no customer-owned step because none of its postings is an owner's consent or claim under the checking charter". task_tools.py declares no `owner="user"` tool.
  - The failure is shown verbatim. But no second answer, unmet prerequisite or scored-value change follows from it, so under the consequence table it cannot be raised to a RED. It needs an orchestrator ruling. `check_extended` does not test this clause (`no_handoff=True` concerns handoff GT only).
- **W-2 (check 6, dataflow; observation).** `dataflow: []` while step 3 consumes the ledger balance raised by steps 0–2. The template's link kinds (object_binding into an action argument, state_effect as an eligibility status) cannot name a side-effect balance, and the `order_rationale` says this explicitly. The ordering 0–2 before 3 is carried by the rule text instead.
