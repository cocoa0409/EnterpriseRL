# Policy-task audit — savings_withdrawals_interest_and_transfers / charter-global

## charter_global_frozen

- Auditor: independent policy-task auditor (erl-task-policy-audit), round 1. I did not write any of the audited artifacts.
- Freeze time: 2026-09-12T19:37Z (drafted); the authoritative freeze is the sha256 record taken at 19:4xZ before any reveal. This section was written before any task's GT was revealed, and nothing in it comes from a revealed GT.
- Frozen inputs (sha256):
  - `tasks/savings_withdrawals_interest_and_transfers/savings.extended.yaml` = `26300564d03f2e7a00b63b752049cc3c2fba64211efe4d90eee2cf947e9fd163` (matches the orchestrator MANIFEST)
  - `tasks/savings_withdrawals_interest_and_transfers/task_tools.py` = `0dcd69b75a2da73abf72b39f783f7027648136094347479a1eac25045f9fff46` (matches MANIFEST)
  - `blueprint/products/savings.yaml` = `8f308ff1…a40a`; `blueprint/share_tools.py` = `7b7ec28e…5d87`; `blueprint/db_schema.json` = `e5cf164d…a7a`; `blueprint/blueprint.yaml` = `61655924…54a`
- Fields I read: the whole extended charter, `task_tools.py`, the blueprint (`blueprint.yaml` difficulty entry, `share_tools.py`, `db_schema.json`, `products/savings.yaml`, plus `products/cd.yaml` and `products/checking.yaml` only as cross-category inputs to my own compute replay), runtime `erlbench/` (engine, scoring, db, tools), and the compute DSL evaluator `skills/erl-task-instantiate/scripts/check_compute.py` (`build_env` / `eval_compute`). For tasks I read only the masked views: `frozen_time`, `user_scenario`, `initial_state`.
- Fields masked and unread at this freeze: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`, and any earlier audit.
- Entry conditions (Step 0): the brief supplied the gate snapshot (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding and check_cross_fire, all exit 0, with their OK lines). check_traceability is deferred until the KB is published; I record that as stated, not as a missing input. The masked views and their hashes were supplied, and I re-hashed them: `task_0.visible.json` = `311ec093…608b` and `task_1.visible.json` = `5267267b…a824`, both matching. Input is complete.
- Base copy: `diff <(head -1250 savings.extended.yaml) <(head -1250 blueprint/products/savings.yaml)` differs only by one trailing blank line (line 1250). The base section is a verbatim copy.

### policy_conflict_scan

The structured policy has 13 base policies, 6 extended policies and 1 workflow. Where subjects overlap:

| Subject | Policies writing or deciding it | Compatible? |
|---|---|---|
| `savings_withdrawal` | base `savings_evt_withdrawal_allowance`, `savings_evt_closure`; ext `savings_ext_certificate_proceeds_transfer` (amount of an owner-instructed telephone transfer) | Yes. Ext decides only the amount, caps it at the balance (which matches base `covered_by_balance`), and says "subject to every rule of savings_evt_withdrawal_allowance on the day it posts". |
| `savings_fee` (excess_withdrawal) | base `savings_evt_withdrawal_allowance`; ext `savings_ext_counted_withdrawal_fee_assessment` | Yes in the final state. Ext reconciles by count ("fees due" − "fees standing") where base works per withdrawal. The rule text itself makes the two agree: ext requires every erroneous fee to be refunded before owed fees are counted (see findings O-3 and O-4). |
| `savings_fee_refund` | base `savings_evt_fee_refund`; ext `savings_ext_linked_waiver_maintenance_refund` (maintenance, bank_error) and `savings_ext_certificate_funding_fee_refund` (excess fee on a certificate-funding internal transfer, bank_error) | Yes. The two ext policies have disjoint fee codes and disjoint tools (`bf99bb2f` writes fee_code monthly_maintenance, `774e6cc0` writes excess_withdrawal). Both are strict instances of base's bank_error ground ("assessed contrary to the savings charter"). |
| `savings_change_product` | base `savings_product_change`; ext `savings_ext_best_money_market_conversion` | Yes. Ext adds the choice of target tier and the "balance after every refund owed" timing. It inherits every other entry gate verbatim ("every other entry-gate item … is inherited unchanged"). |
| `savings_set_automatic_transfer` | base `savings_evt_automatic_transfer`; ext `savings_ext_overdraft_replenishment_transfer` | Yes. Ext computes only the amount and raises it to `automatic_transfer_min_amount`, matching base `minimum_amount`. Ownership, active status and day 1–28 are inherited. |
| `savings_reactivate` | base `savings_evt_dormancy` (workflow step 1, `computed_by: []`) | Yes. |

- Time anchors: the only time-anchor drift I found is O-1 below (linked-checking waiver "at cycle close" versus the current checking record).
- Cross-category read boundaries: every ext policy reads only fields its `cross_category.reads` declares (cd `certificate_id`/`payout_account_id`/`status`; checking `variant_name`/`status`/`checking_account_id`/`overdraft_link_savings_account_id`). All of these can be reached through the share finders `find_cd_certificates` (by `payout_account_id`/`customer_id`) and `find_checking_accounts` (by `customer_id`/`overdraft_link_savings_account_id`).
- Terminal states: no two policies write the same field with different values on the same trigger.
- **Scope exclusivity / completeness, derived from the charter's prerequisite graph alone and to be confirmed against `charter_scope` after the reveal:** the graph splits into two disjoint connected components. Component A is {`certificate_proceeds_transfer`, `linked_waiver_maintenance_refund`, `best_money_market_conversion`} plus workflow `savings_wf_dormant_account_wakeup_and_upgrade`, whose steps use exactly A's three tools plus `reactivate_savings_account_bfe70db1`. Component B is {`certificate_funding_fee_refund`, `counted_withdrawal_fee_assessment`, `overdraft_replenishment_transfer`}. With M = 2, if each task claims one component, the scopes are pairwise disjoint and jointly cover all 6 extended policies and the single workflow.
- Claimed event types not covered by any task tool: `savings_interest_credit` and `savings_close` are in the blueprint claim, but no extended policy or task tool writes them. This is an observation, not a defect of the three relationships (O-9).

### rule_compute_equivalence

For every binding I checked, the `compute_basis` sentence occurs verbatim in the policy's `rule` (whitespace-normalised substring test: 0 misses). Bindings that have no `compute_basis` entry are all trivial parameter reads or arithmetic whose sentence is quoted on a neighbouring binding: `linked_tiers`, `at_min` (linked-waiver); `cur` (conversion); `chans`, `counted`, `free`, `standing` (assessment); `need` (replenishment). This is an observation (O-8), not a gap.

DSL semantics I relied on (from `check_compute.build_env`):
- `CFIELD(cat, field, **eq)` returns the field of the **first** matching cross holding of the customer.
- `LATEST` keeps the first row among ties on `date_field`.
- `SUM` rounds to 2 dp.
- `RND` is Python `round(x, 2)`, not a decimal half-up. Every RND input in this charter is already a 2-dp sum or parameter, so no value can differ.

Per policy:

1. `savings_ext_certificate_proceeds_transfer`
   - `cd_id` = CFIELD cd by `payout_account_id=HID`, from "The certificate is the one whose payout account on the certificate record is this savings account."
   - `cd_in` = SUM of deposits with `channel='internal_transfer'` and counterparty cd_id. The rule states that all certificate postings are internal transfers.
   - `cd_back` = SUM of withdrawals with counterparty cd_id, any channel ("every withdrawal already sent … to that same certificate").
   - `net_cd` = MX(·, 0) ("a difference below zero is taken as zero").
   - `result` = min(net_cd, current balance), rounded.
   - Reverse sweep: every compute step has a rule sentence. The rule's "subject to every rule of savings_evt_withdrawal_allowance" is an inheritance, not an empty promise, because an excess fee would be a separate base write. Equivalent.
2. `savings_ext_linked_waiver_maintenance_refund`
   - `cyc` = statement_cycle of the latest monthly_maintenance fee.
   - `fee_amt` = that cycle's fee amount.
   - `linked_ok` = first active checking tier ∈ `waiver_linked_checking_tiers` (not_offered → False).
   - `at_ok` = automatic_transfer deposits of cyc ≥ `waiver_automatic_transfer_min` (not_offered → False).
   - `result` = fee if either, else 0. Equivalent, subject to O-1 (time anchor) and O-2 (first-row CFIELD against "an active checking account").
3. `savings_ext_best_money_market_conversion`
   - The ladder PCMM → PMM → MMA stops at the current tier.
   - K params (25000 / 10000 / 2500, and 'Private Client Checking') equal the variants' `minimum_opening_deposit` and `entry_required_checking_tiers`.
   - The rule's "every other entry-gate item … including the per-tier account cap … is inherited unchanged" is not evaluated in compute, but the rule reads it as inherited eligibility, not as part of the computed selector (O-2).
4. `savings_ext_certificate_funding_fee_refund`
   - `cd_id` = first active certificate.
   - `fund_wd` = latest internal_transfer withdrawal to cd_id.
   - `counted_flag` = `'internal_transfer' in channels` (False for all six tiers).
   - `fee_amt` = excess fee whose source is fund_wd.
   - Equivalent.
5. `savings_ext_counted_withdrawal_fee_assessment`
   - `cyc` = cycle of the latest overdraft_transfer to the checking account that names this savings as its OD source.
   - `n_*` = per-channel counts gated on the tier list.
   - `n_od` = OD transfers to that checking account, gated on `overdraft_transfer_counts_toward_limit`.
   - `due_fees` = MN(MX(counted − free, 0), cap), with 0 when unlimited.
   - `standing` = excess fee rows − bank_error excess-fee refunds in cyc.
   - `result` = fee if owed ≥ 1.
   - Equivalent for the amount. The rule's "on the earliest counted withdrawal beyond the allowance, in posting order, that carries no standing fee" fixes the `source_item_id`, which no compute binding carries. The number of rows when owed ≥ 2 is also rule-only (O-5).
6. `savings_ext_overdraft_replenishment_transfer`
   - Same cycle selector.
   - `od_total` = OD transfers of cyc to that checking account.
   - `fees_net` = MX(excess fee amounts − excess-fee refund amounts in cyc, 0).
   - `result` = max(rounded need, `automatic_transfer_min_amount`).
   - Equivalent. Its "fees standing" subtracts **all** excess-fee refunds by amount, while the assessment's "fees standing" subtracts only **bank_error** refunds by count (O-6).

### action_binding_and_uuids

| target_tool | computes | claimed by |
|---|---|---|
| `transfer_savings_to_checking_5f60835b` (user) | amount | `savings_ext_certificate_proceeds_transfer` only |
| `refund_savings_maintenance_fee_bf99bb2f` (agent) | amount | `savings_ext_linked_waiver_maintenance_refund` only |
| `convert_savings_tier_d500151b` (agent) | variant_name | `savings_ext_best_money_market_conversion` only |
| `refund_savings_withdrawal_fee_774e6cc0` (agent) | amount | `savings_ext_certificate_funding_fee_refund` only |
| `assess_savings_withdrawal_fee_aafc1fb2` (agent) | amount | `savings_ext_counted_withdrawal_fee_assessment` only |
| `set_savings_automatic_transfer_e1e909eb` (user) | automatic_transfer_amount | `savings_ext_overdraft_replenishment_transfer` only |
| `reactivate_savings_account_bfe70db1` (agent) | — | workflow step 1, `computed_by: []` |

- Each `(target_tool, computes)` pair is claimed by exactly one policy.
- Docstrings match the policy's subject and add no confirmation, review or wait. The refund tools say "dated today" and give `statement_cycle` as "the cycle in which the refund posts", which matches the base event field "Statement cycle in which the refund posted". The assess tool gives "the month in which the cycle of the withdrawal closes".
- uuid8s: `5f60835b`, `bfe70db1`, `bf99bb2f`, `d500151b`, `774e6cc0`, `aafc1fb2`, `e1e909eb`. All seven are distinct. None is a copy of another with a changed tail. There is no common prefix, sequence or adjacency pattern; the only shared leading pair is `bf` in `bfe70db1`/`bf99bb2f`, which is chance-level (about 8% over 21 pairs), and their remaining six characters are unrelated. Reuse in other difficulties is outside my read domain and was not checked.
- Tool bodies (`task_tools.py`, whole file): no function checks status, balance, verification, prior refunds or any policy value. Each performs one `ctx.create`/`ctx.update` from its arguments (plus a balance update). The runtime (`erlbench/engine.py`) enforces only the unlock/call flow, and scoring (`erlbench/scoring.py`, `db.py:80`) is a sort_keys hash of the final DB. So the tool layer judges no prerequisite, and write order matters only through final values.

### prerequisite_graph

- Every ext policy and the workflow has a `prerequisite` key. The empty ones are certificate_proceeds_transfer, linked_waiver_maintenance_refund, certificate_funding_fee_refund and the workflow.
- Edges:
  1. conversion ← linked_waiver_maintenance_refund, `value_input`, gate `bal`
  2. conversion ← certificate_proceeds_transfer, `state_gate`, gate `savings_product_change.must_be_active`
  3. assessment ← certificate_funding_fee_refund, `value_input`, gate `voided`
  4. replenishment ← assessment, `value_input`, gate `fees_net`
  5. replenishment ← certificate_funding_fee_refund, `value_input`, gate `fees_net`
- Every `problem` is an ext policy id in this file. None is a base id and none is a self-reference. The graph is acyclic: topological orders are {transfer, refund_m} → conversion and refund_x → assessment → replenishment.
- `policy_source`: all five occur verbatim in the citing policy's `rule` (substring test True ×5).
- `condition` against the cited sentence: no strengthening or weakening. Edge 1 says "Every fee refund owed" where the rule says "every refund owed"; the only refunds this charter defines are fee refunds, so the two are equivalent.
- `kind`/`gate`: `bal`, `voided` and `fees_net` are real bindings in the citing compute, and `must_be_active` is a real eligibility id of `savings_product_change`.
- `resolved_by`/`effect`: edges 1, 3, 4 and 5 name the tool that writes the row the gate reads. Edge 2 names the transfer tool, but the transfer by itself leaves `status` dormant. The state that satisfies `must_be_active` is written by `reactivate_savings_account_bfe70db1`, which no ext policy owns, so it cannot be a `problem`. The edge's effect says the transfer "lets the dormant account be reactivated, after which savings_accounts.status is active", and the quoted rule sentence itself names both acts ("made a customer-initiated transaction … and the account has been reactivated"). No passage reaches a contrary conclusion, so this is observation O-7. The same edge also has an undeclared value effect: the transfer lowers `bal` (O-7).
- Authoring-viewpoint wording: none of "in this task / at the opening / the current world" appears. Edge 3's effect "owed rises from zero to the missing fee" is phrased for one particular world state (owed = 0 and a fee missing) rather than generally. No contrary conclusion follows, so this is observation O-7.

### override_declarations

Every ext policy has `overwrite: []`. Sentence by sentence against each `base_policy_refs` entry:

- **certificate_proceeds_transfer** vs `savings_evt_withdrawal_allowance`:
  - status active/dormant: inherited.
  - covered by balance: ext caps at the balance, so the declined branch can never arise. Compatible.
  - Branch/ATM not counted, telephone_banking counted: inherited.
  - Excess fee beyond free, cap, one-per-withdrawal, tier on posted_date, wire fees, daily limits (telephone is not "online or mobile"): inherited by "subject to every rule".

  Against `savings_evt_closure`: the closure-only sentences (request row, confirmation, OD unlink, early fee, accrued interest, payout) are not triggered, because this is not a closure. **No undeclared override.**
- **linked_waiver_maintenance_refund** vs `savings_evt_fee_refund`:
  - "refunded in full … one row whose source_item_id is the fee": followed.
  - bank_error ground "a maintenance fee in a cycle where a waiver was met": followed for two waivers. The other three waivers are expressly delegated back ("outside this policy … decided under savings_evt_maintenance_and_statement_fees and savings_evt_fee_refund"), so the `else 0` branch is a scope boundary, not a 0/1 multiplier on base.
  - no time limit / not counted toward courtesy: followed.
  - courtesy gates: not applicable.
  - "at most once": inherited (not re-evaluated in compute).

  Against `savings_evt_maintenance_and_statement_fees`: "The tier used is the variant_name at cycle close" and "an active checking account … held by the same customer at cycle close" are handled by a compute that reads the **current** tier (`P`) and the **current** checking record (`CFIELD … status='active'`). The rule sentence says "holds" without an anchor, but it opens by referring back to the base waiver "for the statement cycle the fee belongs to". This is a potential anonymous time-anchor drift (O-1). Its consequence can only show in a world where the checking tier or status, or the savings tier, changed between that cycle's close and the handling time. Each task file checks this against its own world.
- **best_money_market_conversion** vs `savings_product_change`:
  - "keeps number, balance, history; changes only variant_name": followed.
  - "must be active": followed and sharpened.
  - "entry gate … except the opening deposit; the current balance must be at least the target tier's minimum_opening_deposit": followed. "Current balance" is pinned to "after every refund owed has posted", which is a timing refinement: base pins no order relative to refunds, so there is no base sentence it contradicts.
  - "No fee", "ends promo", "does not restart early closure", "one per cycle": followed or inherited. **No undeclared override.**
- **certificate_funding_fee_refund** vs `savings_evt_fee_refund` / `savings_evt_withdrawal_allowance`: internal_transfer is in no tier's `excess_withdrawal_counted_channels`, so a fee on it is contrary to the charter under base. Refund in full, bank_error, no time limit, and posted in the current cycle all follow the base event field meaning. **No undeclared override.**
- **counted_withdrawal_fee_assessment** vs `savings_evt_withdrawal_allowance`:
  - (a) Base counts "rows with channel overdraft_transfer" of any counterparty. Ext counts only OD transfers to the checking account that names this savings. This is a narrowing, with a consequence only if a savings account funds OD transfers to two checking accounts.
  - (b) Base caps by `savings_msr_cycle_excess_fees` (all excess fee rows). Ext caps "fees due" and nets bank_error refunds out of "standing". The difference shows only near the 6-fee cap.
  - (c) Base is per-withdrawal ("each counted withdrawal beyond … incurs … whose source_item_id is that withdrawal"). Ext is count-based and ordered after the erroneous-fee refund. Evaluated before its own prerequisite, the ext formula can report 0 owed where base reports a fee owed on a specific withdrawal. The ext rule forbids that evaluation ("Before the fees owed are counted, every … fee … assessed contrary to the charter must already have been refunded"), so when the rule is followed both give the same row (O-3, O-4).
  - Against `savings_evt_maintenance_and_statement_fees`, `savings_evt_dormancy`, `savings_evt_closure`: no sentence is contradicted. From closure, "a payout never counts" is consistent with "internal transfers never count".
  - Findings (a) and (b) are undeclared narrowings, and each task file tests them against its world.
- **overdraft_replenishment_transfer** vs `savings_evt_automatic_transfer`: ownership and active status, minimum amount (ext raises to it), day 1–28, business-day roll, posting and skip mechanics, and stop semantics are all inherited ("follow savings_evt_automatic_transfer unchanged"). **No undeclared override.**

### findings

Charter-global findings. Each names the tasks it can affect; the consequence is demonstrated only in those task files.

- **O-1 (observation unless a task world shows a consequence): linked-checking waiver time anchor.**
  - Symptom: the base waiver is "an active checking account of a tier listed in waiver_linked_checking_tiers held by the same customer at cycle close" and "The tier used is the variant_name at cycle close". The ext `linked_ok` reads `CFIELD('checking','variant_name', status='active')` and `P('waiver_linked_checking_tiers')` at the handling time.
  - Root cause: the compute has no cycle-close anchor.
  - Consequence: it would diverge only if the checking holding or the savings tier changed after the fee's cycle close.
  - Affected: `savings_ext_linked_waiver_maintenance_refund.compute[chk_tier, linked_tiers]`.
  - Bears on: task 0.
- **O-2 (observation): CFIELD first-row semantics against "an active checking account".**
  - The rule wording "holds an active checking account whose tier is one of the listed tiers" (linked-waiver) and "holds an active checking account of … Private Client Checking" (conversion) is existential, but `CFIELD` tests only the first active checking row. `CFIELD('cd', …, status='active')` ("the customer's active certificate") presumes a single active certificate in the same way.
  - The conversion compute also does not evaluate the inherited tier cap or age gate.
  - Consequence: it would diverge only for a customer with several active checking accounts or certificates, or at a tier cap.
  - Bears on: tasks 0 and 1 (to be checked against each world).
- **O-3 (observation): the assessment's opening-world value is 0 by construction.** Evaluated on a world that still carries the erroneous fee, `standing` counts it, so `owed` = 0. The rule's own justification says "a fee assessed contrary to the charter does not stand", and base per-withdrawal semantics say a fee is owed on the withdrawal beyond the allowance. The ext rule removes the tension by ordering the refund first. Bears on: task 1 (edge 3's opening-state judgement).
- **O-4 (observation): undeclared narrowings (a) and (b) in `counted_withdrawal_fee_assessment`**, listed above under override_declarations. Bears on: task 1.
- **O-5 (observation): the fee row's `source_item_id` and the row count for owed ≥ 2 are fixed by rule text only.** Same-day posting-order ties are unspecified. Bears on: task 1.
- **O-6 (observation): "fees standing" is defined twice.** The assessment uses excess fee rows − **bank_error** refunds, by count. The replenishment uses excess fee amounts − **all** excess-fee refunds, by amount. The two differ only when a courtesy_waiver refund of an excess fee is in the cycle. Bears on: task 1.
- **O-7 (observation): prerequisite-edge wording.**
  - Edge 2's `resolved_by` is the enabling transfer, not the status-writing reactivation.
  - Edge 2 carries an undeclared value effect on `bal`.
  - Edge 3's effect "owed rises from zero to the missing fee" is phrased for a particular world.
  - Workflow `dataflow` declares 0→1 (posted_date → reactivation_date) and 1→3 (status → must_be_active), but not the balance flows 0→3 and 2→3 that the conversion's `bal` consumes.
  - Bears on: task 0 (and task 1 for the edge 3 wording).
- **O-8 (observation):** 8 trivial bindings have no `compute_basis` key. See rule_compute_equivalence.
- **O-9 (observation):** claimed event types `savings_interest_credit` and `savings_close` have no task tool in this difficulty. The base-level inconsistency "automatic transfer deposits: `savings_evt_automatic_transfer` says channel automatic_transfer, while the `savings_deposit` trigger maps them to channel internal_transfer" sits in the verbatim base copy and is not this difficulty's to answer. Neither task's world contains an automatic-transfer deposit.
- **Workflow shape (charter half; the per-task half is in the task that claims it):**
  - Exactly one workflow, with 4 synchronous write steps (transfer [user], reactivate, refund, convert), so ≥ 4 non-trivial writes and ≥ 1 `owner=user` step.
  - Dataflow 0→1 corresponds verbatim: the tool returns `posted_date` and the consumer arg is `reactivation_date`.
  - The `order_rationale`'s placement of reactivate before refund ("so that the reactivation rests on that transaction alone and not on any bank-posted credit") rests on no policy sentence. No policy makes the refund's value or the reactivation date depend on that adjacency. Whether this can change a terminal state is checked in the task file (the scoring hash is order-insensitive for identical writes).
  - `requires_external_wait: false` / `zero_wait_proof` live in the task's masked `solvability_contract.gold_actions` (per `skills/erl-task-instantiate/references/task.json`), not in the charter. They are checked after the reveal.

No charter-global `SOURCE-POLICY RED` was found. Each task file must still test O-1 through O-7 against its own world.

## closing_checklist

This section was written after both tasks were revealed (2026-09-12T19:43Z) and both comparisons were complete. Nothing above this heading was edited after the reveal.

- **Audit files.** There is one file per task: `0.md` for task 0 and `1.md` for task 1, with `_difficulty.md` alongside. This is round 1, so no earlier revision exists. The pre-reveal freeze hashes are recorded in each task's `source_gt_comparison`. Both comparison sections carry PASS on all three relationships:
  - task 0: SOURCE-POLICY PASS, SOURCE-CHAIN PASS, SOURCE-TASK PASS
  - task 1: SOURCE-POLICY PASS, SOURCE-CHAIN PASS, SOURCE-TASK PASS
- **Coverage and disjointness.** The two tasks' `charter_scope` values are disjoint and together cover all 6 extended policies and the only workflow:
  - task 0: {certificate_proceeds_transfer, linked_waiver_maintenance_refund, best_money_market_conversion} + workflow `savings_wf_dormant_account_wakeup_and_upgrade`, with tools {5f60835b, bfe70db1, bf99bb2f, d500151b}
  - task 1: {certificate_funding_fee_refund, counted_withdrawal_fee_assessment, overdraft_replenishment_transfer}, workflows [], with tools {774e6cc0, aafc1fb2, e1e909eb}

  Each task's scope covers its whole problem tree, root and prerequisites. These scopes match the two components I derived from the prerequisite graph alone before the reveal (§ policy_conflict_scan).
- **Workflow.** Exactly one workflow exists and exactly one task (task 0) claims it. Its gold_actions carry `requires_external_wait: false` and a `zero_wait_proof` on all four workflow steps.
- **Tools and GT closed.** All 7 task tools are called in GT (4 in task 0, 3 in task 1), each once, and every extended policy is computed in exactly one task. The uuid8s are independent and not batch-derived (§ action_binding_and_uuids).
- **Problem trees:**
  - Task 0 has 2 prerequisites (1 value_input, 1 state_gate) and is acyclic.
  - Task 1 has 2 prerequisite problems and 3 value_input edges, and is acyclic.
  - The difficulty-wide `prerequisite` graph (5 edges, all inside one component each) is a DAG with no cross-task reference.
- **Gates.** The orchestrator re-ran the instantiation-stage gates on exactly the audited forms, and all were green: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK and SCOPE OK (brief snapshot); check_traceability is deferred until the KB is published. At 2026-09-12T19:44:49Z the artifacts' sha256 still equalled the MANIFEST values (`savings.extended.yaml` 26300564…, `task_tools.py` 0dcd69b7…, `tasks/0.json` ac2b0b5a…, `tasks/1.json` 549fec62…), so that snapshot applies to the final form. I did not run the gates myself, because Step 0 has the auditor cite the gates rather than run them, and running them could write outside my domain.
- **Open observations** (not grounds for rework): O-1 through O-9 above, T0-O1 through T0-O6 in `0.md`, and T1-O1 through T1-O6 in `1.md`. Two of them concern structure rather than wording:
  - In both tasks the root's scored value on the opening world equals gold (T0-O1, T1-O1). Discrimination rests on the prerequisite writes and the gate, which the final-state hash scores.
  - In task 1 the persona has no courtesy-waiver branch (T1-O2).

**Difficulty verdict: passes the source-layer audit.** Policy self-consistency, problem tree and unique solution all PASS for both tasks.

## revision_2

### charter_global_frozen (revision_2)

- Auditor: the same independent policy-task auditor, round 2 re-audit. Drafted 2026-09-12T21:3xZ. The authoritative freeze is the sha256 record taken before the round-2 GT reveal, cited in each task's revision_2 comparison.
- Inputs re-hashed at 2026-09-12T21:32:40Z:
  - `savings.extended.yaml` = `c5f246ba790b4b39ecd2fc8ec6e6b262bd7e78a146db902cf1ddb35a33c60e11`. It **changed** since round 1 (`26300564…`), so every charter-global section below is **re-derived in full**, not carried forward.
  - `task_tools.py` = `0dcd69b7…ff46` (unchanged).
  - blueprint `products/savings.yaml` `8f308ff1…`, `share_tools.py` `7b7ec28e…`, `db_schema.json` `e5cf164d…`, `blueprint.yaml` `61655924…` (all unchanged).
  - Round-2 views match the MANIFEST: `task_0.visible.json` `311ec093…` (unchanged), `task_1.visible.json` `89e3ac50…` (changed).
- Base copy: `diff <(head -1249 savings.extended.yaml) blueprint/products/savings.yaml` shows no difference. It is verbatim.
- Entry conditions: the orchestrator supplied a post-rework gate snapshot (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE, all OK and exit 0) and rebuilt masked views with hashes. The input is complete.
- **Criterion applied in this revision.** The coordinator stated the self-consistency criterion for this round: two quoted passages reach different conclusions in the same situation, **including a constructed one**. In round 1 I required the consequence to be demonstrated in a task's own world and recorded constructed-only divergences as observations (O-1…O-9). This revision applies the stated criterion to every charter item. Where it re-grades a round-1 observation, the round-1 text is left untouched and the re-grade is recorded here.
- **contamination_disclosure (charter half).** Before this revision I had seen the round-1 GT of both tasks (`evaluation_criteria`, `computations`, `prerequisite_closure`, `design_rationale`, as recorded in round 1). I have **not** yet read the round-2 task JSONs or the KB audit reports under `audits/policy_kb/…`; I will read them only after this section and both task derivations are on disk. Nothing in this section rests on any GT: it is derived from the charter, the tool module, the blueprint and the DSL evaluator alone.

### policy_conflict_scan (revision_2)

- Subjects and overlaps are unchanged from round 1 (same 6 ext policies, same targets, same workflow).
- Ext-side changes found by reading the new ext section in full:
  - (a) `linked_waiver_maintenance_refund`:
    - declares 2 `overwrite` entries (linked-waiver "at cycle close" → "as they stand when the refund is decided"; "The tier used is the variant_name at cycle close." → "the account's tier as it stands when the refund is decided");
    - adds the proviso "opened on or before the posted date of the fee under review";
    - the linked-waiver compute is now per listed tier (`lk_access … lk_private`);
    - restates the automatic-transfer waiver as the cycle sum, with "a single automatic transfer of at least that amount therefore meets it on its own".
  - (b) `best_money_market_conversion`: the Private Client Checking test is now existential (`pc_chk = CFIELD(…, variant_name=K('pcmm_required_checking'), status='active')`, `pc_ok = pc_chk != None`).
  - (c) `certificate_funding_fee_refund`: the certificate is now identified from the counterparty of the latest internal-transfer withdrawal (`fund_cp`, `cd_id = CFIELD(… certificate_id=fund_cp)`) instead of "the customer's active certificate".
  - (d) `counted_withdrawal_fee_assessment`:
    - declares an `overwrite` of base's cap clause;
    - `n_od` counts overdraft transfers "whichever checking account they covered";
    - adds "a fee refunded as a courtesy … still stands for this count".
  - (e) `overdraft_replenishment_transfer`:
    - the trigger now says "in a statement cycle", with "it is the current statement cycle whenever an overdraft protection transfer has posted in the current cycle, and otherwise the last cycle in which one posted";
    - renames its quantity "the withdrawal fees the account bears";
    - states that a courtesy refund also reduces it, "unlike the count of fees standing".
  - (f) The workflow `order_rationale` now says refund and reactivation "commute, so no policy outcome depends on their relative order".
- The scope split derived from the prerequisite graph is unchanged: component A (proceeds, linked-waiver refund, conversion, workflow) and component B (funding refund, assessment, replenishment).

### rule_compute_equivalence (revision_2)

- Mechanical check: every `compute_basis` sentence is a whitespace-normalised substring of its rule, **except** `counted_withdrawal_fee_assessment.compute_basis.charged`. The basis ends "…does not stand." where the rule now reads "…does not stand; a fee refunded as a courtesy…". The difference is punctuation only (R2-O4).
- Bindings without a basis: `cur`, `chans`, `counted`, `standing`, `need`, all trivial.
- `free` is quoted with the cap sentence rather than the allowance sentence (R2-O4).
- DSL semantics are as in round 1: `CFIELD` returns the **first** matching cross holding in record order, and `LATEST` keeps the first row among equal dates.

Per policy, each tested against constructed situations:
1. **proceeds transfer (unchanged).** `cd_id = CFIELD('cd','certificate_id', payout_account_id=HID)` is a first-row lookup. The rule says "the money that one of their certificates of deposit paid into it" and "The certificate is the one whose payout account on the certificate record is this savings account." See R2-1.
2. **linked-waiver refund.**
   - `fee_date` / proviso: equivalent.
   - `lk_*`: for each listed tier, `CFIELD('checking','opened_date', variant_name=X, status='active')` takes the **first** active account of that tier and tests its opened_date. The rule says "at least one checking account that is active and whose tier is one of the listed tiers, provided that this checking account was opened on or before the posted date". See R2-2.
   - `at_total`/`at_ok`: equivalent to the rule and to base `savings_msr_cycle_automatic_transfer_total`, subject to the base channel contradiction in R2-5.
3. **conversion.** `pc_ok` is now existential, so round-1 O-2's checking-row half is **closed**. The tier-cap half is not: see R2-3.
4. **funding refund.**
   - `fund_cp` → `cd_id` (exact id) → `fund_wd` → `fee_amt`: equivalent. When the latest internal transfer went elsewhere, `cd_id` is None and so is `fund_wd`, and `fee_amt` = 0, matching "nothing is refunded".
   - The first-row certificate lookup of round 1 is **closed**.
   - Same-day ties on "most recent" are unresolved by the records (R2-O2).
5. **assessment.**
   - `n_od` now matches base (every overdraft_transfer row), so round-1 O-4(a) is **closed**.
   - The cap is applied to `due_fees` under a declared overwrite (round-1 O-4(b) **closed**; see override_declarations).
   - `voided` counts bank_error refunds only, and the courtesy clause matches.
   - `chk_id` and `cyc` remain first-row lookups of "the checking account that names this savings account": see R2-4.
6. **replenishment.**
   - `cyc`: its rule now matches the compute ("current statement cycle whenever an overdraft protection transfer has posted in the current cycle, and otherwise the last cycle in which one posted"), so the KB item about the "current statement cycle" trigger is **closed**.
   - `fees`/`refunds`/`fees_net`: every excess-fee refund of any ground is subtracted, as the rule says "whatever its ground".
   - `chk_id` / `od_total` "to that checking account": see R2-4.

### action_binding_and_uuids (revision_2)

Unchanged inputs (`task_tools.py` hash equal), and the (target_tool, computes) pairs in the yaml are unchanged. The round-1 section is carried forward by reference on the grounds of those two facts:
- each pair is claimed once;
- the 7 uuid8s are distinct and not batch-derived;
- no tool body checks a prerequisite.

### prerequisite_graph (revision_2)

- The 5 edges are unchanged in endpoints, kind and gate.
- Every `policy_source` is a verbatim substring of its rule; this includes the replenishment edges' new wording "The fees the account bears are counted only after …".
- The graph is acyclic.
- Edge 3's effect is now general ("voided counts each bank_error refund of the cycle's excess fees, so every refunded erroneous fee drops out of standing and owed rises by one for it wherever the fees due exceed the fees that still stand"), so the round-1 O-7 world-specific wording is **closed**.
- Two items remain unchanged and no passage contradicts them, so they stay observations (R2-O1):
  - edge 2 still names the transfer tool as `resolved_by`;
  - the workflow `dataflow` still omits the balance flows 0→3 and 2→3.

### override_declarations (revision_2)

- **linked-waiver refund.** Both superseded clauses occur verbatim in base `savings_evt_maintenance_and_statement_fees`, and both `replaced_by` texts occur verbatim in the ext rule. The merged semantics: the linked waiver is met when an active checking account of a listed tier (current records), opened on or before the fee's posted date, exists. Waiver parameters are taken from the savings tier at refund time. This is one reading, so it is unique.
  - Constructed check: a checking account at an unlisted tier at cycle close is upgraded to a listed tier afterwards. The merged charter now refunds as bank_error a fee that was correct when assessed. The overwrite declares exactly that substitution, and the rule states why ("The checking records keep only each account's current tier and status"). Declared, one answer, so **closed** (round-1 O-1). The residual is R2-O3.
- **assessment.** The superseded clause "until savings_msr_cycle_excess_fees reaches excess_withdrawal_fee_max_per_cycle, after which further counted withdrawals in the cycle are paid without a fee." occurs verbatim in base `savings_evt_withdrawal_allowance`.
  - Constructed check: 6 fee rows are already posted in the cycle, one of them erroneous and later refunded, and ≥ 7 counted withdrawals exceed the allowance. Base: the cap is reached, so no further fee. Ext: standing 5 < due 6, so one fee is owed. The overwrite names exactly this clause, and one merged answer remains, so **closed** (round-1 O-4(b)).
- **Auto-transfer waiver wording (KB item).** Base `parameter_schema.waiver_automatic_transfer_min` says "An automatic transfer from checking of at least this amount posted in the cycle waives the maintenance fee". Base rule and ext use the cycle sum.
  - Constructed check: two automatic transfers of 15.00 each against a minimum of 25.00. The parameter description states a *sufficient* condition and says nothing either way about several smaller transfers. The base rule and the ext rule both give "met", and the ext rule states it outright: "several smaller ones meet it when together they reach it".
  - No passage reaches "not met", so this is **closed**.
- **proceeds transfer, funding refund, conversion, replenishment**: `overwrite: []`. A sentence-by-sentence sweep against each `base_policy_refs` entry found nothing new beyond round 1. No undeclared override.

### findings (revision_2)

Each item gives the verdict under the stated criterion, the two quoted passages, the constructed situation, and the tasks whose claimed policies carry it.

- **R2-1 — SOURCE-POLICY RED (charter; residual of round-1 O-2): certificate lookup in `savings_ext_certificate_proceeds_transfer`.**
  - Passage A (rule): "When the owner asks to move out of a savings or money market account the money that one of their certificates of deposit paid into it … The certificate is the one whose payout account on the certificate record is this savings account."
  - Passage B (compute): `cd_id: "CFIELD('cd','certificate_id', payout_account_id=HID)"`, which returns the first such certificate in record order.
  - Constructed situation: the customer holds two certificates whose `payout_account_id` is this savings account (the CD charter permits this; nothing in the savings or CD charters limits it to one). The owner asks for the money of the one listed second.
  - Conclusions: A gives the named certificate's net payouts. B gives the first-listed certificate's.
  - Root cause: the rule's definite description presupposes uniqueness, and the compute resolves it by record order.
  - Affected: `extended_policies[savings_ext_certificate_proceeds_transfer].compute[cd_id]` and rule sentence 2. Bears on **task 0**.
- **R2-2 — SOURCE-POLICY RED (charter; residual of round-1 O-2): first row per tier in the linked-checking test.**
  - Passage A (rule): "the customer holds at least one checking account that is active and whose tier is one of the listed tiers, provided that this checking account was opened on or before the posted date of the fee under review".
  - Passage B (compute): `lk_premier: "('Premier Checking' in linked_tiers) and ((CFIELD('checking','opened_date', variant_name='Premier Checking', status='active') or '9999-12-31') <= fee_date)"`, and likewise for each tier.
  - Constructed situation: the savings tier is Money Market Account (listed tiers Premier Checking and Private Client Checking). The customer holds two active Premier Checking accounts, which the checking charter allows (`max_accounts_per_customer_this_tier: 2` for Premier). The one first in record order was opened after the fee posted; the other was opened years before. There is no automatic-transfer waiver.
  - Conclusions: A gives met, so a bank_error refund of the full fee. B gives `lk_premier` False, `linked_ok` False, result 0.
  - Affected: `compute[lk_access … lk_private]`. Bears on **task 0**.
- **R2-3 — SOURCE-POLICY RED (charter; residual of round-1 O-2, second half): inherited tier cap absent from the conversion selector.**
  - Passage A (rule): "the target tier is chosen from the top of the money market ranks downward and the first tier the account qualifies for is the target … every other entry-gate item of savings_product_change, including the per-tier account cap of savings_agg_multi_holding, is inherited unchanged". This is read with base `savings_product_change`: "The customer must meet the target tier's entry gate on the conversion date, including entry_required_checking_tiers and savings_agg_multi_holding".
  - Passage B (compute): `result` selects 'Private Client Money Market' whenever `pc_ok and bal >= 25000`, with no cap term.
  - Constructed situation: the customer already holds 2 open Private Client Money Market accounts (tier cap 2) and asks to move a third account (Money Market Account, balance 30,000.00, active Private Client Checking) up.
  - Conclusions: A says PCMM does not qualify, so the target is Premier Money Market (Premier cap not reached). B gives PCMM, which the inherited gate then forbids: either no conversion or a different tier, but never B's value.
  - Affected: `extended_policies[savings_ext_best_money_market_conversion].compute[result]`. Bears on **task 0**.
- **R2-4 — SOURCE-POLICY RED (charter; residual of the round-1 first-row class, not previously itemised for this lookup): "the checking account that names this savings account as its overdraft protection source".**
  - Passage A (assessment and replenishment rules): "the most recent withdrawal with channel overdraft_transfer whose counterparty is the checking account that names this savings account as its overdraft protection source". The replenishment trigger adds "puts back what overdraft protection took from the savings account in a statement cycle".
  - Passage B (both computes): `chk_id: "CFIELD('checking','checking_account_id', overdraft_link_savings_account_id=HID)"` (first row), then `cyc` and `od_total` filtered on `counterparty_account_id=chk_id`.
  - Constructed situation: two checking accounts of the customer both name this savings account as their source. `checking_evt_overdraft_protection_transfer` says only "A checking account may name one savings account as its overdraft protection source", which does not bar two checking accounts naming the same savings account. Account #1 (first in record order) last drew an overdraft transfer last cycle; #2 drew three this cycle.
  - Conclusions: A takes the most recent overdraft transfer to a checking account naming this savings account, so the current cycle and #2's transfers. B takes #1, so the previous cycle, a different `cyc`, `od_total`, fee reconciliation and monthly amount.
  - Affected: `savings_ext_counted_withdrawal_fee_assessment.compute[chk_id, cyc]` and `savings_ext_overdraft_replenishment_transfer.compute[chk_id, cyc, od_total]`. Bears on **task 1**.
- **R2-5 — SOURCE-POLICY RED (charter; root cause in the verbatim base copy, i.e. blueprint `products/savings.yaml`; round-1 O-9 re-graded): the recorded channel of an automatic-transfer deposit.**
  - Passage A (base `savings_evt_automatic_transfer`): "On the transfer day the transfer posts as a savings_deposit with channel automatic_transfer". Base measure `savings_msr_cycle_automatic_transfer_total` reads "savings_deposit rows with channel automatic_transfer", and so does the ext linked-waiver rule and compute (`at_total … channel='automatic_transfer'`).
  - Passage B (base `events[savings_deposit].triggers`): `{event: "checking:checking_debit", when: {channel: automatic_transfer}, map: {…, channel: internal_transfer, …}}`. The value is a literal: `checking_transactions` has no field named internal_transfer, and the checking charter's trigger maps use literals the same way, e.g. `map: {channel: bank_adjustment, …}`.
  - Constructed situation: a 25.00 automatic transfer into a Statement Savings account runs in a cycle whose maintenance fee was charged.
  - Conclusions: under A it is recorded as automatic_transfer, `at_total` = 25.00, the waiver is met and the fee is refunded. Under B it is recorded as internal_transfer, `at_total` = 0.00 and there is no refund under this policy.
  - Affected: the base copy (lines of `savings_deposit.triggers` against `savings_evt_automatic_transfer`), which feeds the ext `linked_waiver_maintenance_refund.compute[at_total]`. Bears on **task 0**'s claimed policy. Its own world is not affected: MMA `waiver_automatic_transfer_min` is not_offered.

**Closed items, re-checked under the stated criterion:**

| Item | Status |
|---|---|
| round-1 O-1 (time anchor) | closed by declared overwrite |
| O-2 conversion checking-row half | closed |
| O-2 funding-refund certificate lookup | closed |
| O-4(a) | closed |
| O-4(b) | closed by declared overwrite |
| O-6 (two "standing" definitions) | closed: now two distinctly named quantities, and the difference is stated in both rules |
| O-7 edge-3 wording | closed |
| T0-O2 (order rationale) | closed |
| KB: replenishment "current statement cycle" | closed |
| KB: linked-waiver "now" versus cycle close | closed by declared overwrite |
| KB: auto-transfer single versus sum | closed |

**Not closed:**
- O-2 residuals: R2-1, R2-2, R2-3, R2-4.
- O-9, re-graded as R2-5.

**Observations (no two-passage contradiction):**
- R2-O1: round-1 O-7 edge-2 `resolved_by` and dataflow omissions, unchanged.
- R2-O2: same-day ties in "most recent internal transfer" and "most recent overdraft transfer"; `savings_transactions` carries no intra-day ordering.
- R2-O3: the merged linked-waiver proxy can call a fee "assessed contrary to the charter" that was correct when assessed. This is declared, so it is not a contradiction.
- R2-O4: `charged` basis punctuation, and `free` quoted with the cap sentence.
- O-3, O-5, O-8 carry forward unchanged.

This section contains nothing derived from round-2 GT or from the KB audit reports.

### closing_checklist (revision_2)

Written after both round-2 reveals (2026-09-12T21:42Z). Nothing above this heading in revision_2 was edited after the reveal; the freeze hashes are in each task's revision_2 comparison. The round-1 closing_checklist is left as it was.

- **Per-task files.** `0.md` and `1.md` each have a `## revision_2` appended, with the round-1 text untouched. Both round-2 derivations are frozen and hashed (21:42:08Z) before the reveal and before reading the KB reports. Contamination (prior exposure to round-1 GT) is disclosed in each file, and the round-2 blind status is void for both tasks by rule. Every value was mechanically re-derived from the new compute and the round-2 views, and matches round-2 GT exactly.
- **Revision_2 verdicts:**
  - Task 0: **SOURCE-POLICY RED** (charter R2-1, R2-2, R2-3, R2-5) · SOURCE-CHAIN PASS · SOURCE-TASK PASS.
  - Task 1: **SOURCE-POLICY RED** (charter R2-4; task R2-T1-c) · **SOURCE-CHAIN RED** (R2-T1-b) · **SOURCE-TASK RED** (R2-T1-a).
- **Coverage and scope.** Both hold: all 6 extended policies plus 1 workflow, split 3+workflow / 3, pairwise disjoint. Exactly one workflow task. 7 task tools, each used once in GT. uuid8s are unchanged and independent. The workflow's gold actions carry `requires_external_wait: false` and a `zero_wait_proof`.
- **Problem trees.** Both hold: task 0 has 2 prerequisites, 1 value_input and no cycle; task 1 has 2 prerequisite problems and 3 value_input edges with no cycle. The difficulty-wide graph is a DAG. Round-1 T1-O1 (task 1's scored value equal to the skip-both value) is closed: 542.55 against 537.55.
- **Gates.** The orchestrator's post-rework snapshot (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE all OK) applies to the audited forms. The artifact hashes at 2026-09-12T21:4xZ still equal the MANIFEST: yaml `c5f246ba…`, tools `0dcd69b7…`, `0.json` `e8b672ae…`, `1.json` `17560549…`. I did not run the gates myself. None of them tests the charter-level constructed-situation items or the stale dossier sentences found here.
- **Closed since round 1:**
  - Round-1 observations: O-1, O-2 (Private Client Checking half and funding-certificate half), O-4(a), O-4(b), O-6, O-7 (edge-3 wording), T0-O2, T0-O4, T1-O1, T1-O2, T1-O4.
  - KB policy-side items: 0.md S1, 0.md N2/S2, 1.md S1, 1.md S2.
- **Not closed or new:**
  - R2-1, R2-2, R2-3, R2-4: residuals of the first-row / inherited-gate class, O-2.
  - R2-5: O-9 re-graded; the root cause is in the verbatim base copy.
  - R2-T1-a: includes T1-O5, not closed in the rationale body.
  - R2-T1-b, R2-T1-c: new in round 2, stale dossier text left by the rework.
- **Difficulty verdict (revision_2): does not pass the source-layer audit.** Policy self-consistency fails for both tasks at charter level under the stated constructed-situation criterion. Task 1 also fails the problem-tree and unique-solution relationships on false proof-field assertions. No scored gold value is wrong; both tasks' gold arguments are uniquely entailed in their own worlds.

## revision_3

### charter_global_frozen (revision_3)

- Auditor: same, round-3 re-audit. Drafted 2026-09-12T21:5xZ. The authoritative freeze is the sha256 record in each task's revision_3 comparison, taken before any round-3 GT was read.
- Inputs re-hashed at 2026-09-12T21:54:13Z:
  - `savings.extended.yaml` = `a912de63cb48fa3d11fb6e17f09e3a691ce8575ba78f70b28ac0cd702aa64d18`. **Changed** since round 2 (`c5f246ba…`), so every section below is re-derived in full.
  - `task_tools.py` = `0dcd69b7…ff46` (unchanged).
  - blueprint `products/savings.yaml` = `8f308ff1…` (unchanged).
  - `share_tools.py`, `db_schema.json`, `blueprint.yaml` unchanged.
  - Views `round3/task_0.visible.json` = `311ec093…` and `round3/task_1.visible.json` = `89e3ac50…` are both **unchanged** from round 2 and match the MANIFEST.
- Base copy: `diff <(head -1249 …extended.yaml) blueprint/products/savings.yaml` shows no difference, so it is verbatim.
- Entry conditions: the post-rework gate snapshot (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK) and the rebuilt views were supplied. The input is complete.
- Criterion: the constructed-situation criterion, as in revision_2.
- contamination_disclosure: I have read the round-1 and round-2 GT of both tasks and the KB audit reports (see revision_2). I have not read round-3 task JSONs. This section is derived from the charter, the tool module, the blueprint, the DSL evaluator, and auditor-built constructed worlds (`scratchpad/policy_audit_swit/constructed_r3.py`). It uses no GT.

### policy_conflict_scan (revision_3)

Ext-side changes, found by reading the ext section in full:

- (a) **`certificate_proceeds_transfer`**
  - The certificate is now "the counterparty of the most recent deposit on this account posted as an internal transfer, taken only when that counterparty is a certificate of deposit of the same customer whose payout account … is this savings account". Otherwise "nothing is moved under this policy, and a request about the money of any other certificate is outside this policy".
  - Compute: `cd_cp` = LATEST internal-transfer deposit counterparty; `cd_id = CFIELD('cd','certificate_id', certificate_id=cd_cp, payout_account_id=HID)`.
- (b) **`linked_waiver_maintenance_refund`**
  - Now decides the **linked-checking waiver only**. The automatic-transfer waiver (with `at_min`/`at_total`/`at_ok`) is removed and delegated with the other waivers to base ("whether the minimum-balance, automatic transfer, age or relationship-balance waiver makes it refundable is decided under savings_evt_maintenance_and_statement_fees and savings_evt_fee_refund").
  - The opened-date proviso of round 2 is removed.
  - `lk_*` = `CFIELD('checking','status', variant_name=X, status='active') == 'active'`.
  - `cross_category.reads` = [variant_name, status].
  - The two overwrites are unchanged.
- (c) **`best_money_market_conversion`**: new sentences: "The per-tier account cap of savings_agg_multi_holding and every other entry-gate item of savings_product_change are not part of the ranking: they are checked as eligibility of the conversion once the target is chosen, and when the customer does not meet one of them for the target tier … no conversion is recorded and no lower tier is substituted." Compute is unchanged.
- (d) **`counted_withdrawal_fee_assessment`** and (e) **`overdraft_replenishment_transfer`**
  - The cycle is taken from "the most recent withdrawal on this account with channel overdraft_transfer, taken only when its counterparty is a checking account of the same customer". Compute: `od_cp` = LATEST OD counterparty, then `od_chk = CFIELD('checking','checking_account_id', checking_account_id=od_cp)`, then `cyc` = LATEST OD cycle when `od_chk` exists.
  - Replenishment `od_total` now sums "every overdraft protection transfer of that cycle, whichever of the customer's checking accounts it covered".
  - Replenishment `result` is 0 when no checking counterparty is found ("no amount is computed under this policy").
- (f) **`certificate_funding_fee_refund`** and **workflow**: unchanged from round 2.

Overlap, targets, triggers and terminal states are otherwise as in round 1. The component split (A: proceeds, linked-waiver refund, conversion, workflow; B: funding refund, assessment, replenishment) is unchanged.

### rule_compute_equivalence (revision_3)

- Mechanical checks:
  - every `compute_basis` sentence is a whitespace-normalised substring of its rule, with 0 misses;
  - no basis entry lacks a binding;
  - bindings without a basis: `chans`, `counted`, `standing`, `need`, all trivial.
- Round-2 R2-O4 is **closed**:
  - `charged` now quotes the full sentence verbatim;
  - `free` now quotes the fees-due sentence.
- New minor item R3-O2: `cur` (= `F('variant_name')`) is given the cap/eligibility sentence as its basis.

Each item below was re-tested with constructed worlds in `constructed_r3.py`, which runs the published compute through `check_compute.build_env`.

1. **proceeds transfer.** `cd_cp` → `cd_id` by exact certificate id plus the payout check matches the new identification sentence.
   - Probe: a second certificate `cdX`, listed **first** in `cd_certificates` and paying the account most recently (50.00 on 2026-09-01). Result: transfer = **50.00**, the most recent payer's money. That is the rule's answer, and record order does not matter.
   - Probe: an internal-transfer deposit from checking posted after the CD payout. Result: transfer = **0.00**, matching "nothing is moved under this policy".
   - R2-1 is **closed**. Residual wording is noted as R3-O1.
2. **linked-waiver refund.** `lk_*` filters on the tier and `status='active'`, so any returned row is active. It is an existence test.
   - Probe: a closed Premier Checking listed first, an active Premier Checking listed second, no PCC. Result: refund = **12.00** (met), matching "at least one checking account that is active and whose tier is one of the listed tiers".
   - R2-2 is **closed**.
   - Without the opened-date proviso, a listed account opened after the fee posted also meets the waiver. That falls under declared overwrite #1 ("read from the checking records as they stand when the refund is decided"). See R2-O3 (broadened) below.
   - No binding reads `channel='automatic_transfer'` any longer.
3. **conversion.**
   - `result` still ignores the tier cap. The rule now places the cap outside the ranking: "checked as eligibility of the conversion once the target is chosen … no conversion is recorded and no lower tier is substituted".
   - Constructed situation of R2-3 (2 PCMM already held): the rule gives target PCMM, the cap fails, so no conversion. The compute gives target PCMM, then the inherited gate refuses. Both reach the same conclusion.
   - Base `savings_product_change` ("must meet the target tier's entry gate") agrees.
   - R2-3 is **closed**.
4. **funding refund.** Unchanged and equivalent (see revision_2).
5. **assessment** and 6. **replenishment**. The cycle comes from the latest OD transfer of any customer checking account, and the "which checking account" record-order dependence is gone.
   - Probe: a second checking `chkZ`, listed **first** and naming no OD source, with an older OD transfer. Result: assessment 0 and replenishment 542.55, identical to the unmodified world. Record order has no effect.
   - The rule/compute pair for two checking accounts naming the same savings now gives "the most recent OD transfer, whichever account it covered" in both.
   - R2-4 is **closed**.

### action_binding_and_uuids (revision_3)

`task_tools.py` is unchanged and the (target_tool, computes) pairs are unchanged. The round-1 section is carried forward by reference on those two grounds.

### prerequisite_graph (revision_3)

- The 5 edges are unchanged in endpoints, kind, gate, condition, `resolved_by` and effect.
- Every `policy_source` is a verbatim substring of its rule.
- The graph is acyclic.
- R2-O1 (edge-2 `resolved_by` names the enabling transfer; dataflow omits the balance flows) carries over as an observation.

### override_declarations (revision_3)

- **linked-waiver refund.** The same two overwrites are declared; each superseded clause is verbatim in base, and each `replaced_by` is verbatim in the ext rule. Merged semantics: an active checking account of a listed tier per current records, with waiver parameters of the current savings tier. This is unique.
- **Assessment cap overwrite.** Unchanged and verbatim. Merged semantics are unique (see revision_2).
- **proceeds transfer.** The narrowing to "the certificate of deposit which most recently paid into it" names no base sentence. `savings_evt_withdrawal_allowance` and `savings_evt_closure` say nothing about which certificate's money may be moved, so there is no undeclared override.
- **conversion.** "no lower tier is substituted" agrees with base `savings_product_change` ("must meet the target tier's entry gate"). Base declares no substitution, so there is no undeclared override.

### findings (revision_3)

**Round-2 REDs, charter-level:**

| Item | Status |
|---|---|
| R2-1 | **closed** |
| R2-2 | **closed** |
| R2-3 | **closed** |
| R2-4 | **closed** |
| R2-5 | **closed at the extended layer** (see below) |
| R2-O4 | **closed** |

**R2-5 detail.** No extended policy, binding or task-claimed quantity reads the automatic-transfer channel. The linked-waiver refund no longer decides the automatic-transfer waiver. However, the **base-internal contradiction itself persists** in the verbatim base copy:
- `events[savings_deposit].triggers` maps an automatic transfer to `channel: internal_transfer`;
- `savings_evt_automatic_transfer` ("posts as a savings_deposit with channel automatic_transfer") and `savings_msr_cycle_automatic_transfer_total` read `automatic_transfer`.

It is recorded as **R3-B1 (open, blueprint-level; root cause `blueprint/products/savings.yaml`; orchestrator-logged known issue)**. It is not charged to either task's verdict for three reasons:
- neither task's claimed extended policies consume it;
- neither task's world contains an automatic-transfer deposit;
- the defect lies in an artifact this difficulty must copy verbatim.

It remains a two-passage contradiction under the stated criterion wherever base alone decides the automatic-transfer waiver. That covers base maintenance-fee assessment and base bank_error refunds, and this difficulty's linked-waiver refund now delegates exactly that question to base.

**Observations (no two-passage contradiction):**
- **R3-O1: proceeds rule, general statement plus exception.**
  - Opening sentence: the request concerns "the certificate of deposit which most recently paid into it", and "the transfer is a telephone withdrawal … whose amount is the certificate money still held in the account".
  - Identification sentence: "That certificate is the counterparty of the most recent deposit on this account posted as an internal transfer … when the most recent internal-transfer deposit came from any other account, … nothing is moved under this policy".
  - In a constructed world where an internal-transfer deposit from checking follows the CD's last payout (probe: 0.00), the certificate that most recently paid in still exists, but the policy moves nothing.
  - The exception clause states its scope explicitly, so one answer remains. This is recorded as a business-semantic narrowing: a request whose wording fits the trigger yields no movement under this policy.
- **R2-O3 (broadened): linked-waiver proxy.** Removing the opened-date proviso means a checking account opened *after* the fee posted now makes that fee a bank_error refund. This is declared by overwrite #1, so it remains an observation.
- **R3-O2:** the `cur` basis sentence does not match its binding.
- **Carried forward:** R2-O1 and R2-O2 (same-day ties; the proceeds `cd_cp` also uses LATEST over deposits); round-1 O-3, O-5, O-8.

No round-3 GT was used in this section.

### closing_checklist (revision_3)

Written after both round-3 reveals (2026-09-12T21:59:37Z). Nothing above this heading in revision_3 was edited after the reveal. The round-1 and round-2 texts are untouched.

- **Per-task files.** `0.md` and `1.md` each carry `## revision_3`.
  - Both derivations were frozen and hashed at 21:59:30Z, before the reveal.
  - The contamination (prior exposure to round-1 and round-2 GT) is disclosed in each file. Their blind status is void by rule.
  - Every value was mechanically re-executed from the round-3 compute and matches the round-3 GT exactly.
  - Both comparison sections carry PASS on all three relationships.
- **Revision_3 verdicts:**
  - Task 0: SOURCE-POLICY PASS · SOURCE-CHAIN PASS · SOURCE-TASK PASS.
  - Task 1: SOURCE-POLICY PASS · SOURCE-CHAIN PASS · SOURCE-TASK PASS.
- **Round-2 REDs re-verified:** R2-1, R2-2, R2-3 and R2-4 are closed (rule and compute agree; confirmed on constructed worlds). R2-5 is closed at the extended layer. R2-T1-a (including T1-O5), R2-T1-b, R2-T1-c and R2-O4 are closed.
- **No regression.**
  - The scored values, prerequisite trees, load-bearing runs and zero-wait fields are unchanged from revision 2.
  - The propagation sweep of both task files found no stale sentence asserting a superseded rule, compute, value or persona line.
- **New observations** (no two-passage contradiction):
  - R3-O1: proceeds rule, general statement plus exception.
  - R2-O3, broadened: the opened-date proviso is dropped; this falls under the declared overwrite.
  - R3-O2: the `cur` basis sentence.
  - R3-T0-O1: `courtesy_window` wording in task 0's base-invariant card. It has been present since round 1 and was not recorded in my earlier revisions.
  - R3-T1-O1: `order_uniqueness` wording.
- **Open and not charged: R3-B1.** This is a base-internal contradiction in the verbatim base copy (blueprint `products/savings.yaml`):
  - `events[savings_deposit].triggers` maps an automatic transfer to `channel: internal_transfer`;
  - `savings_evt_automatic_transfer` and `savings_msr_cycle_automatic_transfer_total` use `automatic_transfer`.

  After the round-3 rework, no extended policy, scored quantity or task world of this difficulty consumes it, and the orchestrator has logged it as a known base issue. Under the constructed-situation criterion it is still a contradiction wherever base alone decides the automatic-transfer waiver. That includes the question this difficulty's linked-waiver refund explicitly delegates to base. It needs a blueprint-level decision.
- **Coverage, scope, one workflow, uuid8s:** unchanged; all hold.
  - The 6 extended policies plus 1 workflow split 3 + workflow / 3, disjoint.
  - The 7 task tools are each used once in GT.
  - `requires_external_wait: false` and `zero_wait_proof` are present on the workflow's gold actions.
- **Problem trees:** unchanged, and both hold.
  - Task 0 has 2 prerequisites, 1 value_input, acyclic.
  - Task 1 has 2 prerequisite problems, 3 value_input, acyclic, and its opening-world value (542.55) differs from gold (537.55).
  - The difficulty-wide graph is a DAG.
- **Gates.** The orchestrator's round-3 post-rework snapshot applies: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE are all OK. The artifact hashes at 2026-09-12T22:01:28Z still equal the MANIFEST: yaml `a912de63…`, tools `0dcd69b7…`, `0.json` `fbfabd3c…`, `1.json` `682e8c56…`. I did not run the gates myself.
- **Difficulty verdict (revision_3): passes the source-layer audit.** Policy self-consistency, problem tree and unique solution all PASS for both tasks. The one open item is R3-B1, which belongs to the blueprint and is outside this difficulty's writable artifacts.

## revision_4

### charter_global_frozen (revision_4)

- Auditor: the same auditor, round-4 re-audit. The authoritative freeze is the sha256 record cited in each task's revision_4 comparison, taken before any round-4 GT was read.
- Inputs re-hashed at 2026-09-12T22:31:34Z:
  - `savings.extended.yaml` = `18641a05f383f943d6622184c02461a9b30fa7c4df78d8f581613be1020eac8a`. Changed since round 3 (`a912de63…`), so every section below is re-derived in full. A snapshot copy is kept in `scratchpad/policy_audit_swit/extended_r4.yaml`.
  - `task_tools.py` = `0dcd69b7…` (unchanged).
  - Blueprint `products/savings.yaml` = `8f308ff1…` and the other blueprint files: unchanged.
  - Views `round4/task_0.visible.json` = `311ec093…` and `task_1.visible.json` = `89e3ac50…`: both unchanged, matching the MANIFEST.
- Base copy: verbatim (`diff` shows no difference).
- Entry conditions: the post-rework gate snapshot (all OK) and the rebuilt views were supplied. Input is complete.
- **Criterion:** the constructed-situation criterion, now explicitly applied to the frozen base **parameter_schema, event field and measure** text as well as base rules, as the coordinator requested.
- **Disclosure about my earlier revisions.** In revisions 2 and 3 I tested the declared overwrites only against base *rule* sentences. I did not test them against frozen base parameter descriptions. That is why I closed round-1 O-1 (linked-waiver anchor) and O-4(b) (cap) on the strength of the overwrites. The KB re-audit's D1 principle, that an overwrite cannot retire parameter text, applies equally to O-4(b), so it is reopened below as R4-2. Round-1's acceptance of the assessment's "refunded … in the cycle" formula is reopened as R4-3.
- **contamination_disclosure:** I have seen round-1 to round-3 GT of both tasks and the KB revision-1 reports. I have not read the round-4 task JSONs. I have not read the KB revision-2 reports; I know D1/S3r2 only from the coordinator's brief. Nothing here uses GT.

### policy_conflict_scan (revision_4)

**What changed.** A policy-by-policy comparison against my round-3 reading shows that only `savings_ext_linked_waiver_maintenance_refund` changed:

- **`overwrite`** is now `[]`. Both round-2/3 overwrites are withdrawn.
- **The rule restores the base basis:** "that is when the customer held at that cycle close an active checking account of a tier listed in the waiver_linked_checking_tiers of the savings tier in force at that close".
- **The rule adds refund conditions:** "The checking and savings records keep each account's opening and closing dates but only its current tier and status, so a refund under this policy is allowed only while those records still show the position at that cycle close: (a) no checking account of the customer was opened or closed after the cycle closing date, (b) none was converted to another tier or moved into or out of active status since that close, and (c) the savings account has not been converted since that close. These are conditions for a refund under this policy, not part of the amount; when any of them fails, no refund is made under this policy and the fee is decided under savings_evt_maintenance_and_statement_fees and savings_evt_fee_refund on the cycle-close basis."
- **The compute is unchanged from round 3.** The `lk_*` status existence tests and the current-tier `P('waiver_linked_checking_tiers')` remain, and there is no binding for conditions (a) to (c).
- **Unchanged from round 3:** the proceeds transfer, conversion, funding refund, assessment (including its cap overwrite), replenishment and workflow texts and computes.

**Scope split:** unchanged.

### rule_compute_equivalence (revision_4)

**Mechanical checks.** Every `compute_basis` sentence is a verbatim substring of its rule, and every `policy_source` is verbatim. The linked-waiver `linked_ok` basis now quotes the cycle-close sentence.

**Linked waiver: stated basis against frozen base text.** The ext rule states one basis, the cycle close. That agrees with:
- base `parameter_schema.waiver_linked_checking_tiers`: "Holding an active checking account of one of these tiers at cycle close waives the maintenance fee";
- base `savings_evt_maintenance_and_statement_fees`: "an active checking account of a tier listed in waiver_linked_checking_tiers held by the same customer at cycle close" and "The tier used is the variant_name at cycle close."

**The operative test is conditioned on facts no record holds.** See R4-1. The schema (`db_schema.json`) has no table or field that records a tier conversion or a status transition with its date:
- `savings_accounts`, `checking_accounts`: current `variant_name` and `status` only, plus `opened_date`/`closed_date`.
- `savings_requests.request_type` ∈ {account_closure, automatic_transfer_change}.
- `checking_service_orders.event_type` ∈ {stop_payment, stop_renewal, card_replacement}.

So condition (a) is checkable, from `opened_date`/`closed_date`. Conditions (b) and (c) are not, and the rule says so itself ("keep … only its current tier and status").

**Other policies.** Unchanged from round 3 and re-confirmed, except for the two items the frozen-text sweep adds (R4-2, R4-3).

### action_binding_and_uuids (revision_4)

`task_tools.py` and the (target_tool, computes) pairs are unchanged. Carried forward by reference.

### prerequisite_graph (revision_4)

Unchanged. There are 5 edges, the graph is acyclic, and every `policy_source` is verbatim.

Edge 3's effect, "voided counts each bank_error refund of the cycle's excess fees, so every refunded erroneous fee drops out of standing", is one of the two passages of R4-3.

### override_declarations (revision_4)

**Linked-waiver refund.** `overwrite: []`, and no base sentence is contradicted in text. The rule defers every case in which its conditions fail to base "on the cycle-close basis". **S3r2 closed:** no base sentence is retired any longer.

**Assessment cap overwrite (unchanged since round 2), re-tested against frozen base text.** See R4-2.

**Frozen-text sweep: base `parameter_schema`, event fields and measures read by the six ext policies.** Every other item checked is consistent:

| Base text | Ext rule it was checked against | Result |
|---|---|---|
| `free_withdrawals_per_cycle` | — | consistent |
| `excess_withdrawal_counted_channels` ("branch and ATM withdrawals never count") | internal transfer never counts | consistent (no tier lists internal_transfer) |
| `overdraft_transfer_counts_toward_limit`, `excess_withdrawal_fee`, `automatic_transfer_min_amount` | — | consistent |
| `minimum_opening_deposit`, `entry_required_checking_tiers`, `max_accounts_per_customer_this_tier` | — | consistent |
| event `savings_deposit.counterparty_account_id` | proceeds `cd_cp` | consistent |
| event `savings_withdrawal.counterparty_account_id` | `od_cp`, `fund_cp` | consistent |
| event `savings_fee.source_item_id` | — | consistent |
| event `savings_fee_refund.amount` ("equal to the fee's amount") and `adjustment_reason` | — | consistent |
| measure `savings_msr_cycle_counted_withdrawals` | `n_*`, `n_od` | consistent |

The exceptions are R4-2 (`excess_withdrawal_fee_max_per_cycle`, `savings_msr_cycle_excess_fees`) and R4-3 (`savings_fee_refund.statement_cycle`).

### findings (revision_4)

- **D1 (KB revision-2): stated-basis half closed; substance not closed.** The charter now states one basis, the cycle close, matching the frozen parameter text. But the operative test that stands in for it rests on conditions (b) and (c), which no record can establish. See R4-1.
- **S3r2: closed.** The overwrite retiring "The tier used is the variant_name at cycle close." is withdrawn. The savings tier at the close now enters through condition (c), which R4-1 covers.
- **S2r2 (automatic-transfer single-transfer vs sum wording): not charged.** It is base against base: `parameter_schema` describes a single transfer, while the base rule and measure use the sum. No ext policy decides the automatic-transfer waiver any longer. It is recorded with R3-B1 as a blueprint-level known issue, as the orchestrator logged it.

- **R4-1 — SOURCE-POLICY RED (charter). The linked-waiver refund conditions cannot be established from any record, so the policy has two operative readings.**
  - **Passage A (rule):** "The checking and savings records keep each account's opening and closing dates but only its current tier and status, so a refund under this policy is allowed only while those records still show the position at that cycle close: … none was converted to another tier or moved into or out of active status since that close, and the savings account has not been converted since that close."
  - **Passage B (rule, continued):** "While they hold, … the linked-checking waiver is met when that tier offers waiver_linked_checking_tiers and the customer holds at least one checking account that is active and whose tier is one of the listed tiers". The compute implements B unconditionally (`result: "RND(fee_amt) if linked_ok else 0"`) and has no binding for the conditions.
  - **Why A cannot be checked:** by A's own words, and by the schema, no record carries the history that conditions (b) and (c) require.
  - **Reading 1 (lenient):** the conditions are presumed to hold whenever nothing on record contradicts them. They then always hold for (b) and (c), and the policy reduces to a current-state test.
  - **Reading 2 (strict):** the conditions must be established. They never can be, so no refund is ever made under this policy, and the fee falls to base "on the cycle-close basis". The linked waiver there is equally unestablishable from records.
  - **Constructed situation:** a Money Market Account whose cycle minimum balance is below 2,500.00 and relationship balance below 15,000.00, so no other waiver applies. A 12.00 maintenance fee was charged at the close. The customer's only checking account is Premier Checking, active, opened years before the close, never closed. Nothing on record shows a conversion.
    - Reading 1: a bank_error refund of 12.00.
    - Reading 2: no refund.
  - **Second constructed situation:** the same account was, unrecorded, Everyday Checking at the close and converted to Premier afterwards. The records are byte-identical to the first. The rule's stated basis says no waiver. Reading 1 and the compute say 12.00.
  - The stated cycle-close basis and the operative test therefore diverge exactly where the records cannot show the difference. That is the substance of D1.
  - **Root cause:** refund eligibility is conditioned on facts the rule itself says no record keeps. There is no evidence source for conditions (b) and (c).
  - **Affected:** `extended_policies[savings_ext_linked_waiver_maintenance_refund].rule`, the sentences "a refund under this policy is allowed only while … since that close" and "While they hold …", and `compute[result]`.
  - **Bears on task 0.**
- **R4-2 — SOURCE-POLICY RED (charter; pre-existing since round 2; D1 class). The assessment's cap overwrite against frozen base parameter and measure text.**
  - **Passage A (ext overwrite and rule):** "The per-cycle cap is applied to the fees due, so a fee assessed contrary to the charter never uses up a place under the cap."
  - **Passage B (frozen base):**
    - `parameter_schema.excess_withdrawal_fee_max_per_cycle`: "Most excess withdrawal fees charged in one statement cycle; integer count."
    - measure `savings_msr_cycle_excess_fees`: "Count of savings_fee rows with fee_code excess_withdrawal posted in the cycle."
    - base `savings_evt_fee_refund`: "A bank_error refund applies when the fee was assessed contrary to the savings charter, such as … beyond excess_withdrawal_fee_max_per_cycle".
  - **Constructed situation:** Statement Savings (free 6, cap 6), 13 counted withdrawals in the cycle, so fees due = MN(7, 6) = 6. Six excess-fee rows are already posted, one of them on an ATM withdrawal and refunded as bank_error.
    - Ext gives standing 5 and owed 1, so it charges a 7th row, which stands.
    - The frozen parameter and measure make 7 rows "charged … in one statement cycle" exceed the maximum of 6. Base fee_refund then calls the 7th fee "beyond excess_withdrawal_fee_max_per_cycle", which is a bank error to be refunded.
    - Different conclusions: charge and keep, against refund.
  - A "net of refunds" reading of "charged" is excluded, because the base measure that operationalises the cap counts posted rows.
  - **Affected:** `extended_policies[savings_ext_counted_withdrawal_fee_assessment].overwrite[0]` / rule / `compute[due_fees, standing, owed]`.
  - **Bears on task 1.**
- **R4-3 — SOURCE-POLICY RED (charter; pre-existing since round 1; round-1 acceptance reopened). The assessment's `voided` counts refunds by the cycle they posted in, while the rule's reason and the edge effect count them by the fee's cycle.**
  - **Passage A (rule formula and compute):** "The fees standing for the cycle are the excess_withdrawal fee rows of the cycle less the excess_withdrawal fees refunded as bank_error in the cycle", implemented as `voided: COUNT(… fee_code='excess_withdrawal', adjustment_reason='bank_error', statement_cycle=cyc)`. Every refund row carries the cycle it **posted** in: base event field `savings_fee_refund.statement_cycle` reads "Statement cycle in which the refund posted", and the funding-refund rule says "posted in the current statement cycle".
  - **Passage B (same rule):** "…because a fee assessed contrary to the charter does not stand", and "Before the fees owed are counted, every excess withdrawal fee of the cycle that was assessed contrary to the charter must already have been refunded". **Passage B′ (prerequisite effect):** "voided counts each bank_error refund of the cycle's excess fees, so every refunded erroneous fee drops out of standing and owed rises by one for it".
  - **Constructed situation** (`scratchpad/policy_audit_swit/constructed_r4.py`): task 1's own ledger, with the clock moved to 2026-09-22, in cycle 2026-10, before any overdraft transfer of that cycle. The reconciled cycle stays 2026-09. The owed bank_error refund of the 15.00 erroneous fee posts with statement_cycle "2026-10".
    - Passage A and the compute give assessment **0**, so no fee.
    - Passages B and B′ say the refunded fee no longer stands, so 1 fee of **10.00** is owed. The counterfactual with the refund labelled 2026-09 gives 10.00.
    - The replenishment in the same world counts the refunded 15.00 as a fee the account "bears" (542.55), because its definition uses refunds "posted in the cycle".
  - **Affected:** `savings_ext_counted_withdrawal_fee_assessment.rule` / `compute[voided]` / `prerequisite[0].effect`.
  - **Bears on task 1.**

**Not charged:** R3-B1 and S2r2 are base-internal and belong to the blueprint's known issues.

**Carried observations:** R3-O1, R3-O2, R2-O1, R2-O2, O-3, O-5, O-8. R2-O3 is superseded by R4-1, since the overwrite it rested on is withdrawn.

**No regression** of the round-2 and round-3 closures R2-1 to R2-4 or R2-T1-a/b/c at the charter level: their texts and computes are unchanged.

No round-4 GT was used in this section.

### closing_checklist (revision_4)

This checklist was written after both round-4 reveals at 2026-09-12T22:38:35Z. Nothing above this heading in revision_4 was edited after the reveal. Revisions 1–3 are untouched.

- **Per-task files.** `0.md` and `1.md` each carry `## revision_4`.
  - Both were frozen and hashed at 22:38:27Z, before the reveal.
  - Contamination is disclosed in each file, so their blind status is void.
  - Every value re-executes under the round-4 compute and equals the round-4 GT.
- **Revision_4 verdicts:**
  - Task 0: **SOURCE-POLICY RED** (charter R4-1) · SOURCE-CHAIN PASS · SOURCE-TASK PASS.
  - Task 1: **SOURCE-POLICY RED** (charter R4-2, R4-3) · SOURCE-CHAIN PASS · SOURCE-TASK PASS.
  - Neither task's own world yields a second answer.
- **Rework claims:**
  - S3r2: **closed**.
  - D1: the stated basis is now single and matches the frozen parameter text. The operative test still diverges from that basis wherever the records cannot show post-close conversions or status changes, so D1 is **not closed in substance** (R4-1).
  - S2r2: base against base, not charged. It is logged with R3-B1.
- **New in this round's sweep of frozen parameter, event and measure text.** Both findings predate the round-4 rework; my earlier revisions did not test against frozen parameter or event text.
  - R4-2: cap overwrite against the frozen parameter and measure.
  - R4-3: posting-cycle `voided` against the fee-cycle reason and edge effect.
- **No regression** of the round-2 and round-3 closures.
  - Coverage, scope, the single workflow and the uuid8s are unchanged.
  - The problem trees are unchanged: task 0 has 2 prerequisites and 1 value_input edge; task 1 has 2 prerequisite problems and 3 value_input edges; both are acyclic.
  - The gate snapshot (all OK) applies, and the artifact hashes equal the MANIFEST. I did not run the gates myself.
- **Difficulty verdict (revision_4): does not pass the source-layer audit.** Policy self-consistency fails at charter level for both tasks (R4-1; R4-2, R4-3). Problem trees and unique solutions pass in both tasks' own worlds.

## revision_5

### charter_global_frozen (revision_5)

- **Auditor:** same, round-5 re-audit. The authoritative freeze is the sha256 record in each task's revision_5 comparison, taken before any round-5 GT was read.
- **Inputs re-hashed 2026-09-12T23:00:28Z:**
  - `savings.extended.yaml` = `fee8420070413cb492e3f95711c9abca062d50f4dff0f0fc441fa368fbe51963`. Changed since round 4. The exact textual diff against my round-4 snapshot is in `scratchpad/policy_audit_swit/extended_r4.yaml` → `extended_r5.yaml`, so every section below is re-derived in full.
  - `task_tools.py` = `0dcd69b7…`. Blueprint files (`products/savings.yaml` = `8f308ff1…` and the rest): unchanged.
  - Views `round5/task_0.visible.json` = `311ec093…` and `task_1.visible.json` = `89e3ac50…`: unchanged.
- **Base copy:** verbatim.
- **Entry conditions:** the gate snapshot (all OK) and the rebuilt views were supplied.
- **Criterion:** the constructed-situation criterion, applied to base rules, parameter_schema, event fields and measures. It includes the coordinator's check that the charter contains "no condition that no record can establish".
- **contamination_disclosure:** I have seen round-1 to round-4 GT of both tasks and the KB revision-1 reports. I have not read round-5 task JSONs or KB revision-2 reports. Nothing here uses GT.

### policy_conflict_scan (revision_5)

Exact diff against round 4:

- **(a) `savings_ext_linked_waiver_maintenance_refund` withdrawn.**
  - Workflow step 2 (`refund_savings_maintenance_fee_bf99bb2f`) now has `computed_by: []`: the maintenance refund is decided by base alone (`savings_evt_fee_refund` + `savings_evt_maintenance_and_statement_fees`).
- **(b) New `savings_ext_same_contact_reactivation`.**
  - Subject `savings_reactivate`; it computes `reactivation_date` for `reactivate_savings_account_bfe70db1`.
  - Rule: the reactivating transaction is "a withdrawal on the account posted on the current date, the date of the contact, with channel telephone_banking, online_transfer or mobile_app_transfer, taken only when its counterparty is a checking account of the same customer; for each of the three channels the transfer looked at is the most recent one of that channel posted on the current date".
  - Compute: `n_today`, `tel_cp`/`onl_cp`/`mob_cp` = LATEST … `posted_date=NOW`, `own_*` = exact-id checking read, `result = NOW if dormant and n_today ≥ 1 and any own_* else ''`.
  - Prerequisite: ← `certificate_proceeds_transfer` (`state_gate`, gate `savings_transactions.posted_date`).
- **(c) `best_money_market_conversion`.**
  - New binding `active = F('status') == 'active'`; `result` keeps the current tier when not active.
  - New sentences: "When the owner moves money out of the account in the same contact, the balance compared is the balance after that transfer has posted" and "An account that is not active when the target is chosen stays in its current tier and no conversion is recorded".
  - Prerequisite is now a single edge ← `same_contact_reactivation` (`value_input`, gate `active`). The edge to the refund policy is gone with that policy.
- **(d) `counted_withdrawal_fee_assessment`.**
  - Overwrite withdrawn (`overwrite: []`).
  - Cap now counts "Every excess withdrawal fee row posted in the cycle, refunded or not … as savings_msr_cycle_excess_fees counts them" (`room = MX(max − fee_rows, 0)`, `owed = MX(MN(beyond − covered, room), 0)`).
  - New scope sentences:
    - "This policy reconciles only the current statement cycle … when the cycle of the most recent overdraft protection transfer is an earlier cycle, nothing is reconciled under this policy."
    - "This policy applies only while every excess withdrawal fee of the cycle either sits on a counted withdrawal beyond the allowance or has been refunded as bank_error, and every bank_error refund of an excess withdrawal fee posted in the cycle refunds a fee of that same cycle".
  - Edge-3 effect reworded to match.
- **(e) `overdraft_replenishment_transfer`.** New scope sentences:
  - "This policy computes an amount only for the current statement cycle … when the cycle so found is an earlier cycle, no amount is computed under this policy."
  - "Every excess withdrawal fee refund posted in the cycle must refund a fee of that same cycle, as its source_item_id shows; when one refunds a fee of another cycle, no amount is computed under this policy."
  - These are quoted as the `compute_basis` of `cyc` and `refunds`. **Neither compute binding changed.**
- **(f) Unchanged:** proceeds transfer, funding refund, workflow `order_rationale`.
- **Scope split:**
  - A = {proceeds, reactivation, conversion} + workflow.
  - B = {funding refund, assessment, replenishment}.
  - Still 6 extended policies; each `(target_tool, computes)` is unique.

### rule_compute_equivalence (revision_5)

**Mechanical checks.**
- Every `compute_basis` sentence and every `policy_source` is verbatim.
- Bindings without a basis: `chans`, `counted`, `need`, all trivial.

**Probes** (`scratchpad/policy_audit_swit/constructed_r5.py`):

| Policy | Result |
|---|---|
| proceeds transfer, funding refund | unchanged; equivalent |
| conversion | `active` implements "An account that is not active … stays in its current tier". Equivalent. The cap still sits outside the ranking, as the round-3 rule says. |
| reactivation | see R5-1 |
| assessment, cap part | "every … fee row posted in the cycle, refunded or not" → `fee_rows`, `room`. Equivalent, and agrees with the frozen parameter and measure text (see override_declarations). |
| assessment, scope sentences | no compute binding; see R5-2 |
| replenishment | `cyc` and `refunds` are *attributed* the two new scope sentences but do not implement them; see R5-2 |

**"No condition that no record can establish" check.** Each condition the extended text now states:

| Condition | Establishable? | Evidence |
|---|---|---|
| Reactivation "same contact" | No: replaced by "posted on the current date" | R5-1(a) |
| Reactivation "most recent one of that channel posted on the current date" | No | R5-1(b); records carry no intra-day order and all such rows share `posted_date` |
| Assessment/replenishment "current statement cycle" | Yes | `frozen_time` + `statement_cycle_day` |
| Assessment/replenishment fee-on-counted-withdrawal and refund-of-same-cycle conditions | Yes | `source_item_id` → fee row → its `statement_cycle` / withdrawal channel. Placing a fee "beyond the allowance" among same-day withdrawals inherits base's unrecorded intra-day order (R2-O2). |
| Conversion "active" | Yes | status |
| Conversion "every refund owed" | Yes via ledger in the task world | Its base linked-checking part inherits a blueprint-level gap, R5-B2 |

### action_binding_and_uuids (revision_5)

`task_tools.py` is unchanged. The pairs changed as follows:
- `reactivate_savings_account_bfe70db1` is now claimed by `savings_ext_same_contact_reactivation`, computing `reactivation_date`.
- `refund_savings_maintenance_fee_bf99bb2f` is no longer claimed by any extended policy.

Every pair is claimed by at most one policy. The uuid8 findings are carried forward by reference.

### prerequisite_graph (revision_5)

Edges:
1. conversion ← reactivation (`value_input`, `active`)
2. reactivation ← proceeds transfer (`state_gate`, gate `savings_transactions.posted_date`)
3. assessment ← funding refund (`value_input`, `voided`)
4. replenishment ← assessment (`value_input`, `fees_net`)
5. replenishment ← funding refund (`value_input`, `fees_net`)

- The graph is acyclic.
- Every `problem` is an extended policy id.
- Every `policy_source` is verbatim.
- **Edge 2 kind/gate mismatch (R5-O1).** Its `kind` is `state_gate`, but its `gate` is a record field, not an eligibility id. Its effect speaks of compute bindings ("n_today counts it, own_tel becomes true"), which makes it a value input in substance. No tree requirement changes as a result: task 0 still has one value_input edge. Recorded as an observation.
- **Conversion "after every refund owed" (R5-O2).** This sentence is still in the conversion rule, but its prerequisite now has no declarable `problem`, because the refund is base-only. The tree read from the policy therefore has one more prerequisite (the base refund) than the declared graph.

### override_declarations (revision_5)

- **Maintenance refund.** No extended text now restates or proxies the base linked-waiver basis. Base decides on its own cycle-close basis. That agrees with base `parameter_schema.waiver_linked_checking_tiers` and "The tier used is the variant_name at cycle close". R4-1 is closed at the extended layer.
  - The base basis itself can only be read from current records. The records do not hold tier or status history, so a post-close conversion or status change cannot be seen. This is a blueprint-level evidence gap (R5-B2).
  - Through the conversion's "every refund owed", R5-B2 can reach an extended value input. It does not in task 0's world, because the ledger-established minimum-daily-balance waiver settles the refund there.
- **Assessment cap.** The overwrite is withdrawn. The ext cap counts posted rows. That agrees with:
  - `parameter_schema.excess_withdrawal_fee_max_per_cycle` ("Most excess withdrawal fees charged in one statement cycle");
  - the measure `savings_msr_cycle_excess_fees`;
  - the base clause "until savings_msr_cycle_excess_fees reaches excess_withdrawal_fee_max_per_cycle";
  - base fee_refund's "beyond excess_withdrawal_fee_max_per_cycle".

  The R4-2 constructed case now gives `room` = 0, so no 7th row. **R4-2 is closed.**
- **Assessment voided / refund cycle.** The posting-cycle formula still stands, but the policy now applies only to the current cycle, and only while every refund posted in the cycle refunds a fee of that cycle. Within that scope, posting cycle and fee cycle coincide, so the "does not stand / covers no withdrawal" reason and the formula agree. **R4-3 is closed at the rule level.** The compute does not carry the scope sentences, which is R5-2.
- **Reactivation against base `savings_evt_dormancy` and the frozen event field.** Undeclared override; see R5-1(a).
  - Base `savings_evt_dormancy` says "Reactivation needs a customer-initiated transaction in the same contact, and its date becomes the new last_customer_activity_date". The base lifecycle says "An identity-verified owner made contact and a customer-initiated transaction reactivated the account". Base event field `savings_withdrawal.posted_date` reads "Business day the withdrawal posted".
  - The ext identifies the same-contact transaction as a withdrawal "posted on the current date, the date of the contact", and `overwrite` is `[]`.

### findings (revision_5)

**Round-4 REDs, re-checked:**

| Item | Status |
|---|---|
| R4-1 | closed (extended policy withdrawn; base decides) |
| R4-2 | closed |
| R4-3 | closed at the rule level; see R5-2 for compute |
| D1 | moot for this difficulty's extended text; the base-level evidence gap is recorded as R5-B2 |
| S3r2 | still closed |

**New RED findings:**

- **R5-1 — SOURCE-POLICY RED (charter; new in round 5). The reactivation policy's identification of the same-contact transaction is an undeclared override of the base, and it depends on facts no record holds.**
  - **(a) "same contact" replaced by "posted on the current date".**
    - Passage A: the base, and the ext's own first sentence, "reactivated when its identity-verified owner makes a customer-initiated transaction in the same contact".
    - Passage B: "The reactivating transfer is a withdrawal on the account posted on the current date, the date of the contact", with compute `n_today`/`*_cp` filtered on `posted_date=NOW`.
    - Probe P5: task 0's world plus an online transfer of 100.00 to the owner's own checking, posted 2026-09-11 before the call, and no transaction in the contact.
      - Compute and passage B give reactivation date **'2026-09-11'**.
      - Passage A gives **no reactivation** until a transaction is made in this contact. The agent can establish contact membership from the conversation transcript, where the transfer is a tool call; the posted date cannot establish it.
    - Weekend case: a contact on a non-business day. The transfer made in the contact posts on the next business day (base event field `savings_withdrawal.posted_date`: "Business day the withdrawal posted").
      - Passage B finds "no withdrawal … posted on the current date", so the account "stays dormant".
      - Passage A reactivates.
    - Not declared in `overwrite`.
  - **(b) "the most recent one of that channel posted on the current date".** Records hold no intra-day order: `posted_date` is a date, and trace numbers are not sequential. For two withdrawals of one channel on one day, "most recent" cannot be established. The compute's LATEST with equal dates returns the first row in record order.
    - Probe P6: two telephone transfers on 2026-09-11, one to the owner's checking and one with no counterparty.
      - Record order own-first gives reactivation **'2026-09-11'**.
      - Record order external-first gives **''** (stays dormant).
      - The records are identical up to row order, and the rule's answer depends on a fact no record holds.
  - **Root cause:** a date and record-order proxy stands in for "same contact" and for "most recent".
  - **Affected:** `extended_policies[savings_ext_same_contact_reactivation].rule` sentences 3–4 and `compute[n_today, tel_cp, onl_cp, mob_cp, result]`.
  - **Bears on task 0.**
- **R5-2 — SOURCE-POLICY RED (charter; new in round 5). The new scope conditions of the assessment and the replenishment are not implemented in compute, and the replenishment's `compute_basis` attributes them to bindings that do not implement them.**
  - Passage A (rule):
    - Assessment: "This policy reconciles only the current statement cycle … when the cycle of the most recent overdraft protection transfer is an earlier cycle, nothing is reconciled under this policy", and "This policy applies only while every excess withdrawal fee of the cycle either sits on a counted withdrawal beyond the allowance or has been refunded as bank_error, and every bank_error refund … posted in the cycle refunds a fee of that same cycle".
    - Replenishment: "This policy computes an amount only for the current statement cycle … no amount is computed", and "when one refunds a fee of another cycle, no amount is computed under this policy". These are quoted as the basis of `cyc` and `refunds`.
  - Passage B (compute): `cyc` is still `LATEST(… overdraft_transfer) if od_chk != None else None`, and `refunds` is still a plain SUM. No binding tests the current cycle, the fee placement or the refund's source cycle. Sibling scope clauses ("when that counterparty is not one of the customer's checking accounts, nothing is reconciled") *are* implemented, through `od_chk`.
  - Probes:
    - **P1** (task 1's ledger, clock 2026-09-22 in cycle 2026-10): replenishment compute **542.55**; rule "no amount is computed".
    - **P2** (erroneous fee refunded on 2026-09-15 in 2026-09, clock 2026-09-22): assessment compute **10.00**; rule "nothing is reconciled".
    - **P3** (at frozen time, an 8th counted withdrawal, erroneous fee not yet refunded): assessment compute **10.00**; rule: condition fails, so nothing under this policy.
    - **P4** (a 2026-09 courtesy refund of a 2026-08 fee on the ledger): replenishment compute **532.55**; rule "no amount is computed".
  - These conditions *are* establishable from records. The defect is the rule↔compute non-equivalence and, for the replenishment, a `compute_basis` that claims an implementation which does not exist.
  - **Contrast with round 3's conversion cap:** that rule declared the cap "not part of the ranking: they are checked as eligibility … once the target is chosen", so its compute was declared not to carry it.
  - **Affected:**
    - `savings_ext_counted_withdrawal_fee_assessment.rule` / `compute[cyc]`, with no binding for the conditions;
    - `savings_ext_overdraft_replenishment_transfer.compute_basis[cyc, refunds]` / `compute[cyc, refunds, result]`.
  - **Bears on task 1.**

**Not charged, blueprint-level:**
- **R3-B1**, automatic-transfer channel.
- **S2r2**, single-transfer versus sum wording.
- **R5-B2**, base cycle-close linked-checking waiver. No tier or status history exists to evaluate it once anything may have changed since the close. It is base-internal, and after the withdrawal of the extended refund policy it reaches the extended charter only through the conversion's "every refund owed".

**Observations:**
- **R5-O1:** edge-2 kind/gate mismatch.
- **R5-O2:** the declared tree omits the base refund prerequisite, which the conversion rule still states.
- **Carried forward:** R3-O1, R3-O2, R2-O1 and R2-O2. R2-O1 is re-shaped: the transfer now feeds the reactivation directly.
- **T0-O1 (opening-world root value equal to gold)** is now closed: the opening-world conversion value is "Money Market Account", because the account is not active, while the gold value is PCMM. It is confirmed per task in `0.md`.

**No regression** of R2-1 to R2-4 or R2-T1-a/b/c: proceeds, funding refund, overdraft-cycle selection and the task-1 texts are unchanged.

No round-5 GT was used in this section.

### closing_checklist (revision_5)

Written after both round-5 reveals (2026-09-12T23:08:19Z). Nothing above this heading in revision_5 was edited after the reveal. Revisions 1–4 are untouched.

**Per-task files**
- `0.md` and `1.md` each carry `## revision_5`, frozen and hashed at 23:08:10Z, before the reveal.
- Task 0 was fully re-derived against the round-5 charter because its policy set and tree changed. The derivation is not blind, and that is disclosed.
- Every value equals the round-5 GT.

**Revision_5 verdicts**
- **Task 0:** SOURCE-POLICY **RED** (charter R5-1) · SOURCE-CHAIN PASS · SOURCE-TASK PASS.
- **Task 1:** SOURCE-POLICY **RED** (charter R5-2) · SOURCE-CHAIN PASS · SOURCE-TASK **RED** (R5-T1-a).
- In neither task's own world does a scored value have a second answer.

**Round-4 REDs**

| Item | Status |
|---|---|
| R4-1 | closed (extended policy withdrawn; base decides; ledger-established in task 0) |
| R4-2 | closed (cap counts posted rows, matching the frozen parameter and measure) |
| R4-3 | closed at the rule level (current cycle only; same-cycle refunds) |

**New REDs in round 5**
- **R5-1**, the new reactivation policy:
  - "same contact" is read as "posted on the current date", which is an undeclared override that is also wrong on non-business days;
  - "most recent" within a day cannot be established from any record.
- **R5-2**, the assessment and replenishment:
  - the scope conditions are not implemented in compute;
  - the replenishment's `compute_basis` attributes them to bindings that do not implement them.
- **R5-T1-a**, a stale quotation in task 1's argument-uniqueness proof.

**Coverage, scope and uuid8s**
- 6 extended policies (task 0: proceeds, reactivation, conversion + the workflow; task 1: funding refund, assessment, replenishment).
- The two scopes are disjoint.
- There is exactly one workflow task, and its gold actions carry `requires_external_wait: false` and a `zero_wait_proof`.
- 7 task tools, each used once in GT. `refund_savings_maintenance_fee_bf99bb2f` is now base-governed.
- uuid8s are unchanged.

**Problem trees**
- **Task 0:** the chain conversion ← reactivation ← transfer.
  - 2 declared prerequisites and 1 value_input edge, acyclic.
  - Every edge bears weight.
  - The undeclarable base refund also bears weight (R5-O2).
  - The opening-world value, MMA, differs from gold, PCMM.
- **Task 1:** unchanged, 3 value_input edges.
- The difficulty-wide graph is a DAG.

**Gates**
- The round-5 snapshot is all OK, and the artifact hashes equal the MANIFEST. I did not run the gates myself.

**Not charged (blueprint):** R3-B1, S2r2, R5-B2.

**Difficulty verdict (revision_5): does not pass the source-layer audit** (R5-1, R5-2, R5-T1-a).

## revision_6

### charter_global_frozen (revision_6)

- **Auditor:** same, round-6 re-audit. The authoritative freeze is the sha256 record in each task's revision_6 comparison, taken before any round-6 GT was read.
- **Inputs, re-hashed 2026-09-12T23:21:34Z:**
  - `savings.extended.yaml` = `626b64be6978477977fca6f975432aa309887ad0720faad9e91515d4d8986142` (changed). The exact diff against my round-5 snapshot is `scratchpad/policy_audit_swit/extended_r5.yaml` → `extended_r6.yaml`. Every section below is re-derived in full.
  - `task_tools.py` = `0dcd69b7…` (unchanged). The blueprint is unchanged. The views `311ec093…` / `89e3ac50…` are unchanged.
- **Base copy:** verbatim.
- **Entry conditions:** the gate snapshot (all OK) and the views were supplied.
- **Criteria:** the same as revision 5:
  - rule ↔ compute, checked in both directions;
  - record-establishability;
  - frozen base parameter, event and measure text;
  - whole-domain retirements;
  - same-day, weekend and cycle-boundary constructions.
- **contamination_disclosure:** I have seen round-1 to round-5 GT of both tasks and the KB revision-1 reports. I have not read the round-6 task JSONs. No GT is used here.

### policy_conflict_scan (revision_6)

Exact diff against round 5:

- **(a) proceeds transfer.** The certificate is the counterparty of the internal-transfer deposits on their latest posting date (`d_in`), taken only when every such deposit that day has one counterparty (`same_cp`). The rule says: "When internal-transfer deposits from different accounts posted on that most recent date, the records do not show which of them is the most recent, and nothing is moved under this policy."
- **(b) reactivation.**
  - "That the transfer was made in this contact is established from the contact itself, where the owner makes it, not from the ledger; it is a condition for reactivation under this policy, and the computed reactivation date does not test it."
  - The date is "the latest posted_date among the account's withdrawals with those three channels, which is that transfer's posted date, a business day as the withdrawal's posted_date always is".
  - It is established "only when exactly one withdrawal with those three channels posted on that date and its counterparty is a checking account of the same customer".
  - Compute: `d_tel`/`d_onl`/`d_mob` → `d` = MX, `n_on_d`, `cp`, `own`, `result = d if dormant and n_on_d == 1 and own else ''`.
  - The edge to proceeds is now `value_input`, gate `d`.
- **(c) funding refund.** `d_out`, `n_out`; `fund_cp` only when exactly one internal-transfer withdrawal posted on `d_out`.
- **(d) assessment and (e) replenishment.**
  - `od_d` / `od_same`: when OD transfers to different accounts share the latest date, nothing is done.
  - Scope conditions are restated as "each read from the records and each a condition for applying the policy that the computed fee [amount] does not test". The `compute_basis` of `cyc` and `refunds` is narrowed to the formula sentences.
  - The assessment adds conditions:
    - every bank_error-refunded fee "sits on a withdrawal that is not a counted withdrawal beyond the allowance";
    - "no other counted withdrawal posted on the same day as the withdrawal that would take the fee, since the records do not order withdrawals within a day".
- **(f) conversion and workflow:** unchanged.
- **Scope split:** unchanged. No overwrite exists anywhere (`overwrite: []` on all six policies), so there are no whole-domain retirements.

### rule_compute_equivalence (revision_6)

- **Mechanical checks:**
  - every `compute_basis` sentence and every `policy_source` is verbatim;
  - no basis lacks a binding;
  - every `value_input` gate (`d`, `active`, `voided`, `fees_net`) is a compute binding.
- **Probes** (`scratchpad/policy_audit_swit/constructed_r6.py`; each same-day case run in both row orders):
  - **P1 proceeds.** An internal-transfer deposit from checking was added on the same 2026-08-25 as the CD payout. Result 0.00 in both orders, matching "nothing is moved".
  - **P4 funding refund.** A second internal-transfer withdrawal on 2026-08-28. Result 0.00 in both orders.
  - **P5 assessment / replenishment.** OD transfers to two different checking accounts on 2026-09-09. Results 0 / 0.
  - **Self-found row-order fixes: verified.**
- **Reactivation:**
  - **P2a (opening world):** the compute returns '2024-08-12', the online transfer of 2024-08-12 to own checking. The rule's in-contact condition, which lies outside the value, fails, so there is no reactivation. The rule is consistent, because it declares that condition outside the computed date, as the round-3 conversion cap was.
  - **P2b (after the in-contact transfer):** '2026-09-11'.
  - **P2c (online transfer that morning plus in-contact telephone transfer, same date):** '' in both orders. The rule gives "no reactivation date is established under this policy". Base `savings_evt_dormancy` still governs, and its date is the same 2026-09-11. See R6-O1.
- **Scope conditions** of assessment and replenishment: they are now declared in the rule as record-read conditions the computed value does not test, and no `compute_basis` claims to implement them. They are therefore equivalent by the round-3 standard.
- **Record-establishability:**
  - reactivation "made in this contact": established from the contact (transcript tool call);
  - "exactly one … on that date": ledger;
  - current cycle: `frozen_time` + `statement_cycle_day`;
  - refund source cycle: `source_item_id`;
  - **the placement of an existing excess fee "on a counted withdrawal beyond the allowance": not establishable when that withdrawal shares a day with another counted withdrawal at the allowance boundary.** See R6-2.
- **Weekend construction:** R6-1.
- **Cycle-boundary construction:** R6-O2.

### action_binding_and_uuids (revision_6)

Unchanged from revision 5 and carried forward by reference.

### prerequisite_graph (revision_6)

- Edges:
  1. conversion ← reactivation (`value_input` `active`)
  2. reactivation ← proceeds (`value_input` `d`)
  3. assessment ← funding refund (`voided`)
  4. replenishment ← assessment (`fees_net`)
  5. replenishment ← funding refund (`fees_net`)
- The graph is acyclic.
- Every `policy_source` is verbatim.
- **R5-O1 closed:** edge 2's gate is now the compute binding `d`.
- R5-O2 still stands: the base refund prerequisite of the conversion cannot be declared.

### override_declarations (revision_6)

- No `overwrite` entries.
- Sentence sweep of the new text against `base_policy_refs` and frozen text:
  - reactivation "that transaction's posted date becomes the new last_customer_activity_date" agrees with base `savings_evt_dormancy` ("its date"), event `savings_reactivate` ("the date of the reactivating transaction") and the schema field meaning ("Posted date of the latest customer-initiated transaction"). The same-contact condition agrees with base, so **R5-1(a) is closed**.
  - "a business day as the withdrawal's posted_date always is" agrees with base event `savings_withdrawal.posted_date` ("Business day the withdrawal posted") but contradicts the transfer tool's contract ("dated today"); see R6-1.
  - The assessment's cap text is unchanged from round 5 and still agrees with the frozen parameter and measure.

### findings (revision_6)

**Round-5 items**

| Item | Status | Basis |
|---|---|---|
| R5-1(a) same-contact proxy | closed | now a stated condition established from the contact, outside the computed value |
| R5-1(b) intra-day "most recent" | closed | exactly-one-per-day requirement; P2c is order-independent |
| R5-1 weekend limb | **not closed; transformed** | see R6-1 |
| R5-2 | closed | conditions declared outside the computed value; `compute_basis` narrowed |
| R5-O1 | closed | |

**R5-T1-a / R5-T1-O1** are task-file items, checked after the reveal in `1.md`.

**R6-1 — SOURCE-POLICY RED (charter; weekend limb of R5-1 carried forward). On a non-business day the reactivation date has two readings.**
- **Passage A** (ext reactivation rule, with frozen base event field `savings_withdrawal.posted_date` "Business day the withdrawal posted"): "the reactivation date is … that transfer's posted date, a business day as the withdrawal's posted_date always is".
- **Passage B** (the transfer tool contract, `transfer_savings_to_checking_5f60835b` docstring and body): "One call posts one withdrawal on the savings account, dated today", with `posted_date=ctx.now()[:10]`. The ext compute `d` reads that record.
- **Probe P3:** a contact on Saturday 2026-09-12.
  - B and the compute give reactivation date **'2026-09-12'**, a non-business day, which contradicts A's own assertion.
  - A with the base field says the withdrawal posts on the business day **2026-09-14**, so the reactivation date is 2026-09-14.
  - `reactivation_date` is a scored argument, so this is two answers.
- **Root cause:** a tool-contract/base-field conflict present since round 1. It becomes scored-relevant here because the round-5/6 reactivation date is read from `posted_date`, and the round-6 rule asserts the base side.
- **Affected:** `extended_policies[savings_ext_same_contact_reactivation].rule` ("a business day as the withdrawal's posted_date always is") and `compute[d]`, together with `task_tools.py` `transfer_savings_to_checking_5f60835b` ("dated today").
- **Bears on task 0.**

**R6-2 — SOURCE-POLICY RED (charter; new text in round 6). An assessment applicability condition depends on intra-day order, which no record holds.**
- **Passage A** (rule): "This policy is applied only when … every excess withdrawal fee of the cycle that has not been refunded as bank_error sits on a counted withdrawal beyond the allowance, and every one that has been refunded as bank_error sits on a withdrawal that is not a counted withdrawal beyond the allowance … and no other counted withdrawal posted on the same day as the withdrawal that would take the fee, since the records do not order withdrawals within a day."
- The same-day guard covers only the withdrawal that would take the *new* fee. Whether an *existing* fee sits "beyond the allowance" depends on its withdrawal's place "in posting order". The rule itself says records do not hold that order within a day.
- **Probe P6:** task 1's ledger, with the telephone transfer moved to 2026-09-09 so that it and the 2026-09-09 OD transfer are counted #6/#7. An existing 10.00 fee sits on the OD transfer. The erroneous fee is refunded as bank_error. An 8th counted withdrawal is on 2026-09-10.
  - If the OD transfer is #7, its fee is correctly placed, the condition holds and owed = 2 − 1 = 1, so **10.00** on #8.
  - If it is #6, its unrefunded fee sits within the allowance, the condition fails and **nothing** is reconciled.
  - The records cannot decide between the two.
  - The compute gives 10.00, because it does not test the condition, by declaration.
- **Affected:** `savings_ext_counted_withdrawal_fee_assessment.rule`, last sentence.
- **Bears on task 1.** The same-day intra-day-order gap also exists in base's "in posting order" (R2-O2); here the extended text states it as its own applicability condition.

**Observations (no two-passage contradiction):**
- **R6-O1:** with two qualifying withdrawals on one date, one of them made in the contact, the extended policy establishes no date. Base reactivation still applies, with the same date. The extended policy's refusal is only an unnecessary narrowing.
- **R6-O2:** on a cycle closing date, "the cycle that closes on the next statement cycle closing date" could be read as today's cycle or the following one. The primary term "current statement cycle" and base's inclusive window ("through the cycle closing date") resolve it to today's cycle. Neither task's clock is on a closing date: task 0 is 2026-09-11 with cycle day 10, task 1 is 2026-09-10 with cycle day 20.
- **R6-O3:** on a world without an in-contact transfer, the reactivation compute returns an old date ('2024-08-12' in task 0). This is consistent only because the in-contact condition is declared outside the value. A compute-only replay of "skip the transfer" therefore reactivates with 2024-08-12 and converts to PCMM.
- **Carried:** R5-O2, R3-O1, R3-O2, R2-O1, R2-O2.
- **Blueprint, not charged:** R3-B1, S2r2, R5-B2.

**No regression:** R2-1 to R2-4, R4-1, R4-2 and R4-3 remain closed, and conversion and workflow are unchanged.

No round-6 GT was used in this section.

### closing_checklist (revision_6)

Written after both round-6 reveals (2026-09-12T23:27:12Z). Nothing above this heading in revision_6 was edited after the reveal, and revisions 1–5 are untouched.

- **Per-task files.**
  - `0.md` and `1.md` each carry `## revision_6`, frozen and hashed at 23:26:59Z.
  - Contamination is disclosed in both, so neither is a blind audit.
  - Every value equals the round-6 GT.
- **Revision_6 verdicts:**
  - Task 0: **SOURCE-POLICY RED** (charter R6-1) · SOURCE-CHAIN PASS · SOURCE-TASK PASS.
  - Task 1: **SOURCE-POLICY RED** (charter R6-2) · SOURCE-CHAIN PASS · SOURCE-TASK PASS.
  - Neither task's own world yields a second answer.
- **Round-5 REDs:**

| Item | Status |
|---|---|
| R5-1(a) | closed |
| R5-1(b) | closed |
| R5-2 | closed |
| R5-T1-a | closed |
| R5-O1 | closed |
| R5-T1-O1 | closed |
| R5-1 weekend limb | not closed; now R6-1 |

- **Self-found same-day fixes:** verified order-independent (P1, P4, P5).
- **New in round 6:** R6-2, an existing fee's placement "beyond the allowance" that cannot be established from records when two counted withdrawals share a day at the allowance boundary.
- **Coverage, scope, single workflow, uuid8s, 7 tools:** unchanged. All zero-wait fields are present.
- **Trees:**
  - Task 0: chain of 2 value_input edges, plus the undeclarable base refund. The opening value (MMA) differs from gold (PCMM).
  - Task 1: 3 value_input edges.
  - Acyclic difficulty-wide.
- **Gates:** snapshot all OK; artifact hashes equal the MANIFEST. Not run by me.
- **Not charged (blueprint):** R3-B1, S2r2, R5-B2.
- **Difficulty verdict (revision_6): does not pass the source-layer audit** (R6-1, R6-2).

## revision_7

### charter_global_frozen (revision_7)

- Auditor: the same auditor, round-7 re-audit. The authoritative freeze is the sha256 record in each task's revision_7 comparison, taken before any round-7 GT was read.
- Inputs, re-hashed 2026-09-12T23:42:22Z:
  - `savings.extended.yaml` = `d1554074e8d8492c24c67236921da5c397d53f26a1da921dc23de370957ddd44` (changed; diff against `extended_r6.yaml`: 3 hunks, all below).
  - **`task_tools.py` = `98c8ca803114b1106a48da5c7c413a398a42aca28cb530a1cac6a90a9dd98820` (changed).** Snapshot at `scratchpad/policy_audit_swit/task_tools_r7.py`. The tool-contract section is re-derived below.
  - Blueprint unchanged. Views `311ec093…` / `89e3ac50…` unchanged.
- Base copy: verbatim.
- Entry conditions: gate snapshot (all OK) and views supplied.
- Criteria: as in revision 6.
- contamination_disclosure: I have seen GT for rounds 1–6 of both tasks. The round-7 task JSONs are unread. No GT is used here.

### policy_conflict_scan (revision_7)

Changes since round 6:

- **(a) reactivation rule.** It now adds: "a transfer made on a Saturday, Sunday or Federal Reserve holiday posts on the next business day, and that posted date is the reactivation date".
- **(b) assessment conditions.** The ordering condition is replaced by "no two counted withdrawals of the cycle posted on the same day, as their posted_date shows, so that the posting order of the counted withdrawals, which the records do not hold within a day, follows from their posted dates alone". Fee placement is now stated "in that posting order".
- **(c) workflow scenario.** It now reads "active with the posted date of the owner's transfer, the business day it posts".
- **(d) task_tools.py, transfer tool.**
  - The docstring now says: "The withdrawal's posted date is the business day it posts: today when today is a business day (Monday through Friday, other than a Federal Reserve holiday), otherwise the next business day". The `statement_cycle` argument is now "the statement cycle that contains the withdrawal's posted date". The receipt's `posted_date` is "the business day the withdrawal posted".
  - The body steps forward from `ctx.now()` to the first Mon–Fri that is not a Federal Reserve holiday. The holidays are 5 fixed dates with Sunday→Monday observance, plus MLK, Presidents, Memorial, Labor, Columbus and Thanksgiving.
  - The two refund tools and the fee tool are **unchanged**. Each still says "dated today" and writes `posted_date=ctx.now()[:10]`. The refund tools' `statement_cycle` is still "the YYYY-MM month in which the account's current statement cycle closes".
- **Everything else is unchanged:** proceeds, conversion, funding refund, replenishment, and all compute blocks.

### rule_compute_equivalence (revision_7)

- **Mechanical checks.** Every basis and every `policy_source` is verbatim. The compute blocks are identical to round 6.
- **Assessment (R6-2 probe P6).** A world with two counted withdrawals on the same day now fails the stated condition, so "nothing is reconciled" is the rule's single answer. The compute (10.00) does not test the condition, by declaration, as in round 6. Placement "in that posting order" is determined by dates once the condition holds. **R6-2 closed.**
- **Reactivation on a weekend.** Probe (`constructed_r7.py`): a Saturday 2026-09-12 contact. The tool posts 2026-09-14, and the reactivation compute gives '2026-09-14'. The rule sentence, the base field "Business day the withdrawal posted" and the tool now all give 2026-09-14. **R6-1 closed.**

### action_binding_and_uuids (revision_7): tool contracts re-derived

- **Names, uuid8s, owners and (target_tool, computes) pairs:** unchanged. There are still no precondition checks in any body. The transfer tool's posting-date loop is a posting convention, not a business gate.
- **Transfer tool date logic.** I ran the real function body under a stub context in `constructed_r7.py`:

| Input date | Posted date | Why |
|---|---|---|
| 2026-09-11 (Fri) | 2026-09-11 | business day |
| 2026-09-12 (Sat) | 2026-09-14 | weekend |
| 2026-09-13 (Sun) | 2026-09-14 | weekend |
| 2026-09-07 | 2026-09-08 | Labor Day |
| 2026-10-12 | 2026-10-13 | Columbus Day |
| 2026-05-25 | 2026-05-26 | Memorial Day |
| 2026-11-26 | 2026-11-27 | Thanksgiving |
| 2026-12-25 (Fri) | 2026-12-28 | Christmas |
| 2027-01-01 (Fri) | 2027-01-04 | New Year's Day |
| 2027-06-19 (Sat) | 2027-06-21 | Monday is correctly not observed; the Fed does not move Saturday holidays |
| 2022-06-19 (Sun) | 2022-06-21 | Monday 06-20 is observed |

  The convention matches the scenario's own definition elsewhere ("Business days are Monday through Friday excluding Federal Reserve holidays", checking and auto charters).
- **Refund tools `bf99bb2f` / `774e6cc0` and fee tool `aafc1fb2`.** These still post "dated today", against base `savings_fee_refund.posted_date` ("Business day the refund posted") and `savings_fee.posted_date` ("Business day the fee posted"). The reworker argues that no extended compute or scored value reads their posted date. That is true of `posted_date` itself. It is not true of what the posting-day convention decides. See R7-1.

### prerequisite_graph (revision_7)

Unchanged from revision 6. Five edges: the gates are `active`, `d`, `voided` and `fees_net` (two edges use `fees_net`). The graph is acyclic and every `policy_source` is verbatim.

### override_declarations (revision_7)

No `overwrite` anywhere. The new reactivation weekend sentence agrees with base `savings_withdrawal.posted_date`, and the new assessment condition names no base sentence. The frozen-text conflict is R7-1, which sits in the tool contracts and the funding-refund rule.

### findings (revision_7)

**R6-1 closed** (reactivation date on non-business days). **R6-2 closed** (same-day ordering is now an applicability condition decided from dates).

**R7-1 — SOURCE-POLICY RED (charter; the refund and fee tools left "dated today"; same class as R6-1).**

A refund or fee made on a non-business day has two posting conventions, and the convention decides a scored `statement_cycle` that the extended computes consume.

- **Passage A (frozen base).**
  - `savings_fee_refund.posted_date`: "Business day the refund posted."
  - `savings_fee_refund.statement_cycle`: "Statement cycle in which the refund posted."
  - `savings_fee.posted_date`: "Business day the fee posted."
  - Measure `savings_msr_cycle_excess_fees`: counted "by posted_date".
- **Passage B.**
  - Tools `refund_savings_withdrawal_fee_774e6cc0` / `refund_savings_maintenance_fee_bf99bb2f`: "One call posts one refund credit, dated today". Their `statement_cycle` argument is "the YYYY-MM month in which the account's current statement cycle closes".
  - Tool `assess_savings_withdrawal_fee_aafc1fb2`: "posts one fee debit, dated today".
  - The funding-refund rule: the refund is "posted in the current statement cycle".
- **Constructed situation.** This is task 1's own ledger with the clock set to **Saturday 2026-09-19** (`constructed_r7.py`). Cycle 2026-09 closes Sunday 2026-09-20, and the next business day, Monday 2026-09-21, lies in cycle 2026-10. The owed bank_error refund of the 15.00 erroneous fee is made in the contact.
  - Passage B: the refund is dated 2026-09-19 with `statement_cycle` **"2026-09"**. The assessment's `voided` counts it, and the assessment is **10.00**.
  - Passage A: the refund posts on business day 2026-09-21, so its cycle is **"2026-10"**. The 2026-09 fee then stands unrefunded within the reconciled cycle. The stated condition ("every excess withdrawal fee of the cycle that has not been refunded as bank_error sits on a counted withdrawal beyond the allowance") fails, so **nothing is reconciled**. Probe: compute = **0** under that labelling.
  - The refund's `statement_cycle` is a scored argument. It is also a value input: edge 3 (`voided`) and edge 5 (`fees_net` via `refunds`) read it.
- **Second limb, fee tool.** A fee assessed on Saturday 2026-09-19 for a 2026-09 withdrawal is dated 2026-09-19 by the tool, but under base it posts on 2026-09-21. The ext rule says fee rows count toward the maximum "as savings_msr_cycle_excess_fees counts them". That measure counts by `posted_date` window, which puts the fee in cycle 2026-10. The ext's `fee_rows` counts by the `statement_cycle` field, which puts it in 2026-09. So the stated identity with the measure fails at the cycle boundary.
- **Root cause.** The rework applied the base business-day posting convention to the transfer tool only.
- **Affected.**
  - `task_tools.py`: `refund_savings_maintenance_fee_bf99bb2f`, `refund_savings_withdrawal_fee_774e6cc0`, `assess_savings_withdrawal_fee_aafc1fb2` (docstrings "dated today"; refund `statement_cycle` args; bodies `posted_date=ctx.now()[:10]`).
  - `savings_ext_certificate_funding_fee_refund.rule`: "posted in the current statement cycle".
- **Bears on task 1**, through tools 774e6cc0 and aafc1fb2 and the funding-refund rule. **Bears on task 0** through tool bf99bb2f; its base-refund `statement_cycle` has the same two readings on a weekend or holiday before a cycle close.

**Observation R7-O1: charter level, workflow zero-wait on non-business days.** On a weekend or holiday contact, the owner's transfer posts on the next business day. The workflow then reactivates and converts in the same contact on a transfer that has not yet posted in real time. The conversion rule says "the balance after that transfer has posted", and base's posting is a future business-day event. So the workflow is zero-wait only on business days. Zero-wait is judged per task, and task 0's clock (Friday 2026-09-11, a business day) is unaffected. Recorded as an observation.

**Carried:**
- Observations: R6-O1, R6-O2, R6-O3, R5-O2, R3-O1, R3-O2, R2-O1, R2-O2.
- Blueprint items: R3-B1, S2r2, R5-B2.

**No regression** of R2-x, R4-x, R5-x or the round-6 same-day fixes. Their text and compute are unchanged.

No round-7 GT was used in this section.

### closing_checklist (revision_7)

Written after both round-7 reveals at 2026-09-12T23:46:41Z. Nothing above this heading in revision_7 was edited after the reveal. Revisions 1–6 are untouched.

**Per-task files.** `0.md` and `1.md` each carry `## revision_7`, frozen and hashed at 23:46:29Z. Contamination is disclosed in both; neither is a blind audit. Every value equals the round-7 GT.

**Revision_7 verdicts.** Neither task's own world yields a second answer.
- Task 0: **SOURCE-POLICY RED** (charter R7-1, via refund tool `bf99bb2f`) · SOURCE-CHAIN PASS · SOURCE-TASK PASS.
- Task 1: **SOURCE-POLICY RED** (charter R7-1, via tools `774e6cc0`/`aafc1fb2` and the funding-refund rule) · SOURCE-CHAIN PASS · SOURCE-TASK PASS.

**Round-6 REDs.**
- R6-1: **closed.** The transfer tool now posts on the business day. The rule states the weekend and holiday case. The tool, the rule and the base field agree. The tool's holiday logic is verified on 11 dates.
- R6-2: **closed.** Same-day counted withdrawals now make the policy inapplicable, and the posting order follows from dates.

**Reworker's decision to leave the refund and fee tools "dated today".** This does **not** hold under the criteria (R7-1). On a weekend or holiday before a cycle close, the posting convention decides the refund's scored `statement_cycle`. That value feeds `voided` and `refunds`, and the constructed probe gives 10.00 against nothing. It also breaks the stated identity between `fee_rows` and `savings_msr_cycle_excess_fees`.

**Coverage, scope, workflow, uuid8s.** All unchanged: six extended policies, disjoint scopes, one workflow task with zero-wait fields present, seven tools each used once, uuid8s unchanged. The tool module changed only in the transfer tool's posting-date logic and wording.

**Problem trees.** Unchanged and holding.

**Gates.** The snapshot is all OK, and the artifact hashes equal the MANIFEST. I did not run them myself.

**Not charged.**
- Blueprint: R3-B1, S2r2, R5-B2.
- Charter observation: R7-O1 (the workflow is zero-wait only on business days).

**Difficulty verdict (revision_7): does not pass the source-layer audit** (R7-1).

## revision_8

### charter_global_frozen (revision_8)

- Auditor: the same auditor, round-8 re-audit. The authoritative freeze is the sha256 record in each task's revision_8 comparison, taken before any round-8 GT was read.
- Inputs, re-hashed 2026-09-12T23:58:50Z:
  - `savings.extended.yaml` = `7e8da8bb5534aa2e5ea62945dd524f31d6ffce58f38db4f2e9cd05a5bc8cf09e` (changed). Snapshot: `scratchpad/policy_audit_swit/extended_r8.yaml`.
  - `task_tools.py` = `6b58a78be39e9393fc6f6f1366c7bd0deb6dfcfa65a6d0e113064925a38f9cce` (changed). Snapshot: `task_tools_r8.py`.
  - Exact diffs against the round-7 snapshots were reviewed in full.
  - Blueprint unchanged. Views `311ec093…` and `89e3ac50…` unchanged.
- Base copy is verbatim. The gate snapshot (all OK) and the views were supplied.
- Criteria are as in revision 7.
- contamination_disclosure: I have seen round-1 to round-7 GT. I have not read the round-8 task JSONs. No GT is used in this section.

### policy_conflict_scan (revision_8)

Changes since round 7:

- **(a) tools.** `refund_savings_maintenance_fee_bf99bb2f`, `refund_savings_withdrawal_fee_774e6cc0` and `assess_savings_withdrawal_fee_aafc1fb2` now use the transfer tool's business-day posting loop.
  - Their docstrings: "The refund's [fee's] posted date is the business day it posts: today when today is a business day (Monday through Friday, other than a Federal Reserve holiday), otherwise the next business day".
  - The refund tools' `statement_cycle` is "the statement cycle that contains the refund's posted date".
  - The fee tool's `statement_cycle` still means "the statement cycle the fee belongs to", the withdrawal's cycle, as in base `savings_fee.statement_cycle`.
  - Every receipt now returns `posted_date`.
- **(b) reactivation.**
  - Rule: "A transfer made on a Saturday, Sunday or Federal Reserve holiday posts on the next business day, after the contact, so it has not posted within the contact: the date is established under this policy only when that posted date is not after the frozen date".
  - Compute: new binding `not_after_contact: "d <= NOW"` in `result`.
- **(c) conversion.** New condition, declared outside the computed target: "applied only when no transaction on the account has a posted_date later than the frozen date … until it has posted no target is chosen under this policy".
- **(d) funding refund.** "…it posts on the business day it is made … and its statement_cycle is the statement cycle that contains that posted date". This replaces "posted in the current statement cycle".
- **(e) assessment.** New conditions, each record-read and outside the computed fee:
  - the frozen date is a business day;
  - fee rows by `posted_date` window equal fee rows by `statement_cycle`, "so that the fee rows of the cycle are the rows savings_msr_cycle_excess_fees counts";
  - every bank_error refund of a fee of the cycle posted in the cycle.
- **(f) replenishment.** New condition: "no transaction on the account has a posted_date later than the frozen date".
- **(g) workflow.** Scoped "in one contact on a business day". The `order_rationale` states the non-business-day case.
- **Unchanged:** proceeds, all other compute blocks, the scope split, and the prerequisite graph.

### rule_compute_equivalence (revision_8)

**Mechanical checks.**
- Every basis is verbatim, including the new `not_after_contact` basis.
- Every `value_input` gate is a binding.
- Every `policy_source` is verbatim.

**Probes** (`scratchpad/policy_audit_swit/constructed_r8.py`; real tool bodies under a stub context):

| Date | transfer | refund_mm | refund_xw | assess |
|---|---|---|---|---|
| Thu 2026-09-10 | 09-10 | 09-10 | 09-10 | 09-10 |
| Fri 2026-09-11 | 09-11 | 09-11 | 09-11 | 09-11 |
| Sat 2026-09-19 | 09-21 | 09-21 | 09-21 | 09-21 |
| Labor Day 2026-09-07 | 09-08 | 09-08 | 09-08 | 09-08 |
| Thanksgiving 2026-11-26 | 11-27 | 11-27 | 11-27 | 11-27 |
| Sunday Juneteenth 2022-06-19 | 06-21 | 06-21 | 06-21 | 06-21 |

**Reactivation.**
- Saturday 2026-09-12 contact, transfer posted 2026-09-14: `''`. This matches "no reactivation date is established under this policy".
- Friday 2026-09-11 (task 0 world): '2026-09-11'.

**R7-1 world** (task 1 ledger, Saturday 2026-09-19).
- The refund tool now posts 2026-09-21 with `statement_cycle` "2026-10". That is its single reading, matching base "Business day the refund posted" / "Statement cycle in which the refund posted". The funding-refund rule now says the same.
- The assessment's rule says the frozen date is not a business day, so nothing is reconciled. The compute gives 0, which is not a contradiction in any case.
- The replenishment's rule sees a posted_date after the frozen date, so no amount.
- The two readings of R7-1 no longer exist.

**Fee-row identity (R7-1 second limb).** The new assessment condition makes fee rows by field equal fee rows by the measure's `posted_date` window whenever the policy applies. On a non-business day the policy does not apply. **Closed.**

**Record-establishability.** Every new condition is readable from `frozen_time`, the business-day calendar the tools and rules state, `posted_date`, `statement_cycle` and `source_item_id`. None depends on unrecorded history or intra-day order.

### action_binding_and_uuids (revision_8): tool contracts re-derived

- Names, uuid8s, owners and (target_tool, computes) pairs are unchanged. Each pair is claimed by at most one policy.
- The only body change is the posting-date loop, now in all four posting tools. It is a posting convention, not a business precondition. No tool refuses, validates or hints.
- Every docstring agrees with the base event fields (`posted_date` "Business day the … posted"; refund `statement_cycle` "cycle in which the refund posted"; fee `statement_cycle` "cycle the fee belongs to") and with the extended rules.

### prerequisite_graph (revision_8)

Unchanged, and acyclic. The value_input gates are `active`, `d`, `voided` and `fees_net` (×2). Every `policy_source` is verbatim.

### override_declarations (revision_8)

- There is no `overwrite` anywhere.
- The new sentences agree with base `savings_withdrawal`, `savings_fee` and `savings_fee_refund` field text, the dormancy rule, and the measure `savings_msr_cycle_excess_fees`.
- Nothing is retired anywhere in the domain.

### findings (revision_8)

**Round-7 items:**

| Item | Status | Basis |
|---|---|---|
| R7-1 | **Closed** | Both limbs; the tools, base fields and extended rules now reach one posting date and one `statement_cycle` on every day |
| R7-O1 | **Closed** | Reactivation tests "posted date not after the frozen date" in compute. The conversion and the replenishment require no future-dated posting, as record-read conditions. The workflow is scoped to business-day contacts, so no step rests on a posting that has not happened. |

**New findings:**
- No new RED.
- One new observation. On a non-business day, **R8-O1** leaves the extended reactivation, assessment, replenishment and conversion inapplicable. The owner's same-contact transaction could still reactivate under base `savings_evt_dormancy`, with its next-business-day posted date. This is the same general-plus-exception shape as R6-O1: no two-passage contradiction, only a narrowing.

**Carried observations:** R6-O1, R6-O2, R6-O3, R5-O2, R3-O1, R3-O2, R2-O1, R2-O2.

**Blueprint items, not charged:** R3-B1, S2r2, R5-B2.

**No regression** of the R2–R6 closures, re-confirmed on the unchanged compute blocks and probes.

No round-8 GT was used in this section.

### closing_checklist (revision_8)

Written after both round-8 reveals (2026-09-13T00:01:15Z). Nothing above this heading in revision_8 was edited after the reveal. Revisions 1–7 are untouched.

- **Per-task files.** `0.md` and `1.md` each carry `## revision_8`, frozen and hashed at 00:01:00Z before the reveal. Contamination is disclosed: neither is a blind audit, and every value comes from mechanical recomputation on the unchanged views. Every value equals the round-8 GT. Both comparison sections carry PASS.
- **Revision_8 verdicts.**
  - Task 0: SOURCE-POLICY PASS · SOURCE-CHAIN PASS · SOURCE-TASK PASS.
  - Task 1: SOURCE-POLICY PASS · SOURCE-CHAIN PASS · SOURCE-TASK PASS.
- **Round-7 items.** R7-1 and R7-O1 are closed.
  - All four posting tools now apply the base business-day convention. Their holiday logic was verified on six dates across all four tools.
  - The refund `statement_cycle` means the cycle that contains the posted date.
  - Conditions on the frozen date being a business day and on no future-dated posting are stated in the rules, and they are record-read.
  - The workflow is scoped to business-day contacts.
- **Regression.** None across rounds 2–7. Every earlier closure is re-confirmed on the unchanged compute blocks and probes.
- **Coverage and scope.**
  - The 6 extended policies are fully covered and split disjointly:
    - task 0: proceeds, reactivation, conversion, plus the single workflow;
    - task 1: funding refund, assessment, replenishment.
  - Exactly one workflow task. Its gold actions carry `requires_external_wait: false` and a `zero_wait_proof`.
  - The 7 task tools are each used once in GT. Each (target_tool, computes) pair is claimed at most once.
  - The uuid8s are the originals, independently generated and unchanged since round 1.
- **Problem trees.**
  - Task 0: the chain conversion ← reactivation (value_input `active`) ← transfer (value_input `d`), with the base refund also load-bearing (undeclarable; R5-O2). 2 declared prerequisites and 2 value_input edges. Every edge bears weight, and the opening value (MMA) differs from gold (PCMM).
  - Task 1: 2 prerequisite problems and 3 value_input edges. Every edge bears weight, and the opening value (542.55) differs from gold (537.55).
  - The difficulty-wide graph is a DAG with no cross-task edge.
- **Gates.** The round-8 snapshot (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK) applies to the audited forms, whose hashes equal the MANIFEST. I did not run the gates myself.
- **Open but not charged, blueprint level.** These are for a blueprint decision; none is consumed by an extended policy or by a scored value in either world.
  - R3-B1: the automatic-transfer channel, trigger against rule and measure.
  - S2r2: single-transfer against sum wording.
  - R5-B2: the base cycle-close linked-checking waiver, which records cannot establish once the tier or status may have changed.
- **Observations**, none of them grounds for rework: R8-O1, R6-O1, R6-O2, R6-O3, R5-O2, R3-O1, R3-O2, R2-O1, R2-O2, and the task-level carried observations.

**Difficulty verdict (revision_8): passes the source-layer audit.** Policy self-consistency, problem tree and unique solution PASS for both tasks.
