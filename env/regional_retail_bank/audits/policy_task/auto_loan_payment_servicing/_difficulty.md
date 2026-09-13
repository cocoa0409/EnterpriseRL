# Policy-task audit — auto_loan_payment_servicing / charter-global

## charter_global_frozen

- Round: revision 1 (first audit of this difficulty; no earlier revision exists under this directory).
- Freeze time: 2026-09-12T20:11Z (written before any task's GT was revealed; nothing in this section comes from a revealed GT field).
- Auditor: independent policy-task auditor (erl-task-policy-audit). I did not write any of these artifacts.
- Frozen inputs (sha256):
  - `env/regional_retail_bank/tasks/auto_loan_payment_servicing/auto.extended.yaml` = `c462c9699c9f8a8f1f71c5a82d817369dfd211db35de3ac6c9a022a9a87c814d`
  - `env/regional_retail_bank/tasks/auto_loan_payment_servicing/task_tools.py` = `ff9b197c57b9acc34fe53b21b838b4f7226773261ddc60388d8a81bc80ec9f4d`
  - The hashes match the orchestrator's MANIFEST.txt.
- Other inputs read: `blueprint/blueprint.yaml` (difficulty entry, lines 131-155), `blueprint/products/auto.yaml`, `blueprint/share_tools.py`, `erlbench/scoring.py`, `erlbench/determinism.py` (make_id), and the DSL evaluator in `skills/erl-task-instantiate/scripts/check_compute.py` (lines 141-308, which say what RND/DAYS/LATEST/CFIELD/EXISTS mean).
- Fields I could read: the charter and the tool module in full. Fields masked for every task until all derivations are frozen: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure`, `db_closure_matches_initial_state`.
- Entry conditions (Step 0): the brief includes the gate snapshot. All seven instantiation gates exited 0: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE. check_traceability is deferred by design. The brief also includes the masked views with their hashes. I recomputed the view hashes: `task_0.visible.json` = d48b2c07…, `task_1.visible.json` = e12a670e…, both matching. Input is complete.

### Base copy verbatim check

The command `diff blueprint/products/auto.yaml <(head -1365 auto.extended.yaml)` shows one difference: a single trailing blank line. Lines 1-1364 of the extended charter (the parameter schema, variants, events, measures and the base `policies`) are byte-identical to the scenario constitution. The base copy is verbatim.

### policy_conflict_scan

The structured surface is 13 base policies, 6 `extended_policies` and 1 workflow. Overlaps between extended policies and between extended and base:

| Subject / quantity | Policies touching it | Compatible? |
| --- | --- | --- |
| `auto_payment` scheduled split (`principal_portion`) | base `auto_evt_payment_allocation`, ext `auto_ext_catchup_installment_payment` | Compatible, with the charter observations O2, O3, O4 and O7 below |
| `auto_payment` payoff (`amount`) | base `auto_evt_payoff_and_lien`, base `auto_evt_payment_allocation`, ext `auto_ext_payoff_settlement` | Compatible (O5 and O6 are latent) |
| `auto_set_autopay` `interest_rate` on cancel | base `auto_agg_relationship_discount`, base `auto_evt_autopay`, ext `auto_ext_autopay_cancel_rate` | Compatible on every reachable parameter set (O8) |
| `auto_set_autopay` `interest_rate` on enrol, plus enrolment legality | base `auto_agg_relationship_discount`, base `auto_evt_autopay`, ext `auto_ext_autopay_enroll_rate` | **Conflict. One clause is declared; another base sentence governing the same quantity is not (F1)** |
| `auto_fee_waiver` bank_error on a returned-payment fee | base `auto_evt_fee_waiver`, base `auto_evt_returned_payment`, base `auto_evt_autopay`, ext `auto_ext_closed_source_returned_fee_waiver` | Additive. The base bank_error list is open ("such as"). The premise is not grounded in base (O9) |
| `auto_fee_waiver` bank_error on a late charge | base `auto_evt_fee_waiver`, base `auto_evt_late_charge`, ext `auto_ext_closed_source_late_charge_waiver` | Additive (O9) |
| `auto_change_due_date` | base `auto_due_date_change` only (workflow step 1, `computed_by: []`) | Base only |

- Triggers and time anchors. Every extended rate or amount uses one credit date, the clock date (`NOW`). The payoff and catch-up rules take the credit date from base's cutoff sentence without implementing the after-cutoff branch (O2). No extended policy moves a base time anchor: the late-charge grace, the due-date-change window and the lien deadline are untouched.
- Cross-category reads. All extended policies read only `checking` (status, ledger_balance, variant_name, opened_date, closed_date). The reads are declared in `cross_category`, and the base `auto_agg_relationship_discount` / `auto_evt_autopay` license them. Nothing reads outside the claimed categories.
- Terminal states. Payoff → `paid_off` with lien `release_pending`. The tool does this, matching base `auto_pay_off` and `auto_evt_payoff_and_lien`. No extended policy writes a terminal state that base forbids.
- Scope partition, from the charter alone. The extended policies fall into two disjoint trees:
  - {catch-up, cancel, enrol, and the workflow `auto_wf_autopay_source_change`}. Its root is the enrolment, with edges from catch-up and from cancel.
  - {returned-fee waiver, late-charge waiver, payoff}. Its root is the payoff, with two edges from the waivers.

  No policy belongs to both trees. There is no cross-tree edge. With M = 2, one task per tree covers all 6 extended policies and the workflow. After the reveal I check whether the tasks' actual claims match this (see closing_checklist).
- Event types claimed by the blueprint but carried by no extended policy or task tool: `auto_fee` (assessed only as a trigger), `auto_extend`, `auto_cancel_gap`, `auto_gap_refund`, `auto_release_lien`. This is an observation only (O10). The skill requires the extended policies to be covered, not every claimed event type.

### rule_compute_equivalence

This is check 2, run over all six extended policies. A script confirmed that every `compute_basis` value is a verbatim substring of its policy's `rule` (whitespace-normalised), and that every `compute_basis` key set equals its `compute` binding set.

- `auto_ext_catchup_installment_payment`. Each binding traces to its rule sentence: due, credited, returned_id, returned_credit, shortfall (MX 0), funds (active checking ledger_balance), amount (min), fees_due (ledger), fees_portion (MN), principal (ledger), accrued, interest_portion (MN), result. The rule makes no promise that compute leaves out. Gaps:
  - (a) Compute sets the credit date to `NOW` unconditionally. The rule says "through the credit date", and base defines the credit date by the 17:00 ET cutoff and business days (O2).
  - (b) `funds` = `CFIELD('checking','ledger_balance',status='active')` takes the first active account when there are several. The rule says "the borrower's checking account in active status", which also assumes there is exactly one (O3).
  - (c) `RND` is Python `round(float, n)`, per check_compute.py line 256. The rule says "rounded half-up". The two differ only at an exact half-cent tie (O4).
- `auto_ext_autopay_cancel_rate`. The bindings rec_auto, rec_rel, pre_rate, held_premier, held_private, rel_kept, kept, raw_rate and result each trace to a rule sentence. The `held_*` bindings take the first account of that tier via CFIELD, which is ambiguous when two accounts share a tier (O3). The rule's closing sentence ("rate_discounts is recorded as relationship when the relationship discount is kept and none otherwise") has no compute binding and no branch for `autopay_discount_removed_on_cancel = false`. Every variant sets that flag to true, so the gap is unreachable (O8).
- `auto_ext_autopay_enroll_rate`. The bindings are rule-grounded, with one gap. `source_active` = `EXISTS('checking', status='active')` checks that *any* active checking account exists, while the rule says "the paying account is a checking account of the borrower in active status". Compute does not bind the paying account (O7).
- `auto_ext_closed_source_returned_fee_waiver` and `auto_ext_closed_source_late_charge_waiver`. The bindings (fee_id / charge_id, the returned or debit payment, channel, debit_date, paying_account, source_closed, pcb_error, amount, prior_waivers, result) are rule-grounded both ways. Neither computes the `applied_to_principal` tool argument; it comes from the rule sentence "the part already paid from a payment is applied to principal". Both select only the *most recent* fee of their kind (see O5).
- `auto_ext_payoff_settlement`. The bindings principal, fees_due, days, accrued, penalty (0 because `prepayment_penalty_pct` = 0.00 in every variant), payoff, funds and result are rule-grounded. The portions (fees = fees_due, interest = accrued, principal = principal) come from the rule sentence. Gaps O2, O3 and O4 apply here too.

No compute invents a basis that has no rule sentence. The DSL gaps above (a single credit date, the first matching account, float rounding) do not change a value in either task world (see each task file).

### action_binding_and_uuids

- The `(target_tool, computes)` pairs are pairwise distinct: `(post_installment_payment_660c6229, principal_portion)`, `(cancel_autopay_a2c51ad3, interest_rate)`, `(enroll_autopay_b9bffdb4, interest_rate)`, `(waive_returned_payment_fee_ab31cb83, amount)`, `(waive_late_charge_e8055e73, amount)`, `(post_payoff_payment_63569e96, amount)`. Each is claimed by exactly one policy. `change_due_day_df9bec35` is claimed only by workflow step 1 (`computed_by: []`, base `auto_due_date_change`).
- The tool docstrings match their subjects and owners. owner=agent: payment, due-day change, the two waivers, payoff. owner=user: cancel and enrol, which base describes as the "borrower's own instruction" in `auto_evt_autopay`.
- Tool bodies (task_tools.py lines 56-88, 115-120, 155-165, 199-210, 244-259, 294-309, 347-374) validate nothing. There is no status check, no refusal, no prerequisite hint and no computed amount. Each tool writes the arguments it is given, plus arithmetic on the loan row's fields.
- Two observations on the tools:
  - The payment and payoff tools do not write the base trigger `checking:checking_debit` ("Payments from a PCB checking account debit that account through the payment's trigger"), and the runtime fires no triggers (erlbench contains no trigger code). The paying account's ledger_balance is therefore never lowered (O11).
  - The payment tool's row id hashes every argument, including `next_payment_due_date` and `days_past_due` (task_tools.py line 59). Those two arguments therefore enter the final-state hash.
- uuid8 suffixes: 660c6229, df9bec35, a2c51ad3, b9bffdb4, ab31cb83, e8055e73, 63569e96. All seven are distinct. They share no common prefix beyond a single hex digit, are not sequential and are not near each other in value. Nothing suggests a batch-derived or copied tail. I can check only the pattern, not how the suffixes were generated.

### prerequisite_graph

This is check 7. A script confirmed the facts below against the YAML.

- Every extended policy and the workflow has a `prerequisite` field. It is `[]` for catch-up, cancel, both waivers and the workflow. The enrolment and the payoff have 2 edges each.
- The edges:
  - E1: enrol → `auto_ext_catchup_installment_payment`, `value_input`, gate `autopay_added`.
  - E2: enrol → `auto_ext_autopay_cancel_rate`, `state_gate`, gate `auto_loans.autopay_enrolled`.
  - E3: payoff → `auto_ext_closed_source_returned_fee_waiver`, `value_input`, gate `fees_due`.
  - E4: payoff → `auto_ext_closed_source_late_charge_waiver`, `value_input`, gate `fees_due`.

  Every `problem` is an extended policy id in this file. No edge points at a base policy or at itself. The graph has sinks {catch-up, cancel, both waivers}, two roots, depth 1, and no cycle.
- `policy_source`: all four are verbatim substrings of the citing policy's `rule`.
- `condition` compared with its source sentence:
  - E1: "no installment past due when autopay is enrolled" equals the rule's "the loan must have no installment past due".
  - E2: "No autopay enrollment stands on the loan" equals "only on a loan with no enrollment standing".
  - E3 and E4: "every … has been waived before the payoff amount is fixed" equals the rule sentence.

  No condition is strengthened or weakened.
- `resolved_by` compared with `effect`:
  - E1. `post_installment_payment_660c6229` writes `days_past_due` from its argument (line 84). When that argument is 0, the enrolment compute's `F('days_past_due') == 0` holds and `autopay_added` switches from 0 to 0.25. The effect is real.
  - E2. `cancel_autopay_a2c51ad3` sets `autopay_enrolled=False` and `autopay_source_account_id=""` (line 161). The effect is real.
  - E3 and E4. Each waiver tool creates an `auto_fee_waiver` row (lines 249, 299), which lowers the ledger `fees_due` that the payoff compute reads. The effect is real.
- `kind` compared with `gate`: `autopay_added` and `fees_due` are bindings in the citing compute. `auto_loans.autopay_enrolled` is a real field, and the rule sentence makes it a legality gate. The kinds match.
- No authoring-viewpoint phrasing ("in this task", "at the opening") appears in any `prerequisite` field.
- One edge not in the graph: workflow step 1 (the due-day change) depends on catch-up through base `auto_due_date_change` ("The loan must be active with no installment past due"). That is a base-policy gate, and `problem` may not name a base policy, so leaving it out of the graph is correct. The dependency is still carried by the workflow's `order_rationale` and by dataflow 0→1 (`eligibility_id: current_and_active`).

### override_declarations

This is check 1's finding half. I went sentence by sentence through each `base_policy_refs` entry. The criterion is the quantity that ends up scored.

**`auto_ext_catchup_installment_payment`** (refs `auto_evt_payment_allocation`, `auto_evt_payoff_and_lien`; `overwrite: []`)
- Daily simple interest / `auto_msr_accrued_interest` on principal from last_payment_date. Followed. Extended recomputes principal from the ledger. That equals `principal_balance` whenever the ledger and the row agree (both task worlds agree; see the task files).
- Cutoff and credit day. Followed in the rule ("credit date"). Compute implements it only as `NOW` (O2).
- Posting only to an active or delinquent loan. Inherited; extended is silent.
- Allocation fees → interest → principal, settlement row, last_payment_date becomes the credit date. Followed.
- Installment satisfied when scheduled payments credited toward it total at least monthly_payment; advances one month; no early satisfaction. Followed, with one narrowing. Extended subtracts only the payment named by the **most recent** `auto_payment_reversal` from the standing credit (O1).
- Principal-only; no prepayment penalty; the PCB checking debit trigger. Not applicable / inherited. The trigger is not implemented (O11).
- `auto_evt_payoff_and_lien` sentences (payoff amount, quote, excess or shortfall, lien, GAP). Not engaged by a scheduled payment. The "shortfall leaves the loan open with the payment applied normally" sentence agrees with the partial-funds branch.

**`auto_ext_autopay_cancel_rate`** (refs `auto_agg_relationship_discount`, `auto_evt_autopay`; `overwrite: []`)
- The relationship discount is granted at funding when an active qualifying account is held on the funding date. Extended re-derives it from open and close dates. That agrees whenever `rate_discounts` and the checking records agree (O8).
- "fixed for the life of the loan … not added later … nor removed if it later closes". Followed ("a qualifying account closed later still counts").
- Stacking up to the cap, never below the floor; lost excess. Followed. Rebuilding `pre_rate` as recorded rate + recorded discounts is exact unless the floor bound at funding. No variant can reach that: the lowest base+adder−0.50 is 4.99 against a 3.49 floor (Green 36). Unreachable (O8).
- "When autopay is cancelled … the APR rises by the autopay discount actually applied". Followed: pre_rate − kept equals rate + applied autopay on every reachable parameter set.
- `auto_evt_autopay` "cancelling removes it on the same schedule". Extended records the post-removal APR on the cancellation. The base event field `interest_rate: "APR after the autopay discount is added or removed."` records the same value, so the recorded quantity does not change. After `auto_ext_autopay_enroll_rate` superseded the enrolment half of the sentence, "the same schedule" refers to a superseded clause (O8).
- Borrower's own instruction; the loan must be active or delinquent. Inherited.

**`auto_ext_autopay_enroll_rate`** (refs `auto_agg_relationship_discount`, `auto_evt_autopay`; one declared overwrite on `auto_evt_autopay`, whose superseded_clause matches base verbatim)
- Declared. The `auto_evt_autopay` clause "Enrolling adds the autopay discount to the APR … from the next installment due at least autopay_lead_days calendar days after enrollment" is replaced by the past-due and active-source discount condition.
- **Not declared.** `auto_agg_relationship_discount`: "When autopay is cancelled and autopay_discount_removed_on_cancel is true, the APR rises by the autopay discount actually applied, **and re-enrolling later restores it**". This base sentence governs the same scored quantity, the APR recorded on a re-enrolment. Extended gives a different conclusion when an installment is past due: "an enrollment recorded while an installment is past due carries no autopay discount". The overwrite does not name this sentence (F1).
- Not declared, and a dropped branch. `auto_evt_autopay`: "Enrolling or cancelling is the borrower's own instruction to move their funds, and the loan must be active or delinquent." Extended adds "Before an enrollment is recorded, the loan must have no installment past due". A delinquent loan (days_past_due ≥ 30) always has an installment past due, so the base "delinquent" branch for enrolment can never occur (part of F1).
- Source account active at enrolment. Inherited. Extended's "no discount if the source is not active" branch cannot be reached while the base eligibility forbids that enrolment (O7).

**`auto_ext_closed_source_returned_fee_waiver`** and **`auto_ext_closed_source_late_charge_waiver`** (ref `auto_evt_fee_waiver`; `overwrite: []`)
- "waived in full, never in part, as one auto_fee_waiver row whose source_item_id is the fee". Followed.
- "A bank_error waiver applies to any fee assessed contrary to this charter, such as …; it has no limit". Extended adds one ground to the open ("such as") list: an autopay debit presented to an account closed before the debit date. This is additive. The premise "autopay may draw only on an active PCB checking account" has no base sentence (O9).
- The courtesy sentences do not apply (bank_error). "A fee can be waived at most once" is followed through `prior_waivers`. "Already paid … applied to principal" is followed and refined to "the part already paid".

**`auto_ext_payoff_settlement`** (refs `auto_evt_payment_allocation`, `auto_evt_payoff_and_lien`; `overwrite: []`)
- Payoff = principal_balance + accrued through the date + fees_due. Followed, with a ledger recomputation and a penalty term that is always 0.
- Posts as payoff, pays all to zero, moves the loan to paid_off. Followed (tool lines 353-372).
- Excess refund; "a shortfall leaves the loan open with the payment applied normally". Extended's "ledger_balance lower than the payoff amount → no payoff is posted and the amount is 0.00" governs the transfer the agent starts, not a short payment already received. Compatible. It is never engaged when funds cover the payoff (O6).
- Lien release deadline; GAP refund on payoff with GAP in force. Inherited; extended is silent.

### findings

**F1 — SOURCE-POLICY RED (charter-global; bears on task 0).**
- Symptom: `auto_ext_autopay_enroll_rate` makes the autopay discount, and enrolment itself, conditional on no installment being past due. Two base sentences in its own `base_policy_refs` reach a different conclusion for the same situation, and the policy's `overwrite` names neither.
- Root cause: the single declared overwrite names only the `auto_evt_autopay` enrolling clause. The same quantity is also governed by `auto_agg_relationship_discount`'s "re-enrolling later restores it" and by `auto_evt_autopay`'s "the loan must be active or delinquent". Both are left in force and will be rendered alongside the extended rule.
- Evidence (verbatim):
  - Base `auto_agg_relationship_discount.rule`: "When autopay is cancelled and autopay_discount_removed_on_cancel is true, the APR rises by the autopay discount actually applied, and re-enrolling later restores it; the relationship discount is unaffected by autopay changes."
  - Base `auto_evt_autopay.rule`: "Enrolling or cancelling is the borrower's own instruction to move their funds, and the loan must be active or delinquent."
  - Extended `auto_ext_autopay_enroll_rate.rule`: "Before an enrollment is recorded, the loan must have no installment past due, and a past-due installment is first brought current by a scheduled payment." and "an enrollment recorded while an installment is past due carries no autopay discount."
  - `auto_ext_autopay_enroll_rate.overwrite[0].base_policy` = `auto_evt_autopay`, and its superseded_clause is only the "Enrolling adds the autopay discount … after enrollment" clause.
- Demonstrated consequence (same situation, two conclusions): a borrower cancels autopay and re-enrols while an installment is past due. Task 0's opening world is one such situation: Auto Refinance Loan, interest_rate 8.24, rate_discounts `autopay_and_relationship`, days_past_due 9.
  - Base: re-enrolment is permitted (the loan is active) and "restores" the autopay discount. APR = 8.74 − min(0.50, 0.25 + 0.25) = **8.24**.
  - Extended: the enrolment may not be recorded until the installment is brought current. If recorded, it carries no autopay discount: APR = 8.74 − 0.25 = **8.49**.
  - This contrast is exactly what the declared edge E1 (`value_input`, gate `autopay_added`) depends on. The task-0 file shows what it costs that task.
- Affected artifact: `auto.extended.yaml` → `extended_policies[auto_ext_autopay_enroll_rate].overwrite` (missing entries for the two base sentences), its `rule`, and `prerequisite[0]` (E1).

**Observations (charter-global; not red because no consequence can be shown in either task's world):**
- O1. The catch-up treats as "returned" only the payment named by the *most recent* reversal on the loan. Base `auto_evt_returned_payment` ("The installment the payment satisfied becomes unsatisfied again") reverses every returned payment. The two diverge only when an earlier-returned payment toward the current installment is not the most recently reversed one. Neither world has that (task 0 has one reversal).
- O2. The credit date is implemented as `NOW` (catch-up and payoff). The base after-cutoff and non-business-day branch is not implemented. Both frozen times are before 17:00 ET on business days: Fri 2026-08-14 10:20 and Mon 2026-08-10 11:05.
- O3. CFIELD takes the first matching checking row (the active account's ledger_balance; the qualifying-tier account's dates). This is ambiguous when two rows match. Each task world has exactly one active account and at most one account per tier.
- O4. `RND` is Python float `round`, not half-up. No computed value in either world lands on a half-cent tie (the raw figures are in the task files).
- O5. The payoff rule demands that "every" qualifying returned-payment fee and late charge be waived "under its own rule". Each waiver rule, however, considers only the most recent fee of its kind, so a second qualifying fee could never be waived. Task 1 has exactly one qualifying fee of each kind (see its file).
- O6. The payoff's insufficient-funds branch (amount 0.00) is never engaged in task 1.
- O7. The enrolment's `source_active` checks for any active checking account rather than the paying one. The "no discount for an inactive source" branch cannot be reached under the base source eligibility.
- O8. The cancel rule has no `rate_discounts` branch for removed_on_cancel = false (every variant sets it true). Its floor-binding rebuild is unreachable. "Same schedule" in base `auto_evt_autopay` now refers to a superseded clause. The re-derived relationship discount agrees with the recorded `rate_discounts` in both worlds.
- O9. The two closed-source waivers call the fee "assessed contrary to this charter" on the premise "autopay may draw only on an active PCB checking account". Base states only "The autopay source must be a checking account of the same customer in active status when autopay is enrolled." Base `auto_evt_autopay` also says "An autopay debit returned unpaid is handled as a returned payment". The extended rule adds a waiver ground and contradicts no base sentence about waiving, because the bank_error list is open. I record this as a grounding observation; the waiver itself is not red.
- O10. Five claimed event types (auto_fee as a primary action, auto_extend, auto_cancel_gap, auto_gap_refund, auto_release_lien) have no extended policy or task.
- O11. The payment and payoff tools do not debit the paying checking account, although base defines that trigger. No later step in either task reads that ledger_balance.
- O12. Workflow `auto_wf_autopay_source_change`:
  - Step 0 before step 1, and step 2 before step 3, are policy-backed (`auto_due_date_change` "active with no installment past due"; the enrol rule's "no enrollment standing").
  - Step 1 before step 2 is justified only by `order_rationale`'s own claim ("the bank settles the due day the new enrollment will follow before the borrower's own autopay instructions are taken"). No policy sentence says this. Policy alone also allows [0,2,3,1] and [0,2,1,3].
  - `dataflow` declares only `auto_loan_id` object bindings. It does not declare the value and state flows the later steps consume: step 0's `days_past_due` → step 3's `autopay_added`, step 0's `next_payment_due_date` → step 1's `next_payment_due_date`, and step 2's `interest_rate` / `rate_discounts` → step 3's `pre_rate`.
  - Final-state hashing (erlbench/scoring.py) makes these orders score identically, so the task-0 file reports no scored consequence.
  - `requires_external_wait` / `zero_wait_proof` live in the task's `solvability_contract`, not in the YAML (instantiate SKILL.md line 105). I check them in the task-0 comparison after the reveal.

## closing_checklist

Written after the reveals (task 0 GT revealed 2026-09-12T20:15:49Z, task 1 GT revealed 20:17:02Z). The `charter_global_frozen` section above was frozen and hashed (d3a0f909…) at 20:15:44Z, before any reveal, and was not edited afterwards.

**Status: the difficulty does NOT close in this revision.** Task 0 is SOURCE-POLICY RED (F1). Step 4's precondition, that all three relationships PASS for every task, is not met. The items below record where each checklist item stands.

| Item | State |
| --- | --- |
| Per-task files match tasks one-to-one; `_difficulty.md` alongside | `0.md` and `1.md` for tasks 0 and 1; revision 1, with no older revisions. |
| Every comparison carries a PASS | **No.** Task 0: SOURCE-POLICY RED (policy), PASS (chain, under the extended reading), PASS (unique solution). Task 1: PASS / PASS / PASS. |
| Extended policies fully covered | Yes. Task 0 `charter_scope` = {catch-up, cancel, enrol} + workflow. Task 1 = {returned-fee waiver, late-charge waiver, payoff}. The union is all 6 extended policies. This matches the partition I derived before the reveal (`policy_conflict_scan`). |
| Scopes pairwise disjoint, over whole problem trees | Yes. Tree 0 = {enrol ← catch-up, enrol ← cancel}; tree 1 = {payoff ← two waivers}. No shared node. Task tools: {660c6229, df9bec35, a2c51ad3, b9bffdb4} and {ab31cb83, e8055e73, 63569e96}, disjoint and covering all 7. |
| Exactly one workflow, claimed by exactly one task | Yes. `auto_wf_autopay_source_change` is claimed only by task 0. Its four GT steps have `requires_external_wait: false` and a `zero_wait_proof`. |
| Task tools and GT closed; independent frozen uuid8 per tool | Yes. Every GT write uses one of the 7 tools, and every tool is used. The uuid8 pattern check is in `action_binding_and_uuids`. |
| Each task's tree has ≥ 2 prerequisites, ≥ 1 value_input edge, no cycle | Task 0: 2 edges (E1 value_input, E2 state_gate). E1's value weight is contingent on F1. Task 1: 2 edges, both value_input. |
| Whole-difficulty prerequisite graph is a DAG | Yes. Four edges, two roots, depth 1, no cross-task edge. |
| Instantiation gates re-run on the final form | Not done. The difficulty has not reached a final form; the task-0 RED is open. The gate snapshot the orchestrator supplied at entry (all 7 gates exit 0; traceability deferred) is the one cited in `charter_global_frozen`. |

Per-task verdicts:
- Task 0: **SOURCE-POLICY RED** (F1: undeclared override in `auto_ext_autopay_enroll_rate` of base `auto_agg_relationship_discount` "re-enrolling later restores it" and base `auto_evt_autopay` "the loan must be active or delinquent"). See `0.md`.
- Task 1: **PASS**. See `1.md`.

## revision_2

### charter_global_frozen (revision 2)

- Re-audit round 2. Freeze time: 2026-09-12T20:29Z (before any round-2 task JSON was opened). Auditor: the same independent auditor as revision 1. I did not take part in the rework.
- Inputs:
  - `auto.extended.yaml` sha256 **37c0826d…1080795**. It changed from c462c969…, so every charter-global section below is **re-derived in full**.
  - `task_tools.py` sha256 ff9b197c…c9f4d, unchanged. The tool-body findings of revision 1 carry forward on that hash.
  - Round-2 views: task 0 c3c47960… (changed), task 1 e12a670e… (unchanged). Both hashes match the round-2 MANIFEST.
  - Gate snapshot after the rework, as the coordinator supplied it: all 7 gates exit 0; traceability deferred.
- contamination_disclosure: I read the **round-1** GT fields of both tasks at 20:15-20:17Z, after my round-1 blind derivations were frozen. The revision-2 derivations therefore cannot be blind with respect to round-1 GT. My round-1 blind derivations (frozen and hashed before any reveal) are the uncontaminated anchor: revision 2 re-derives from the round-2 charter and views and records any difference from that anchor. I did not open the **round-2** task JSONs (0.json 17bc796c…, 1.json 4e148e2a…) before this freeze and the task freezes below.
- The reworker's claims are treated as unverified until the checks below.

#### What changed in the charter (revision 1 → revision 2)

I compared the round-2 file against the round-1 text I recorded. The base section, lines 1-1365, is byte-identical to round 1 and still verbatim with `blueprint/products/auto.yaml`: `diff` is empty except for the trailing blank line, and my round-1 snapshot `audit_auto/base_head.yaml` is unchanged.

Changes in the extended section:
1. `auto_ext_autopay_enroll_rate.overwrite` has two new entries:
   - (b) supersedes `auto_evt_autopay` "Enrolling or cancelling is the borrower's own instruction to move their funds, and the loan must be active or delinquent." It is replaced by "Enrolling is the borrower's own instruction to move their funds, and an enrollment is recorded only on an active loan with no installment past due; a delinquent loan cannot be enrolled until it is brought current."
   - (c) supersedes `auto_agg_relationship_discount` "and re-enrolling later restores it". It is replaced by "Re-enrolling after a cancellation restores the autopay discount only on the same terms as a first enrollment: …".
   - Both replacement texts are also added to the enrolment `rule`. Both superseded clauses are verbatim substrings of the base rules (script-checked). Compute is unchanged.
2. The `auto_ext_autopay_cancel_rate.rule` has three new sentences. Compute is unchanged and `overwrite` is still `[]`.
   - (i) "when autopay_discount_removed_on_cancel is false, rate_discounts is left as recorded."
   - (ii) "The APR written on the cancellation is the APR the loan carries once the autopay discount has left the rate, recorded with the cancellation itself."
   - (iii) "When a borrower who is moving autopay to a different checking account also asks for a new due day, the due date change is recorded before the standing enrollment is cancelled, so the loan is never left without autopay while its payment schedule is still being changed."
3. Both closed-source waiver rules have one new grounding sentence. Returned-fee: "PCB keeps an autopay enrollment drawing only on a source account that is open on each debit date, extending to every debit the enrollment-time requirement that the autopay source be an active checking account of the borrower; presenting a debit to an account PCB's own records show already closed is therefore PCB's error, not the borrower's." The late-charge rule has the analogous sentence. Compute, `overwrite` and `base_policy_refs` are unchanged.
4. Workflow `auto_wf_autopay_source_change`:
   - `dataflow` gains `carries` notes on 0→1 and 2→3, and a new 0→3 edge whose `carries` says the enrolment reads the payment's `days_past_due`.
   - `order_rationale` now grounds step 1 before step 2 in change 2(iii).
   - Steps, owners and tools are unchanged.
5. `auto_ext_catchup_installment_payment` and `auto_ext_payoff_settlement`: rule, compute, compute_basis and prerequisite all read the same as in revision 1.

#### Mechanical re-checks (script over the round-2 YAML)

- Every `compute_basis` value is a verbatim substring of its rule, and every compute key set equals its compute_basis key set, in all 6 policies.
- All 4 `policy_source` strings are verbatim in their rules.
- The gates `autopay_added` and `fees_due` exist as compute bindings.
- All 3 `superseded_clause` strings are verbatim in the named base rule, and all 3 `replaced_by` strings appear in the enrolment rule.
- The `(target_tool, computes)` pairs are still distinct.
- The graph is unchanged: E1-E4, two roots, no cycle.
- uuid8s and tool bodies are carried forward from revision 1 on the unchanged `task_tools.py` hash (ff9b197c…).

#### policy_conflict_scan / override_declarations (revision 2)

- **F1 (revision-1 SOURCE-POLICY RED) — CLOSED.** Both base sentences F1 named are now declared in `auto_ext_autopay_enroll_rate.overwrite` (entries b and c). Sentence-by-sentence sweep of the two refs as merged:
  - `auto_agg_relationship_discount`, merged: "… the APR rises by the autopay discount actually applied, [Re-enrolling after a cancellation restores the autopay discount only on the same terms as a first enrollment …]; the relationship discount is unaffected by autopay changes." This agrees with the extended gate. No sentence remains that restores the discount on a past-due re-enrolment.
  - `auto_evt_autopay`, merged: the enrolment eligibility is now "active loan with no installment past due", the same as the extended rule. The source-active eligibility is inherited. "A change of APR does not change monthly_payment" and "autopay stays enrolled" after a return are compatible.
  - Re-demonstration on task 0's opening world (dpd 9, 8.24 `autopay_and_relationship`): every surviving passage now gives the same conclusion. Enrolment is not recorded until the loan is current; if one were recorded it would carry no autopay discount (8.49). No passage yields 8.24 on the opening world. The two conclusions F1 demonstrated no longer both hold.
- **NEW observation N1 — the superseded clause is wider than its replacement.**
  - Overwrite (b) supersedes a base clause that governs **both** enrolling and cancelling ("Enrolling or cancelling is the borrower's own instruction …, and the loan must be active or delinquent"). The replacement restates only enrolling.
  - The merged charter therefore no longer says that cancelling is the borrower's own instruction, or that a cancellation needs an active or delinquent loan. That provision belongs to the subject of `auto_ext_autopay_cancel_rate`, whose own `overwrite` is `[]`.
  - The merged semantics for cancellation eligibility can be read two ways. Reading a: the whole clause is superseded, so no status gate applies. Reading b: an overwrite declared by the enrolment policy reaches only enrolment, so the cancelling half survives. The readings differ for, say, cancelling autopay on a paid-off or charged-off loan.
  - Consequence in the task worlds: none. Task 0's cancellation is on an `active` loan, allowed under both readings, and its owner is fixed as user by the tool contract (`@tool(owner="user")`, line 123) and the persona. Task 1 cancels nothing.
  - Recorded as an observation (the rework introduced it; no task demonstrates it). Affected: `auto.extended.yaml` → `auto_ext_autopay_enroll_rate.overwrite[1]`.
- **O12 (workflow order) — CLOSED.** Step 1 before step 2 is now carried by policy text, cancel-rule change 2(iii). Policy alone now gives the total order 0 < 1 (base `auto_due_date_change`), 1 < 2 (cancel rule), 2 < 3 and 0 < 3 (enrolment rule). `dataflow` now declares the value and state flows (0→1 dpd and next due, 2→3 rate and discounts, 0→3 dpd).
  - Residual observation N2. Sentence 2(iii) is an ordering gate on the cancellation (the due-day change goes first), but the cancel policy's `prerequisite` stays `[]`. It cannot be declared, because the due-day change has no extended policy id and `problem` may not name a base policy. The same was true of the round-1 due-day-change ← catch-up base gate. Not red.
- **O8 — PARTLY CLOSED.**
  - Closed: the missing `rate_discounts` branch for removed_on_cancel = false (sentence 2(i)); the recording point of the cancel APR (2(ii)).
  - Remaining: base `auto_evt_autopay` still reads "…; cancelling removes it on the same schedule when autopay_discount_removed_on_cancel is true". The cancel policy's `overwrite` is still `[]`, and after overwrite (a) "the same schedule" still refers to a superseded clause. The recorded value is unaffected: the base event field reads "APR after the autopay discount is added or removed", and 2(ii) agrees. The floor-binding rebuild is still unreachable under this charter's parameters.
  - Remains an observation.
- **O9 / OB-T1-1 — CLOSED as a grounding gap.** The waiver rules now state their premise in charter text and present it as extending base `auto_evt_autopay`'s enrolment-time source requirement to every debit.
  - No base sentence says the requirement applies *only* at enrolment, and none forbids a bank_error waiver. The base bank_error list is open.
  - Residual observation N3: the waiver rules now extend a provision of `auto_evt_autopay`, which is absent from their `base_policy_refs` ([auto_evt_fee_waiver]). The extension is a strengthening that contradicts no base sentence, so there is no conflict to declare. Not red.
- Unchanged and carried forward from revision 1 on the unchanged catch-up, payoff and waiver compute: O1, O2, O3, O4, O5, O6, O7, O10, O11. Each still bears on no task value (re-checked per task below).

#### rule_compute_equivalence (revision 2)

- Compute blocks are unchanged in all six policies. New rule sentences:
  - Enrolment, overwrites b and c: legality and restoration terms. They agree with the existing `autopay_added` and `source_active` bindings, and the legality part does not need to be a binding.
  - Cancel 2(i): the `rate_discounts` branch, a tool argument with no compute binding, on the same footing as the round-1 sentence.
  - Cancel 2(ii): the recording point.
  - Cancel 2(iii): ordering only.
  - Waivers: grounding only.
- No new rule sentence makes a promise that compute leaves out, and no binding lost its basis.
- O7 (`source_active` = any active account) still stands.

#### Verdict of the charter-global re-derivation

- No charter-global SOURCE-POLICY RED remains.
- The new observations are N1 (widest), N2 and N3. The residual observations are O8 (partial) and those carried forward.

### post-reveal addendum (revision 2)

Written after the round-2 reveal at 20:30:11Z. The `charter_global_frozen (revision 2)` section above was hashed at 20:30:03Z (7cf5b625…) and not edited afterwards.

- N1, refined from task-0 GT. Round-2 `tasks/0.json` design_rationale [3] states the intended reading: "(cancelling keeps the base sentence through auto_ext_autopay_cancel_rate)". The charter does not carry that reading. The cancel policy has `overwrite: []` and its rule restates neither half of the superseded clause. N1 therefore stays an observation: the policy surface is ambiguous for cancellation eligibility, and no task value depends on it.
- N4 (new, task-0 proof field): `prerequisite_closure.order_uniqueness` still presents cancel-first as a same-terminal alternative, although cancel sentence 2(iii) now forbids it in task 0. The hash claim is true. Observation.

### closing_checklist (revision 2)

**Status: the difficulty CLOSES in revision 2.** Every task passes all three relationships.

| Item | State |
| --- | --- |
| Per-task files match tasks one-to-one; `_difficulty.md` alongside; old revisions traceable | `0.md` and `1.md`. Revision 1 is kept verbatim above each `## revision_2` heading. |
| Every comparison carries a PASS | Yes. Task 0 revision 2: PASS / PASS / PASS. Task 1 revision 2: PASS / PASS / PASS. |
| Extended policies fully covered | Yes. Task 0 claims {catch-up, cancel, enrol} + workflow; task 1 claims {returned-fee waiver, late-charge waiver, payoff}. The union is all 6 extended policies (round-2 `charter_scope`). |
| Scopes pairwise disjoint, over whole problem trees | Yes. No shared node and no cross-task edge. Tool sets {660c6229, df9bec35, a2c51ad3, b9bffdb4} and {ab31cb83, e8055e73, 63569e96} are disjoint and cover all 7. |
| Exactly one workflow, claimed by exactly one task | Yes (task 0). All four GT steps have `requires_external_wait: false` and a `zero_wait_proof`. |
| Task tools and GT closed; independent frozen uuid8 per tool | Yes. `task_tools.py` is unchanged (ff9b197c…), so revision 1's uuid check carries forward. |
| Each tree has ≥ 2 prerequisites, ≥ 1 value_input edge, no cycle | Task 0: E1 value_input (now non-contingent) and E2 state_gate. Task 1: E3 and E4, both value_input. |
| Whole-difficulty prerequisite graph is a DAG | Yes. Four edges, two roots, depth 1. The undeclarable base gates (due-day change ← catch-up; cancel ← due-day change, N2) add no cycle. |
| Instantiation gates re-run on the final form | The orchestrator re-ran them after the rework, on the same file hashes as the round-2 manifest (extended 37c0826d…, tools ff9b197c…, tasks 17bc796c… / 4e148e2a…). EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE all exit 0; traceability is deferred to the KB stage by design. I cite this snapshot; I did not re-run the gates myself (Step 0). |

Open observations. None is a ground for rework under the skill's threshold, because none has a demonstrated consequence in either task's world:
- N1: overwrite (b) is wider than its replacement for cancelling.
- N2: cancel's policy gate on the due-day change cannot be declared.
- N3: the waiver rules extend `auto_evt_autopay`, which is not in their refs.
- N4: stale order_uniqueness text in task 0.
- O8 residue: "same schedule".
- O1-O7, O10, O11: carried forward.
- OB-T0-2.

Per-task verdicts, revision 2:
- Task 0: **PASS** (revision-1 SOURCE-POLICY RED F1 closed).
- Task 1: **PASS** (unchanged).

## revision_3

### charter_global_frozen (revision 3)

- Re-audit round 3. Freeze time: 2026-09-12T21:29Z. That is before I opened the round-3 task JSONs and before I read the render-layer (KB) audit reports under `audits/policy_kb/…`. The items I verify from those reports (P1, P2, P3, the tool-example coincidence) are the ones the coordinator's brief names; the reports themselves are read only after this freeze.
- Inputs:
  - `auto.extended.yaml` sha256 **47876ef9…8afa**. It changed from 37c0826d…, so the charter-global sections are re-derived in full.
  - `task_tools.py` sha256 **51e8146c…8ce6**. It changed from ff9b197c…, so the tool sections are re-derived too.
  - Views: task 0 2ff7d98e… (changed), task 1 e12a670e… (unchanged). Both match the round-3 MANIFEST.
  - Gate snapshot after the rework, as the coordinator supplied it: all 7 gates exit 0.
- contamination_disclosure: I read round-1 GT (at 20:15-20:17Z) and round-2 GT (at 20:30Z) for both tasks. The coordinator also says the KB reports quote scored values. This revision is therefore **not blind**. The uncontaminated anchor is still my revision-1 blind derivation (hashes 7eb7d0c9… / 4fa72562…).
- Base section: lines 1-1365 are byte-identical to round 1 and 2 (`diff` against `audit_auto/base_head.yaml` is empty), and verbatim with `blueprint/products/auto.yaml` (sha256 d467be87…, unchanged).

#### What changed (round 2 → round 3), by `diff` against my round-2 snapshot `audit_auto/ext_r2.yaml`

1. `auto_ext_autopay_cancel_rate.overwrite` was `[]` and now has two entries:
   - (P1) supersedes `auto_agg_relationship_discount` "When autopay is cancelled and autopay_discount_removed_on_cancel is true, the APR rises by the autopay discount actually applied". It is replaced by the rebuild sentence "The new APR is the rate before discounts less the discounts kept, …apr_floor…; rounded to two decimal places."
   - (P3) supersedes `auto_evt_autopay` "cancelling removes it on the same schedule when autopay_discount_removed_on_cancel is true". It is replaced by "… recorded with the cancellation itself and in force from the cancellation, not from a later installment."
   - The rule gains "and in force from the cancellation, not from a later installment".
2. `auto_ext_autopay_enroll_rate`:
   - Round-2 overwrite (b) is **withdrawn**. That was the one on `auto_evt_autopay` "Enrolling or cancelling is the borrower's own instruction to move their funds, and the loan must be active or delinquent."
   - The rule sentences that made a past-due installment a hard block on enrolment are **removed**: "an enrollment is recorded only on an active loan with no installment past due; a delinquent loan cannot be enrolled until it is brought current" and "Before an enrollment is recorded, the loan must have no installment past due, and a past-due installment is first brought current by a scheduled payment." A script search of the extended section finds none of the blocking phrases left.
   - Added: "When the loan has an installment past due and the borrower brings it current in the same call, the scheduled payment is posted before the enrollment is recorded, so that the enrollment is recorded on a loan with no installment past due and carries the autopay discount."
   - E1's `policy_source` is now that sentence. Its `condition` now ends "…, so the enrollment carries the autopay discount."
   - Overwrites (a) and (c) are kept.
3. Catch-up, both waivers, payoff and the workflow are unchanged since round 2. Compute is unchanged in every policy.
4. `task_tools.py`: only docstring examples changed. The tool bodies are identical to the ones I read in rounds 1 and 2. I compared them against the round-1 text; decorators, owners and argument lists are the same. The examples are now: installment_due_date 2031-02-15, next_payment_due_date 2031-03-15 and 2031-03-28, interest rates 7.24 / 6.99.

#### Mechanical re-checks

- Every compute_basis value is verbatim in its rule, and the key sets equal the compute bindings (all 6 policies).
- All 4 policy_sources are verbatim in their rules.
- All 4 superseded_clauses are verbatim in the named base rules, and all 4 replaced_by strings are in the extended rules.
- The gates `autopay_added` and `fees_due` are bindings. The graph (E1-E4) is acyclic.
- The `(target_tool, computes)` pairs are distinct. The uuid8 suffixes are unchanged (the tool names are the same).

#### Override sweep and conflict scan (revision 3)

- **F1 stays CLOSED under the new wording.** This re-check is the one the reworker asked for.
  - Of the two base sentences F1 named, `auto_agg_relationship_discount` "re-enrolling later restores it" is still superseded by (c).
  - `auto_evt_autopay` "the loan must be active or delinquent" is back in force because (b) was withdrawn. It **no longer conflicts**: the extended rule no longer forbids enrolment while past due. It only withholds the autopay discount ("an enrollment recorded while an installment is past due carries no autopay discount"), and the base "Enrolling adds the autopay discount …" clause is superseded by (a).
  - On task 0's opening loan (active, dpd 9) every surviving passage now agrees. Enrolment is permitted (base: active) and carries no autopay discount (extended plus a and c), which gives 8.49 / relationship. No surviving passage gives 8.24 on the opening world. The two conclusions F1 demonstrated no longer both hold.
  - Merged `auto_evt_autopay`: "Enrolling or cancelling is the borrower's own instruction…, and the loan must be active or delinquent. [a]; [P3]. A change of APR does not change monthly_payment …". This is unique.
  - Merged `auto_agg_relationship_discount` sentence: "… [P1 replacement], [c replacement]; the relationship discount is unaffected by autopay changes." Two overwrites from two different extended policies split this one base sentence at adjacent clauses. The merged meaning is unique: the cancellation rebuild applies, and re-enrolment restores the discount on first-enrolment terms. It is awkward as prose (observation R3-O1, for the render layer).
- **N1 — CLOSED by the withdrawal of (b).** The cancelling half ("borrower's own instruction", "active or delinquent") is back in force for cancellation. The reworker's "no change for N1" understates this. Verified from the text.
- **P2 — CLOSED.** E1 is `value_input` (gate `autopay_added`), and the rule now only orders the payment before the enrolment when the borrower pays in the same call, and withholds the discount otherwise. No hard block remains, so the declared kind matches the rule. The `condition` states the value condition exactly. It drops the "brings it current in the same call" trigger, but that trigger governs ordering, not the value, so the condition is not strengthened as a legality gate.
- **P1 — CLOSED** (the override is now declared). My revision-1 analysis still holds: the rebuild equals base "rises by the autopay discount actually applied" on every reachable parameter set, and diverges only in a floor-binding world, which this charter's parameters cannot reach. Whether it was a live conflict or not, the deviation is now declared and the merged semantics are unique.
- **P3 / O8 residue — CLOSED.** "Same schedule" is superseded, and the recording point and the in-force point are now stated. The enrolment timing clause was superseded by (a); the enrolment discount is "added at enrollment". Timing is consistent on both sides.
- **Tool-example coincidence — CLOSED.**
  - Auditor's own miss, disclosed: in rounds 1 and 2 the round-1 `task_tools.py` docstrings used "for example 2026-08-05" (installment_due_date), "2026-09-05" (next_payment_due_date) and "2026-09-20" (change_due_day next_payment_due_date). Those are exactly task 0's scored argument values. I did not flag this in revision 1 or revision 2.
  - The round-3 examples (2031-02-15, 2031-03-15, 2031-03-28, 7.24, 6.99) coincide with no scored value of either task. Task 0's are 2026-08-05, 2026-09-05, 2026-09-20, 8.49, 8.24; task 1 has no date argument and 6.24 is not a scored rate.
- N2 (cancel's policy gate on the due-day change cannot be declared) and N3 (waiver rules extend `auto_evt_autopay` outside their refs): unchanged observations.
- O1-O7, O10, O11: unchanged, carried forward.
- **New-defect scan of the added text:**
  - "in the same call" is general business phrasing, not authoring-viewpoint phrasing.
  - The E1 trigger now depends on the borrower paying in the same call. In task 0 that is driven by the base due-day-change gate. Whether it holds is judged per task (see `0.md`).
  - No new conflict was found among the three overwrites on `auto_evt_autopay` / `auto_agg_relationship_discount`.

**Verdict of the charter-global re-derivation:** no SOURCE-POLICY RED. The observations are R3-O1, N2, N3, O1-O7, O10 and O11.

### post-reveal addendum (revision 3)

Written after the KB reports (21:30:03Z) and the round-3 task JSONs (21:30:21Z) were read. The `charter_global_frozen (revision 3)` section above was hashed at 21:29:59Z (9be2b99d…) and not edited afterwards.

- The KB reports' source-side items P1, P2 and P3 and their N2 (tool examples) match the ones this section verified before the reveal: all four are closed in the round-3 charter and tools.
- The KB report's N1 (the means clause rendered only through the workflow) is a render-layer note. It is not this audit's N1 (overwrite b being too wide), which is closed by the withdrawal of (b).
- **No charter-global defect remains.**
- A mechanical confirmation script found a per-task regression: **F2** (see `0.md` revision_3). Task 0's `design_rationale` [7] still quotes E1's round-2 condition and policy_source ("Before an enrollment is recorded, the loan must have no installment past due …"). That sentence is no longer in the enrolment rule (substring test False), while `prerequisite_closure.edges[0]` equals the charter (True). Task 0's `design_rationale` [3] still says the cancel policy has "overwrite []", but it has 2 entries. These are task-artifact proof defects, not charter defects.

### closing_checklist (revision 3)

**Status: the difficulty does NOT close in revision 3.** Task 0 carries F2: SOURCE-POLICY RED and SOURCE-CHAIN RED on stale proof sentences. The charter, the tools and both scored solutions are correct.

| Item | State |
| --- | --- |
| Per-task files one-to-one; revisions traceable | `0.md` and `1.md`, each with revision 1, `## revision_2` and `## revision_3`. Older text is untouched. |
| Every comparison carries a PASS | **No.** Task 0: SOURCE-POLICY RED (F2-L2), SOURCE-CHAIN RED (F2-L1), unique solution PASS. Task 1: PASS / PASS / PASS. |
| Extended policies fully covered; scopes disjoint | Yes (round-3 `charter_scope`: the 3 + 3 extended policies, the workflow on task 0, and 4 + 3 tools). |
| Exactly one workflow, one claimant; zero-wait fields | Yes (task 0; four gold steps with `requires_external_wait` false and a `zero_wait_proof`). |
| Tools and GT closed; uuid8 | Yes. Tool names and uuid8s are unchanged; the round-3 edits are docstring examples only. |
| Each tree has ≥ 2 prerequisites, ≥ 1 value_input, no cycle; whole-difficulty DAG | Yes (E1-E4 as before; E1 is value_input consistent with the rule). |
| Gates on the final form | Not applicable. The difficulty is not in final form while F2 is open. The coordinator's post-rework snapshot (all 7 exit 0) is cited. The gates do not examine the design_rationale text that F2 concerns. |

Observations still open: N2, N3, R3-O1 (P1 and (c) split one base sentence), O1-O7, O10, O11, OB-T0-1, OB-T0-2, and F2-L3/L4/L5.

Per-task verdicts, revision 3:
- Task 0: **SOURCE-POLICY RED + SOURCE-CHAIN RED** (F2, stale proof text in `tasks/0.json` `design_rationale` [3] and [7]; unique solution PASS).
- Task 1: **PASS**.

## revision_4

### charter_global_frozen (revision 4) — carried forward by hash

- Re-audit round 4. Freeze time: 2026-09-12T21:38Z. That is before I opened the round-4 task JSONs (0.json 6c3ba88e…, 1.json 91f1727f…).
- `auto.extended.yaml` sha256 47876ef9…8afa and `task_tools.py` sha256 51e8146c…8ce6 are both **identical** to revision 3. I recomputed the hashes, and the extended file also matches my round-3 snapshot `audit_auto/ext_r3.yaml`. `blueprint/products/auto.yaml` d467be87… is unchanged.
- Under the re-audit rule, the revision-3 charter-global sections carry forward by reference, with the two hashes as the grounds. That covers: the change list, the mechanical re-checks, the override sweep (F1, P1, P2 and P3 closed; N1 closed) and the verdict "no SOURCE-POLICY RED at charter level". Nothing is re-derived.
- Views: task 0 2ff7d98e… and task 1 e12a670e…, both unchanged since revision 3.
- Gate snapshot after the rework, as the coordinator supplied it: all 7 gates exit 0.
- contamination_disclosure: rounds 1-3 GT and the KB reports have been read. This revision is not blind. The anchor is still the revision-1 blind derivation.
- The open item from revision 3 is per-task: F2 (task 0 proof text). It is re-judged in `0.md` revision_4.

### closing_checklist (revision 4)

Written after the round-4 reveal at 21:38:15Z. The revision-4 charter section above was hashed at 21:38:01Z (0fffca67…).

**Status: the difficulty CLOSES in revision 4.**

| Item | State |
| --- | --- |
| Per-task files one-to-one; revisions traceable | `0.md` and `1.md` with revisions 1-4. Older text is untouched. |
| Every comparison carries a PASS | Yes. Task 0 revision 4: PASS / PASS / PASS (F2 closed). Task 1 revision 4: PASS / PASS / PASS. |
| Extended policies fully covered; scopes disjoint across whole trees | Yes. Task 0: catch-up, cancel, enrol + workflow, with 4 tools. Task 1: two waivers + payoff, with 3 tools. |
| Exactly one workflow, one claimant, zero-wait fields | Yes (task 0). |
| Tools and GT closed; independent frozen uuid8 per tool | Yes. The tool module is unchanged since revision 3; the names and uuid8s are the same as in revision 1. |
| Each tree has ≥ 2 prerequisites, ≥ 1 value_input, no cycle; whole-difficulty DAG | Yes. E1 (value_input) and E2 (state_gate) for task 0; E3 and E4 (value_input) for task 1. No cross-task edge. |
| Gates on the final form | The coordinator's post-rework snapshot on these exact hashes (extended 47876ef9…, tools 51e8146c…, tasks 6c3ba88e… / 91f1727f…) has EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE all exiting 0. I cite it; I did not re-run the gates (Step 0). |

Observations carried (none has a demonstrated consequence in either task world):
- N2: cancel's policy gate on the due-day change cannot be declared.
- N3: the waiver rules extend `auto_evt_autopay` outside their refs.
- R3-O1: two overwrites split one base sentence.
- O1-O7, O10, O11.
- OB-T0-1: E2 is value-invariant.
- OB-T0-2.

Per-task verdicts, revision 4:
- Task 0: **PASS**.
- Task 1: **PASS**.

## revision_5

Re-audit round 5, by a new, independent auditor (clean session; not the author of the artifacts and not the auditor of revisions 1-4, whose session cannot be resumed). The text of revisions 1-4 above is left untouched. Everything under `### charter_global_frozen` was written and appended to this file **before** any masked task field, any earlier revision of this file and any KB-audit report were read. The material under `### post_reveal_revision_5`, further down, was appended only after the freeze.

### charter_global_frozen

- Auditor: policy-task auditor, round 5 (independent session). Freeze time: 2026-09-13T17:46Z (UTC). Commands were run from `/home/ubuntu/github/enterprise_rl`.
- Frozen inputs and hashes (verified against `MANIFEST.sha256` in the orchestrator's masked-view directory):
  - `env/regional_retail_bank/tasks/auto_loan_payment_servicing/auto.extended.yaml`: sha256 `223a222a1058942cc40e0e0beea372b1f19681b46bc14b7bebe2a596de471e91`
  - `env/regional_retail_bank/tasks/auto_loan_payment_servicing/task_tools.py`: sha256 `51e8146c035283d4f893ebd79a0c6a70d4a009fe3be50d5092e279fc54708ce6`
  - `task_0.masked.json` `ab09fad5…c361` (cut from `tasks/0.json` sha256 `d5b79a8b…5ddd`), `task_1.masked.json` `c08f3a4a…0c33` (cut from `tasks/1.json` sha256 `0cb44e8f…ec84`). Each view holds only `frozen_time`, `user_scenario` and `initial_state`.
- Why this is a full re-derivation: `git diff --stat HEAD` shows the extended charter changed in the rework (26 lines) and `task_tools.py` did not. I have not read revision 4, so I cannot carry anything forward by reference. Every section below is derived from scratch.
- Base copy: lines 1-1364 of the extended charter are **byte-identical** to `blueprint/products/auto.yaml` (`diff` is empty). A yaml-level comparison of all 10 base keys (category … policies) also finds no difference.
- Permitted and read before the freeze: the blueprint (`blueprint.yaml`, `products/auto.yaml`, `share_tools.py`, with `db_schema.json` consulted through the finders), the extended charter, `task_tools.py`, `erlbench/{tools,scoring}.py`, and the DSL evaluator `skills/erl-task-instantiate/scripts/check_compute.py`, read for the semantics of `CFIELD`/`LATEST`/`RND`/`DAYS` only, with no task run through it. I also read the two masked views and ran runtime share queries through `audit_kit/rq.py` to confirm reachability. Its outputs were the runtime rows only: 2 checking accounts, 1 loan and 22/31 loan entries per task, identical to the masked `initial_state`.
- Masked and unread at freeze: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, all of `audits/` (including revisions 1-4 of these files and `audits/policy_kb/…`), `docs/`, and the other agents' files in the shared scratchpad. I ran no recursive search under `env/`. The only contact with `audits/` was a file listing plus `grep -c "^## revision_"` to find where to append.
- Entry conditions (Step 0): the orchestrator re-ran the instantiation gates on the current tree and supplied the snapshot in the brief. Cited, not re-run: EXTENDED OK (extended_policies=6, workflows=1, task_tools=7, tasks=2, workflow_guided_tasks=1); TASK TOOL CONTRACT OK; REPLAY OK (0.json 13/26/26, 1.json 11/35/35); SOLVABILITY OK; COMPUTE OK (suite means factors=30.50 branches=18.00 steps=12.00); GROUNDING OK; TRACEABILITY OK (it reads the published KB, which predates this rework); SCOPE OK. The masked views and their hashes were supplied. Input complete.

#### policy_conflict_scan

The structured policy is 13 base policies plus 6 extended policies plus 1 workflow.

| Subject (event) | Policies acting on it | Conclusion |
| --- | --- | --- |
| `auto_payment` (scheduled) | base `auto_evt_payment_allocation`; ext `auto_ext_catchup_installment_payment` (`post_installment_payment_660c6229`) | Compatible. The ext policy fixes the payment amount (shortfall capped by the paying account's posted funds) and splits it in the base allocation order. Base inherited: cutoff/credit date, active/delinquent status, satisfaction at ≥ monthly_payment, no early satisfaction of later installments. |
| `auto_payment` (payoff) | base `auto_evt_payoff_and_lien`; ext `auto_ext_payoff_settlement` (`post_payoff_payment_63569e96`) | Compatible. Payoff = principal + accrued + fees due (+ penalty 0). The ext policy recomputes principal and fees due from the ledger (see O3) and posts nothing when funds are short (base "a shortfall leaves the loan open with the payment applied normally" describes a payment that was posted, so the two do not collide). |
| `auto_set_autopay` (cancel / enroll) | base `auto_evt_autopay`, `auto_agg_relationship_discount`; ext `auto_ext_autopay_cancel_rate`, `auto_ext_autopay_enroll_rate` | Every base clause these two policies replace is named in `overwrite` (see override_declarations). The two ext policies bind distinct tools. The cancel/enroll pair is ordered by the enroll rule ("recorded only on a loan with no enrollment standing"). |
| `auto_change_due_date` | base `auto_due_date_change` only (tool `change_due_day_df9bec35`, `computed_by: []`) | No extended policy touches it. Its gate "The loan must be active with no installment past due" is what orders the workflow's step 0 before step 1. The cancel rule's ordering sentence puts the due date change before the cancellation. The two orderings are compatible. |
| `auto_fee_waiver` | base `auto_evt_fee_waiver`; ext `auto_ext_closed_source_returned_fee_waiver`, `auto_ext_closed_source_late_charge_waiver` | Compatible. Both ext policies use the base bank_error ground ("any fee assessed contrary to this charter … no limit") and the base once-only dedup. They are disjoint by fee_code (returned_payment vs late_charge) and by tool. |
| triggers | `on_request` (catchup, cancel, enroll, payoff); `state_due` (both waivers) | The `state_due` waivers are evaluated whenever the state is due. They fire only when the returned or late-charged debit was presented to an account whose `closed_date` precedes the debit's `posted_date`. |
| time anchors | credit date = frozen date (business day, before 17:00 ET); accrued interest from `last_payment_date` exclusive to credit date inclusive; due-change window 365 days from `last_due_date_change_date`; grace days by state | No two policies anchor the same quantity differently. |
| cross-category reads | checking only: `status`, `ledger_balance` (catchup, payoff); `variant_name`, `opened_date`, `closed_date` (cancel, enroll); `closed_date` by `checking_account_id` (waivers) | Each ext policy declares its checking reads in `cross_category`, and those reads match the `CFIELD` calls. Account selection is the subject of R5-G1/R5-G2. |

**Scope partition (to be checked against `charter_scope` at reveal).** From the charter and the two worlds I expect this partition:
- Task 0 claims the workflow `auto_wf_autopay_source_change` with catchup, cancel_rate and enroll_rate, plus the base due date change as a workflow step.
- Task 1 claims payoff_settlement with its two waiver prerequisites.

The two scopes are pairwise disjoint, jointly cover all 6 extended policies, and give exactly one workflow task.

#### rule_compute_equivalence

Check 2, run over all six extended policies. Each binding's `compute_basis` quotation was located verbatim in its rule. Items not listed below map one-to-one.

- **catchup.** `due`, `credited`, `returned_id` (most recent reversal, `LATEST … date_field='posted_date'`), `returned_credit`, `shortfall` (`MX(0, …)` = "never below zero"), `amount` (lesser of ledger_balance and shortfall), `fees_due` (auto_fee − settlement − waiver), `fees_portion` (`MN`), `principal` (disbursement − Σprincipal_portion + Σreversal), `accrued` (single `RND` on the final figure, `DAYS(last_payment_date, NOW)` = exclusive/inclusive), `interest_portion` (`MN`) and `result` all correspond. The exception is **`funds = CFIELD('checking','ledger_balance', status='active') or 0`** (→ R5-G2).
- **cancel_rate / enroll_rate.** `rec_auto`/`rec_rel` read the name in `rate_discounts`. `pre_rate` caps the recorded discounts at `max_total_discount_pct`. `kept`/`total_disc` apply the cap once to the sum. `raw_rate` branches on `autopay_discount_removed_on_cancel` (cancel only). `result` applies the floor and then `RND(…,2)`. `autopay_added` = `days_past_due == 0`. All of these correspond. The exception is **`held_premier`/`held_private`** (→ R5-G1).
  - Minor: the compute hardcodes the two tier names instead of reading `relationship_qualifying_checking_tiers`. The list is `[Premier Checking, Private Client Checking]` in all six variants, so no value in the domain diverges (observation O5).
- **returned_fee_waiver.** `fee_id`/`returned_pay` (latest returned_payment fee and the payment it names), `channel`/`debit_date`/`paying_account` (read from that payment), `source_closed` (`CFIELD` keyed on a unique `checking_account_id`), `pcb_error` (`channel=='autopay_pcb'`, closed_date non-empty, strictly earlier than posted_date), `prior_waivers` (once only) and `result` all correspond.
- **late_charge_waiver.** `charge_id`/`charge_installment` (latest late_charge), `debit_id` (latest `autopay_pcb` payment toward that installment), `reversals` (≥1 reversal naming it), `source_closed` (unique `checking_account_id`), `pcb_error` and `result` all correspond.
- **payoff_settlement.** `principal`, `fees_due`, `days`, `accrued` (one rounding), `penalty` (0 when pct is 0), `payoff` and `result` (0 when funds < payoff) correspond. The exception is **`funds = CFIELD('checking','ledger_balance', status='active') or 0`** (→ R5-G2).
- **Sweep back.** No compute binding reads a quantity the rule does not state, apart from the two account-selection reads named above (they select by table order, which the rule never states).
- **Rounding.** Every "rounded half-up / rounded to the cent / two decimal places" sentence maps to `RND`. The instantiation skill defines "rounding to `RND`" as the mapping. The evaluator implements `RND` as Python `round` on a float, which differs from decimal half-up only on exact half-cent inputs. That is an evaluator property, not a charter one, and the per-task files check that no scored figure sits on a half-cent (observation O7).

#### action_binding_and_uuids

Check 3.
- `(target_tool, computes)`: `(post_installment_payment_660c6229, principal_portion)`, `(cancel_autopay_a2c51ad3, interest_rate)`, `(enroll_autopay_b9bffdb4, interest_rate)`, `(waive_returned_payment_fee_ab31cb83, amount)`, `(waive_late_charge_e8055e73, amount)`, `(post_payoff_payment_63569e96, amount)`. Each pair is claimed by exactly one policy.
- `change_due_day_df9bec35` is claimed by no extended policy. It is governed by base `auto_due_date_change` and is workflow step 1 with `computed_by: []`.
- The seven uuid8s are `660c6229, df9bec35, a2c51ad3, b9bffdb4, ab31cb83, e8055e73, 63569e96`. They are pairwise distinct, share no common prefix or tail pattern, and form no arithmetic sequence. Nothing indicates batch derivation.
- Each tool's owner matches the charter:
  - cancel and enroll are `owner="user"`, matching base "Enrolling or cancelling is the borrower's own instruction" and the blueprint summary;
  - payment, due change, waivers and payoff are `owner="agent"`, matching "Waivers, due date changes, payoff posting … are agent service actions".
- **No function body judges a business precondition or a prerequisite.** All seven bodies do `ctx.find` (for customer_id and current balances), then `ctx.create`/`ctx.update` of the arguments given, then return the receipt. No docstring mentions a past-due installment, a standing enrollment or a waiver-before-payoff condition.
- No confirmation, review or wait is added. The `completed` `auto_requests` row that cancel/enroll write is the record of the borrower's own instruction.

#### prerequisite_graph

Check 7.
- `prerequisite` is filled in on all 6 policies and on the workflow (`[]` on catchup, cancel, both waivers and the workflow).
- Edges:
  - E1 `enroll_rate → catchup` (value_input, gate `autopay_added`, resolved_by `post_installment_payment_660c6229`);
  - E2 `enroll_rate → cancel_rate` (state_gate, gate `auto_loans.autopay_enrolled`, resolved_by `cancel_autopay_a2c51ad3`);
  - E3 `payoff → returned_fee_waiver` (value_input, `fees_due`, `waive_returned_payment_fee_ab31cb83`);
  - E4 `payoff → late_charge_waiver` (value_input, `fees_due`, `waive_late_charge_e8055e73`).
- Every `problem` names an extended id in this file. None names a base policy or itself. The graph is two disjoint in-stars and is acyclic.
- `policy_source` is verbatim in the cited rule for each edge:
  - E1 = enroll rule "When the loan has an installment past due and the borrower brings it current in the same call, the scheduled payment is posted before the enrollment is recorded, so that the enrollment is recorded on a loan with no installment past due and carries the autopay discount."
  - E2 = enroll rule "A new enrollment is recorded only on a loan with no enrollment standing; when the borrower moves autopay to a different checking account, the standing enrollment is first cancelled under its own rule, and the enrollment is then recorded from the new account."
  - E3 and E4 = the two "Before the payoff amount is fixed, …" sentences of the payoff rule.
- Each `condition` agrees with its sentence.
  - E1 omits the rule's "and the borrower brings it current in the same call" qualifier, but restates the rule's own `autopay_added` sentence ("added at enrollment only when … days_past_due is zero"). It is therefore neither strengthened nor weakened in effect.
- `kind` matches `gate`: `autopay_added` and `fees_due` are real bindings of the dependent compute, and `auto_loans.autopay_enrolled` is a real field and gate.
- Each `resolved_by` tool genuinely produces its `effect`:
  - the payment tool writes `days_past_due` as given;
  - cancel writes `autopay_enrolled=False`;
  - each waiver adds a waiver row to the ledger and lowers `fees_due`.
- No authoring-viewpoint phrasing: a scan of the charter for "this task / at the opening / current world / in the task" returns nothing.

#### override_declarations

Check 1, finding half. Each `base_policy_refs` entry is taken sentence by sentence.

- **catchup** (refs `auto_evt_payment_allocation`, `auto_evt_payoff_and_lien`; `overwrite: []`).
  - Allocation sentences followed: accrual on principal from `last_payment_date`, cutoff and business-day credit, status gate, fees→interest→principal with settlement trigger, `last_payment_date` = credit date, satisfaction at ≥ monthly_payment, no early satisfaction, and principal-only (not reached).
  - Two quantities are handled by an extended-specific formula, with no overwrite:
    - (i) "standing credit" subtracts only the payment named by the **most recent** reversal. Base `auto_evt_returned_payment` makes every returned payment's installment unsatisfied again, so the two diverge only when two or more returned payments were credited toward the same installment (O2).
    - (ii) principal and fees due are recomputed from the ledger instead of read from `principal_balance`/`fees_due`. These diverge only after a waiver of an already-paid fee, whose principal credit the ledger formula does not see (O3).
  - "Payments from a PCB checking account debit that account through the payment's trigger": the tool does not implement that trigger (O1).
  - Payoff sentences: not reached by a scheduled payment.
  - Consequences are demonstrated per task.
- **cancel_rate** (refs `auto_agg_relationship_discount`, `auto_evt_autopay`). Two clauses are replaced, each named verbatim in `overwrite`: "When autopay is cancelled … the APR rises by the autopay discount actually applied" and "cancelling removes it on the same schedule …". After replacement the merged semantics are unique: rebuild from the recorded discounts, in force from the cancellation. Every other sentence is followed:
  - relationship granted at funding, fixed for life, not added later, not removed on closure (made concrete by the funded-date test);
  - discounts stack to the cap and floor;
  - the relationship discount is unaffected by autopay;
  - owner = borrower; loan active or delinquent;
  - APR changes leave monthly_payment alone.
- **enroll_rate** (same refs). Two clauses are replaced and named: "Enrolling adds … from the next installment due at least autopay_lead_days …", replaced by the days_past_due gate at enrollment, and "and re-enrolling later restores it". The rest is followed, including "The autopay source must be a checking account of the same customer in active status when autopay is enrolled."
- **returned_fee_waiver / late_charge_waiver** (ref `auto_evt_fee_waiver`; `overwrite: []`). Followed:
  - waived in full as one row with `source_item_id` = fee;
  - bank_error has no limit;
  - waived once;
  - the already-paid part goes to principal on the waiver date;
  - courtesy gates, which are not used.
  - The "contrary to this charter" ground is new charter text inside each extended rule ("PCB keeps an autopay enrollment drawing only on a source account that is open on each debit date …"). No sentence of the cited base policy keeps a fee in that situation. Base `auto_evt_returned_payment` ("The return also incurs returned_payment_fee") and `auto_evt_late_charge` are uncited, and they describe how a fee is assessed, not whether it may later be waived as bank error. So there is no quantity both clauses fight over (O4).
- **payoff_settlement** (refs allocation, payoff_and_lien; `overwrite: []`). Followed: "The payoff amount on a date is principal_balance plus auto_msr_accrued_interest through that date plus fees_due" (same quantity as long as ledger and fields agree; see O3), payment_type payoff, pays to zero, and the move to paid_off through the trigger.
  - "any excess is refunded": the ext amount equals the payoff exactly, so there is no excess.
  - "a shortfall leaves the loan open …": concerns a payment that was posted; ext posts none.
  - The lien/GAP sentences are not reached by the tool (lien set to release_pending; GAP handled by `auto_evt_gap_refund`).
  - The checking-debit trigger is not implemented (O1).

#### findings (charter-global, pre-reveal)

**R5-G1 — SOURCE-POLICY RED (check 2, rule → compute not lossless: the relationship test over accounts of a tier).**
- *Symptom.* The cancel and enroll rules test existentially over the borrower's checking accounts of a qualifying tier. The compute reads a single account per tier.
- *Evidence.* Cancel rule, repeated word for word in the enroll rule: "it stays when, on the loan's funded_date, the borrower held a checking account of a tier in relationship_qualifying_checking_tiers, meaning one of those accounts was opened on or before funded_date and was not closed on or before funded_date; a qualifying account closed later still counts, and one opened after funded_date never counts." Compute (both policies): `held_premier: "(CFIELD('checking', 'opened_date', variant_name='Premier Checking') or '9999-12-31') <= F('funded_date') and (CFIELD('checking', 'closed_date', variant_name='Premier Checking') or '9999-12-31') > F('funded_date')"`, and the same for `held_private`. `CFIELD` returns `hs[0].get(field)`, the first matching row of the customer's checking table (`skills/erl-task-instantiate/scripts/check_compute.py` `CFIELD`/`_cross`). The DSL offers no inequality filter and no iteration over rows.
- *Demonstrated consequence (same situation, two conclusions).* Take a borrower with two Premier Checking accounts: A (listed first, opened after `funded_date`) and B (opened before `funded_date`, still open). The rule says B was held at funding, so the relationship discount is kept. The compute says `held_premier` = A.opened ≤ funded = False; with no Private Client, `rel_kept` = 0. For a loan recording `autopay_and_relationship` at a rate above the floor, the rule's cancel APR is pre − 0.25 while the compute gives pre − 0; the enroll APR differs by the same 0.25.
- *Root cause.* The rule's domain (any number of accounts per tier) is wider than what the compute expression implements (one account per tier). The instantiation standard itself requires "The formula must cover the complete policy domain, not merely the branch the current seed hits" and "`rule` and `compute` must have equal domains".
- *Affected.* `auto_ext_autopay_cancel_rate` and `auto_ext_autopay_enroll_rate`: rule sentence above and compute `held_premier`/`held_private`/`rel_kept`/`rel_disc`. Both are claimed by task 0 (per-task consequence in `0.md` revision_5).
- *Why RED and not an observation.* Checks 2, 3 and 7 are world-independent by the skill's own division ("None of the three reads a task's world"). For policy self-consistency, the demonstration the skill requires is two verbatim artifact passages reaching different conclusions in the same situation, which the construction above supplies. That the compute language cannot express the existential test does not exempt the pair: it is exactly the reason the rule and compute domains are unequal.

**R5-G2 — SOURCE-POLICY RED (check 2, same class: which checking account caps the payment).**
- *Symptom.* The catchup and payoff rules cap the amount by the paying account's posted funds. The compute reads the ledger_balance of the first active checking row of the customer.
- *Evidence.* Catchup rule: "When a borrower asks PCB to pay … by a transfer from the borrower's own PCB checking account … The transfer is drawn only from posted funds: the paying account is the borrower's checking account in active status, and when its ledger_balance is lower than the shortfall the payment amount is that ledger_balance". Payoff rule: "The transfer is drawn only from posted funds of the borrower's checking account in active status: when its ledger_balance is lower than the payoff amount no payoff is posted". Compute (both): `funds: "CFIELD('checking', 'ledger_balance', status='active') or 0"`.
- *Demonstrated consequence.* Take a borrower with two active checking accounts: A (listed first, ledger 100.00) and B (the one the borrower pays from, ledger 5,000.00), with a shortfall of 438.01.
  - Catchup: the rule caps by the paying account B, giving an amount of 438.01. The compute caps by A, giving 100.00.
  - Payoff: the rule posts the payoff, while the compute gives `result` 0.00.
  - A borrower with no active account gives compute `funds` 0 (amount 0.00), where the rule states no outcome.
- *Root cause.* The account is selected by table order, a basis the rule never states.
- *Affected.* `auto_ext_catchup_installment_payment` `funds`/`amount` (task 0) and `auto_ext_payoff_settlement` `funds`/`result` (task 1).

**Observations (not grounds for rework unless a task file demonstrates a consequence):**
- **O1** (base-section trigger). Base event `auto_payment` declares `checking:checking_debit when payment_channel in [autopay_pcb, pcb_transfer]`, and base allocation says "Payments from a PCB checking account debit that account through the payment's trigger". `post_installment_payment_660c6229` and `post_payoff_payment_63569e96` write `payment_channel="pcb_transfer"` but no checking debit row, and do not lower `checking_accounts.ledger_balance`. No agent tool can write it either. Scored-value impact is judged per task.
- **O2** (catchup, check 1): the most-recent-reversal restriction vs base returned-payment semantics. It diverges only with ≥2 returned payments toward one installment.
- **O3** (catchup and payoff, check 1): the ledger recomputation of principal and fees due ignores the principal credit carried by a waiver of an already-paid fee (`applied_to_principal` in the waiver tools; base "recorded by the same waiver row"). It diverges from `principal_balance`/`fees_due` only after such a waiver.
- **O4** (both waivers): the bank-error ground is extended-side charter text. No cited base sentence conflicts (see override_declarations).
- **O5**: the cancel/enroll compute hardcodes the qualifying tier names; the value is equal in every variant.
- **O6** (catchup): for an active account with negative ledger_balance, the rule literally yields a negative payment amount, which conflicts with the tool's "positive number of dollars". "Drawn only from posted funds" suggests nothing is drawn. Neither world has an overdrawn account.
- **O7**: `RND` = float `round` vs "half-up"; exact half-cent inputs are checked per task.
- **O8**: the workflow block carries `order_rationale` with a zero-wait sentence but no `requires_external_wait` or `zero_wait_proof` keys. `check_solvability.py` reads those keys from the task's `solvability_contract`, to be verified for task 0 at reveal.
