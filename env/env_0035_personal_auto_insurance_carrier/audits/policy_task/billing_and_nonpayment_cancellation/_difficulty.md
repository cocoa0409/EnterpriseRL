# Policy-task audit — billing_and_nonpayment_cancellation / charter-global

## charter_global_frozen

- Auditor: erl-task-policy-audit subagent (independent of the instantiating agent). Revision 1 (no earlier revision exists; the `audits/` tree did not exist before this run).
- Freeze time: 2026-10-05T10:50Z, written before any task's GT was revealed.
- Inputs and hashes (verified with `sha256sum` against the conductor's MANIFEST.sha256, and the two charter files also hashed in place under `env/.../tasks/billing_and_nonpayment_cancellation/`, byte-identical):
  - `billing.extended.yaml` d662720fe272236fe5a75d80b0b931e71f1803bda50c59e9b3fbec8aa287d0b2
  - `task_tools.py` e6e71eed2d2848822d31ada9e04e7d249babcd5de770537a4c2adff1de1d914a
  - `task_0.view.json` 8d0899eb03156fdd94ed10a65288b31690e232c9dc0968dbb3c6b4ff336ad466
  - `task_1.view.json` ce93a2762ad42c9d2a6c613446147baa0039a6af58d1506c560f30045e43a4f7
- Also read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/billing.yaml` (base charter), parameter rows of `blueprint/products/auto.yaml` (policy_term_months, policy_fee_per_term, renewal_offer_lead_days), and the restricted-expression semantics (`MONTHS`, `DAYS`, `within_months`, `LATEST`, `F`, `P`, `CFIELD`, `CPARAM`, `XCOUNT`) in `skills/erl-task-instantiate/scripts/check_compute.py` lines 224-390.
- Masked and not read before this file was written: `tasks/billing_and_nonpayment_cancellation/tasks/*.json` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure) and `tasks/billing_and_nonpayment_cancellation/worklog.md`. No recursive search ran over `env/` or `tasks/`.
- Entry conditions (Step 0): the gate snapshot `/tmp/erl35_views/billing_and_nonpayment_cancellation/GATES.txt` reports EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; check_traceability is deferred because the KB has not been published. The masked views and their hashes came with the brief. Entry conditions are met.

### policy_conflict_scan

- **Base copy.** Lines 1-1134 of `billing.extended.yaml` are byte-identical to `blueprint/products/billing.yaml`. The only difference is one trailing blank line at line 1135, before the `extended_policies` banner.
- **Extended policies (6), by task claim (from the charter's own `# task 0` / `# task 1` banners):**
  - task 0: `billing_ext_late_fee_charge`, `billing_ext_renewal_down_payment`, `billing_ext_additional_premium_bill`, `billing_ext_assisted_payment` (root).
  - task 1: `billing_ext_installment_charge`, `billing_ext_term_payoff` (root).
  - The two claim sets are disjoint and together cover all six extended policies. This is to be confirmed against `charter_scope` at reveal.
- **Overlapping subjects:**
  - `billing_fee_charged` is shared by the base late-fee, returned-payment, reinstatement and payment-application policies and by `billing_ext_late_fee_charge`. The extended late-fee policy writes only `fee_type=late_fee`, and its amount clause is declared as overwritten (see override_declarations). No other policy computes a late-fee amount.
  - `billing_installment_billed` is claimed by `billing_ext_renewal_down_payment` (installment 1 of a renewal term) and by `billing_ext_installment_charge` ("each installment of the current term after the down payment"). The scopes are disjoint: renewal term vs current term, and installment 1 vs installments 2 and later. The tools are disjoint too: `bill_renewal_down_payment_49af2eee` takes an explicit renewal `term_effective_date`, while `invoice_installment_259ff7d9` always writes the account's current `term_effective_date`.
  - `billing_payment_received` is claimed by `billing_ext_assisted_payment` (rep on the line, settles the whole balance, `pay_balance_by_phone_6aa6e134`) and by `billing_ext_term_payoff` (automated payment line, pays off the current term in advance, `pay_term_payoff_2a94a5fa`). The channel and the object differ, so no request falls under both. One case comes close: on an account with no installment left to invoice, the term payoff formula collapses to the posted balance. Even then the channel separates the two, and in task 0 the persona is explicit about paying "with the representative".
  - The base sentence "The installment_fee is added to every installment after the down payment and to no other bill." is overwritten twice, by `billing_ext_additional_premium_bill` (AP bill carries a billing charge) and by `billing_ext_installment_charge` (each installment carries a computed charge). The two replacements cover disjoint bills, so the merged semantics are unique.
- **Triggers, eligibility and time anchors:** these are inherited from base and unchanged. They are: late-fee grace counting (the day after due_date is day 1, so the fee posts on the first day after the last grace day), the late-fee term cap, notice and reinstatement windows, renewal_bill_lead_days, invoice_lead_days and ap_immediate_due_days. No extended rule restates a base time anchor with a different value.
- **Cross-category read boundaries:** every extended policy reads `auto` only, through CFIELD/CPARAM on the customer's auto policy (policy_state, inception_date, term_expiration_date, policy_term_months). In addition, `billing_ext_renewal_down_payment` reads XCOUNT on `auto_transactions` (auto_driver_add / auto_vehicle_add). These are reads, never writes.
- **Terminal states:** each write tool changes only `billing_ledger` and `billing_accounts.account_balance`. No status transitions are involved.
- **Conclusion:** no conflict in the charter produces two values for one scored quantity in a structural sense. The one wording-level ambiguity that does produce two values is recorded under findings F1. Its consequence is demonstrated in `0.md`.

### rule_compute_equivalence

Check 2 was run binding by binding against `compute_basis` and swept back over every rule sentence.

- **billing_ext_late_fee_charge**
  - Every binding has a verbatim basis.
  - `lf_installment_premium` (LATEST by due_date in the account term) maps to "tied to the installment invoiced last in the current term".
  - `lf_paid_in_window` (SUM payments − SUM returns, within_months=1) maps to "payments posted less than one whole month before the charge date, less the returned payments posted in that same window". `within_months` matches "less than that many whole months ... counted on calendar months", because `MONTHS` subtracts one when the day-of-month has not been reached.
  - The charged-share three-way branch, the loyalty, returned-payment and repeat ladders, and the single final RND are all present on both faces.
  - Swept back: the sentence "The late fee charge on an installment is the pay plan's late fee, rounded to the cent" is the baseline. It has no binding of its own, because the fall-through tiers reproduce it. This is acceptable, but see observation O3 on its categorical wording.
- **billing_ext_renewal_down_payment**
  - Every binding has a basis.
  - The binding `dp_expiring_premium` = SUM(term_premium entries of the account term) quotes "the full-term premium of the term the account currently bills". The rule never says that this is the term-premium entry, whereas it does say so for the renewal side ("the renewal full-term premium, which is the term premium received most recently on the account"). The compute therefore fixes a basis ("term-premium entries only, endorsements excluded") that the rule's words leave open. This is finding F1.
  - The deposit uses XCOUNT on the customer's auto_transactions with within_months=3 on effective_date. That matches "effective date less than 3 whole months before the bill date".
  - Order of operations ("rounded, bounded, then deposit added, then rounded") is equivalent on both faces.
- **billing_ext_additional_premium_bill**
  - Every binding has a basis. The size method, the relief ladder (exactly-one-holds), the offset ladder, the floor at zero and the single final RND are equivalent.
  - The rule's first sentence (billed at once when received after the last installment of its term was invoiced, due ap_immediate_due_days later) is the scope and due-date clause. It is not computed and it is carried by the tool's `due_date` argument.
- **billing_ext_assisted_payment**
  - Every binding has a basis.
  - `as_balance` sums exactly the event families the rule lists. `billing_premium_change` is correctly excluded, and there is no term filter, which matches "posted on the account".
  - The purpose ladder uses DAYS(posted, NOW) ≤ 5, matching "no more than 5 calendar days before the payment date".
  - Swept back: the rule sentence "No fee is charged when the payment cures a notice of cancellation or reinstates the account." has no branch in compute. That makes it a promise the compute does not implement. In neither task's world does the account carry a notice or a cancellation, so no scored value depends on it. Recorded as observation O1.
- **billing_ext_installment_charge**
  - Every binding has a basis.
  - The premium portion is (term + AP − RP − already invoiced) / installments not yet invoiced, rounded, with the last installment taking the rest. The installment count is 1 + (term months / interval − 1) via CPARAM. The charge method has three branches (under $175 pro rata; last installment ≥ $175 half; otherwise whole). The relief ladder, the two additions, the floor and the final RND are equivalent.
  - The base `min_installment_amount` combining clause is inherited and not computed. Neither world triggers it.
- **billing_ext_term_payoff**
  - Every binding has a basis.
  - The posted payoff balance matches the event families listed. The premium still to be invoiced, the remaining count, the fee share, `RND(plan installment fee × remaining × share)`, the credit-rate ladder, the credit-base ladder on DAYS(payoff date, term expiration), the eligibility ladder, `RND(credit)` and the final RND are all equivalent.
- **Factor tiers:** every tier named in `factors[].ladder` is a sentence of its rule and a branch of its `decides` binding, and every branch is a stated tier. No tier exists on only one face.
- **Baseline sentences:** a scripted check confirmed that every sentence of every `baseline.rule` occurs verbatim in that policy's `rule`.

### action_binding_and_uuids

- `(target_tool, computes)` pairs, each claimed by exactly one policy:
  - (charge_late_fee_8c3b3141, amount)
  - (bill_renewal_down_payment_49af2eee, amount)
  - (bill_additional_premium_a7869908, amount)
  - (pay_balance_by_phone_6aa6e134, amount)
  - (invoice_installment_259ff7d9, installment_fee)
  - (pay_term_payoff_2a94a5fa, amount)
- uuid8s: 8c3b3141, 49af2eee, a7869908, 6aa6e134, 259ff7d9, 2a94a5fa. They are pairwise distinct, share no prefix, follow no sequence and show no adjacent-value pattern. Each appears to be independently generated.
- Owners: the two payment tools are `owner="user"` and the four billing writes are `owner="agent"`.
- Docstrings:
  - No docstring names another tool, states a position in a sequence, or adds a confirmation, review or wait.
  - The only ordering words are in return-value descriptions, such as "the balance after the charge / invoice / bill / payment". These describe the tool's own effect and are recorded as observation O6.
  - The module docstring says "No tool checks eligibility, prior steps or amounts", and the bodies confirm it. Each function does only `ctx.find(...)[0]` on the account, then `ctx.create`, then `ctx.update`. None has a branch on the ledger state, a prerequisite, or an amount check (`task_tools.py` lines 41-54, 89-108, 141-155, 186-210, 245-269, 300-313).
- Each policy's subject, base refs, target tool and docstring admit a single business reading.

### prerequisite_graph

- `prerequisite` is filled in on all six extended policies: four are `[]`, and two carry edges.
- Edges:
  - billing_ext_assisted_payment → billing_ext_late_fee_charge (value_input, gate `as_balance`, state form)
  - billing_ext_assisted_payment → billing_ext_renewal_down_payment (value_input, gate `as_balance`, state form)
  - billing_ext_assisted_payment → billing_ext_additional_premium_bill (value_input, gate `as_balance`, state form)
  - billing_ext_term_payoff → billing_ext_installment_charge (value_input, gate `po_balance`, state form)
- Structure checks:
  - Every `problem` is an extended policy id in this file. None points at a base policy or at itself.
  - The graph is two stars of depth 1, so it is acyclic.
  - All four `policy_source` strings were verified verbatim (whitespace-normalised) inside their own policy's `rule` by script.
  - `form` is `state` on all four edges and no `fallback_reason` is present, which is consistent.
  - Each `gate` names a binding that exists in that policy's compute (`as_balance`, `po_balance`).
  - Each `resolved_by` equals the depended-on policy's `target_tool`.
- Each `effect` was checked against the tool body:
  - The late-fee entry raises `as_balance`.
  - The renewal invoice plus its policy fee raise `as_balance`, and its posted_date of today feeds `as_last_down_invoice`.
  - The AP bill raises `as_balance`.
  - The installment invoice raises `po_balance`, raises `po_billed_count` and lowers `po_unbilled`.
- Each `condition` against its sentence:
  - Late fee: the condition adds "beyond the underpayment tolerance". The sentence says "the late fee owed", and the late-fee rule owes a fee only beyond the tolerance, so the strength is equal.
  - Renewal: the condition adds "with its policy fee". The renewal rule makes the policy fee part of the same invoice ("invoiced with it as a separate charge"), and the one tool posts both, so this is not a strengthening that changes the resolving write.
  - AP and installment: the conditions match their sentences.
- No authoring-viewpoint phrasing was found ("in this task", "at the opening", "current world", "this task"; scripted scan of every `rule` and `prerequisite`).

### prerequisite_sentences

Check 6 was applied to each edge.

- **E1. Assisted payment waits on the late fee.** Sentence: "The assisted payment amount is fixed only after the account carries the late fee owed on every installment of the current term that stayed unpaid past its grace days."
  - Four-point test:
    - The connective is "only after".
    - The waited-on thing is a record-visible state: late-fee entries on the account, keyed by installment.
    - It names no tool, no policy id and no snake_case token.
    - Its scope ("every installment of the current term" past grace) matches the condition.
  - Exactly one write of the difficulty creates a late-fee entry: `charge_late_fee_8c3b3141`, under `billing_ext_late_fee_charge`.
  - Derivation:
    1. The late-fee rule says a late fee charge "is booked once on an installment of the current term that is still unpaid, beyond the underpayment tolerance, when its grace days have ended".
    2. Read against the ledger, this identifies which installments owe one and lack one.
    3. The late-fee policy's own write is the resolving action.
  - There is a single reading.
- **E2. Assisted payment waits on the renewal down payment.** Sentence: "The assisted payment amount is not worked out until the account carries the renewal down payment invoice for a renewal term whose renewal bill date has arrived."
  - Four-point test: the connective is "not … until", the state is record-visible (installment 1 of the renewal term on the ledger), and there is no tool or id.
  - The renewal bill date is defined in base (`renewal_bill_lead_days before the term expiration date`) and in the renewal rule ("invoiced on the renewal bill date").
  - Exactly one write creates installment 1 of a renewal term: `bill_renewal_down_payment_49af2eee`. The other installment writer (`invoice_installment_259ff7d9`) is scoped by its policy to "the current term after the down payment", and its body always writes the account's current term.
  - There is a single reading.
- **E3. Assisted payment waits on the additional-premium bill.** Sentence: "Before the assisted payment amount is fixed, every additional premium received after the last installment of its term was invoiced must stand on the account as an additional-premium bill."
  - Four-point test: the connective is "Before", the state is record-visible (an endorsement-charge entry per such additional premium), and there is no tool or id.
  - Exactly one write: `bill_additional_premium_a7869908`. The AP-bill rule's first sentence restates the same scope ("An additional premium received after the last installment of its term was invoiced is billed at once"). That sentence is the depended-on policy's own rule, not a restatement of the prerequisite sentence, and it names no other problem.
  - There is a single reading.
- **E4. Term payoff waits on the installment invoice.** Sentence: "The term payoff amount is fixed only after the account carries the invoice of every installment of the current term whose invoice date has arrived."
  - Four-point test: the connective is "only after", the state is record-visible (an installment entry per installment whose invoice date has arrived), and there is no tool or id.
  - The invoice date is defined in the installment-charge rule ("invoiced invoice_lead_days calendar days before its due date") and in base.
  - Exactly one write: `invoice_installment_259ff7d9`.
  - There is a single reading.
- **Depended-on rules and stray orders:**
  - None of the depended-on rules (late fee, renewal down payment, AP bill, installment charge) mentions the assisted payment or the term payoff.
  - No rule states a cross-problem order that grounds no declared edge. The AP-bill scope clause "received after the last installment of its term was invoiced" is a temporal condition on when the premium arrived, not an order between writes.
  - No base sentence is used to ground an edge.

### override_declarations

Check 1's finding half was run sentence by sentence against each `base_policy_refs` entry.

- **billing_ext_late_fee_charge** (refs: installment_schedule, late_fee, returned_payment, reinstatement, payment_application)
  - Declared: base late_fee sentence 1 ("A late fee of the plan's late_fee is charged once … at the end of late_fee_grace_days") is replaced by a booked-once, computed amount.
  - Inherited unchanged: the no-late-fee exclusions (new-business down payment, final earned-premium bill, account not current, term cap `billing_msr_late_fees_term`), the grace-count sentence, and the courtesy and posting-error waiver sentences.
  - The extended rule's "posted on the first day after the last grace day" equals base's counting rule.
  - The extended rule adds "tied to the installment invoiced last in the current term". Base ties the fee to "an installment that is still unpaid". These coincide when the unpaid installment is the last one invoiced. They diverge when an earlier installment is the unpaid one, and in that case the extended rule is also internally strained (observation O2). Neither task's world is such a case.
  - The installment_schedule, returned_payment, reinstatement and payment_application sentences are not touched.
  - No undeclared override.
- **billing_ext_renewal_down_payment** (ref: installment_schedule)
  - Declared: the down-payment sentence is replaced for renewal terms. The new-business sentence is restated unchanged in the extended rule.
  - "The renewal down payment is billed renewal_bill_lead_days before the term expiration date" is followed.
  - "The policy fee of the auto package is billed once per term with the down payment" is followed (a separate charge on the same invoice).
  - The even split of the remainder and the installment fee are not touched.
  - No undeclared override.
- **billing_ext_additional_premium_bill** (ref: installment_schedule)
  - Declared: "installment_fee … to no other bill" is replaced by an AP billing charge.
  - "spread_over_remaining_installments … when none remain it is billed at once due in ap_immediate_due_days; bill_immediately bills it at once due in ap_immediate_due_days" is followed: the scope sentence equals "none remain", and the due date is the same.
  - The extended policy is silent on the plans whose `ap_billing_method` is `bill_immediately` (Paid-in-Full): its scope sentence covers only AP received after the last installment. Neither task's world is on that plan.
  - No undeclared override.
- **billing_ext_assisted_payment** (refs: cross_account_payments, reinstatement, payment_application)
  - Declared: the phone-representative fee sentence is replaced by a computed fee included in the authorised amount.
  - Followed:
    - the application order;
    - accepted methods;
    - certified funds;
    - posting cutoff;
    - "no fee is charged when the payment cures a notice of cancellation or reinstates the account" (restated in the extended rule);
    - the overpayment handling;
    - the cross-account rules ("posted to the one account the customer names");
    - the reinstatement-payment formula (not touched).
  - No undeclared override.
- **billing_ext_installment_charge** (ref: installment_schedule)
  - Declared: the installment_fee sentence is replaced by a computed installment charge.
  - The premium portion restates the base even split. "reduce_remaining_installments lowers the installments not yet billed evenly" is followed: return premium is subtracted from the not-yet-invoiced premium before the split. "Any cent left by rounding goes on the last installment" is followed: the last installment takes the rest. "Invoices are issued invoice_lead_days before each due date" is followed.
  - No undeclared override.
- **billing_ext_term_payoff** (refs: cross_account_payments, reinstatement, payment_application; `overwrite: []`)
  - Payment application: the automated phone line carries no fee, which is followed (the tool posts no fee). Accepted methods are followed. "An overpayment stays on the account as a credit applied to the next installment where overpayment_applied_to_next_installment is true" is followed (the tool docstring says the excess "stays on the account as a credit for the installments still to come").
  - The payoff's "plan's installment fee for each installment still to be invoiced" is a quantity inside a payment amount, not a fee charged by the payoff. No base sentence governs a payoff amount, so the empty `overwrite` is consistent.
  - Its relation to `billing_ext_installment_charge` (future invoices carry computed charges, not the plan fee) is observation O4.
  - No undeclared override.
- **Disguised forms:** no anonymous intermediate factor, 0/1 multiplier or dropped branch was found against base. The payoff eligibility tier "none of it" is a multiplier of 0 on a credit that base never defines, so it zeroes nothing base fixed.

### factor_ladders

Factor structure is charter-global. Weight-bearing is judged per task.

- **billing_ext_late_fee_charge** has 5 factors (4 parameter, 1 method):
  - `late_fee_state_amount` (P): KY $10 / VA-WV $12 / plan late fee. Cross-difficulty, auto policy_state.
  - `late_fee_charged_share` (M):
    - pro rata on the unpaid part, when net payments in the last whole month are above zero but short of the installment total;
    - 10 % of the installment total, when nothing was paid in that window and the installment total is under $100;
    - otherwise the whole amount.
    - Multi-source: payments and returns ledger plus the installment invoice and fee.
  - `late_fee_loyalty_rate` (P): 0.50 / 0.75 / 1.00. Multi-source and cross-difficulty: notice ledger AND auto inception_date.
  - `late_fee_returned_payment_rate` (P): 1.50 / 1.25 / 1.00.
  - `late_fee_repeat_rate` (P): 1.40 / 1.20 / 1.00.
- **billing_ext_renewal_down_payment** has 6 factors (5 parameter, 1 method):
  - record percentage (P): 30 / 25 / plan %. Multi-source: returns AND or OR late fees.
  - tenure reduction (P): 5 / 2.5 / 0. Cross-difficulty, auto inception.
  - notice surcharge (P): 10 / 5 / 0.
  - method reduction (P): 3 / 1 / 0.
  - increase base (M): expiring + ½ increase / expiring + ¾ increase / renewal premium.
  - new-driver deposit (P): $75 / $40 / 0. Cross-difficulty, auto_transactions.
- **billing_ext_additional_premium_bill** has 4 factors (3 parameter, 1 method):
  - state charge (P): KY $2 / VA-WV $4 / plan installment fee. Cross-difficulty.
  - charge method (M): state + 2 % above $75 / half / whole.
  - relief rate (P): 0.50 / 0.75 / 1.00. Multi-source: last payment method AND returns.
  - endorsement offset (P): $1.50 / $0.75 / 0.
- **billing_ext_assisted_payment** has 5 factors (4 parameter, 1 method):
  - state fee (P): KY $2 / VA-WV $3.50 / plan phone fee. Cross-difficulty.
  - fee method (M): state + 0.25 % above $500 / half / whole.
  - loyalty (P): 0.50 / 0.80 / 1.00. Multi-source, auto inception AND returns, cross-difficulty.
  - purpose (P): 0.50 / 0.75 / 1.00. Multi-source: installment-1 invoice and AP bill dates.
  - frequency (P): 1.50 / 1.20 / 1.00.
- **billing_ext_installment_charge** has 5 factors (4 parameter, 1 method):
  - state charge (P): KY $5 / VA-WV $6 / plan installment fee. Cross-difficulty.
  - charge method (M): pro rata under $175 / half on a last installment ≥ $175 / whole.
  - relief (P): 0.50 / 0.75 / 1.00. Multi-source: last payment method AND auto inception, cross-difficulty.
  - returned addition (P): $2 / $1 / 0.
  - late addition (P): $1.50 / $0.75 / 0.
- **billing_ext_term_payoff** has 4 factors (3 parameter, 1 method):
  - prepaid-fee share (P): none / half / all. Multi-source: late fees AND auto inception, cross-difficulty.
  - credit rate (P): 1.5 % / 1.0 % / 0.
  - credit base (M): whole unbilled / unbilled less one share / one share. Cross-difficulty, auto term_expiration_date.
  - eligibility (P): 0 / ½ / 1.
- **Shared structure checks:**
  - Every ladder has three tiers that are pairwise disjoint as stated.
  - Every tier is stated in prose in its `rule` with its condition and value or method, and implemented in `compute`.
  - Every `decides` is an input binding, not `result`.
  - Binding sets within each policy are disjoint.
  - Each factor's fall-through equals its `baseline` binding, and each baseline binding equals what that policy's `baseline.rule` states for that input. The exceptions are the payoff's `credit_base` and `eligibility`, for which `baseline.rule` states no credit at all (observation O5).
- **Label honesty:**
  - Each `method` factor has at least one tier that changes the algorithm (pro rata on a second quantity, a percentage of a second quantity added, or a different credit base). The remaining tiers of those method ladders are scalings.
  - No `parameter` factor changes the algorithm.
  - The labels are honest.
- **Coverage per task:**
  - task 0: multi-source factors present (loyalty, record %, AP relief, assisted loyalty, purpose). Cross-difficulty factors present, reading auto (state ×3, loyalty, tenure, deposit).
  - task 1: multi-source factors present (installment relief, payoff fee share). Cross-difficulty factors present, reading auto (installment state, relief, fee share, credit base).
- **Tier distinctness by plan.** On the Direct Bill Monthly Plan, which both tasks use, all three tiers of every ladder select distinct values. Across the charter's other plans, the state ladders' fall-through can coincide with the KY tier:
  - Late fee: KY $10 equals the plan late fee $10 on the Card Autopay, EFT Autopay and Paid-in-Full plans.
  - AP state charge: KY $2 equals the EFT Autopay installment fee $2.
  - Installment state charge: KY $5 equals the installment fee $5 on Card Autopay, Three-Pay and Two-Pay.
  - This is observation O7. Neither task's world sits on those plans.
- **Realism of conditions and outcomes:**
  - Accepted as things a personal-auto billing department weighs:
    - state-specific fixed fee amounts (fees are filed by state);
    - percentage caps on late fees for small installments;
    - escalation for repeat lateness;
    - tenure and loyalty relief;
    - higher renewal down payments after returned payments or late fees or a recent notice;
    - lower down payments or fees for electronic payers;
    - smoothing a renewal down payment on a rate shock;
    - a deposit after a mid-term driver addition;
    - offsetting a billing charge against a just-charged endorsement fee;
    - a prepayment credit;
    - withholding a prepayment credit from NSF accounts.
  - Weak, recorded as observation O8:
    - a late fee scaled up by returned-payment history;
    - an installment that is "the last of the term and ≥ $175" charged half;
    - a phone fee halved when a renewal invoice is fresh.
  - **Not accepted (finding F3):** the payoff's prepaid-fee-share ladder, whose fall-through (and baseline) charges every remaining installment fee in a payoff, and whose tiers decide the share from late-fee history and tenure.

### findings

- **F1. Renewal down payment rule admits two "expiring full-term premium" readings.** Bears on task 0; consequence demonstrated in `0.md`.
  - Symptom: `billing_ext_renewal_down_payment.rule` compares the renewal premium against "the full-term premium of the term the account currently bills". It defines only the renewal side as a ledger entry ("the renewal full-term premium, which is the term premium received most recently on the account").
  - Compute: `dp_expiring_premium` = `SUM(... premium_change_type='term_premium', term_effective_date=F('term_effective_date'))`, which counts only the term-premium entry.
  - Root cause: the world's own vocabulary names a different figure "full-term premium". In `db_schema.json`, `auto_transactions.full_term_premium_after` is "Full-term premium rated with the change". After a mid-term endorsement, the term the account bills has a full-term premium that differs from its term-premium entry.
  - Neither the rule nor any other charter sentence says that endorsements are excluded from the expiring figure.
  - Class: SOURCE-TASK RED in each task whose world has a mid-term premium-bearing endorsement in the billed term.
- **F2. Term payoff "prepaid installment fees" priced at the plan fee, while future invoices carry computed charges.** Bears on task 1; observation O4. No scored value of task 1 changes.
- **F3. The payoff prepaid-fee-share ladder is not real-world practice.** Bears on task 1; SOURCE-FACTOR RED, demonstrated in `1.md`.
  - The rule's standard payoff and its fall-through charge "the pay plan's installment fee for each installment still to be invoiced".
  - The two better tiers waive half or all of them according to late-fee history and tenure.
  - In US personal-auto billing, installment (service) fees attach to installments as they are billed, and paying the remaining term in full is exactly how a policyholder stops incurring them. Carriers publish "pay in full / pay the remaining balance and you will not be charged further installment fees" to every customer, not as a reward for tenure or a clean late-fee record. Where premium is financed, state premium-finance law requires the unearned service charge to be rebated on prepayment.
  - Two consequences follow. A treatment that collects every future installment fee up front on a payoff is not something such a business publishes for an ordinary customer, which makes the fall-through a straw man. Neither late-fee history nor tenure is a condition the business weighs when deciding whether a payoff incurs future installment fees, so the ladder's conditions are not ones that line of business weighs for this quantity.
- **Observations** (no demonstrable consequence in either task's world):
  - O1. The assisted-payment rule's "No fee is charged when the payment cures a notice of cancellation or reinstates the account" has no branch in compute.
  - O2. The late-fee rule is internally strained when an earlier installment is the unpaid one: it books the fee "on an installment … that is still unpaid" yet ties it "to the installment invoiced last in the current term". In both worlds the unpaid installment is the last one invoiced.
  - O3. The late-fee rule states the baseline categorically ("The late fee charge on an installment is the pay plan's late fee, rounded to the cent."), without the "standard" qualifier the other five policies use. A reader resolves it from the following sentences.
  - O4. After a payoff, `billing_ext_installment_charge` still invoices the remaining installments with computed charges. The payoff prepays the plan fee × share and deducts a credit, so the credit left on the account need not equal what the remaining invoices will carry. The payoff rule's "so that no further installment is left to pay" is therefore not guaranteed by the charter. This is observation-level because the future invoices are not part of either scored solution.
  - O5. For the payoff `credit_base` and `eligibility` factors, `baseline.rule` states no credit at all. Their factor-level baseline bindings (one share; whole) are each factor's fall-through, but `baseline.rule` does not state them. The full baseline (credit rate 0) is still definite.
  - O6. Each docstring's return description uses "after" only to describe that tool's own resulting balance.
  - O7. State ladders' fall-through coincides with the KY tier on some plans (listed above). The difficulty's two worlds are on Direct Bill, where they differ.
  - O8. Weakly grounded but not demonstrably unreal: the late-fee returned-payment multiplier, the half charge on a last installment ≥ $175, and the phone-fee purpose rate.
  - O9. Rules carry raw parameter tokens ("ap_immediate_due_days" in the AP-bill rule, "invoice_lead_days" in the installment rule). Neither is in a prerequisite sentence.

## closing_checklist

This section was written after both reveals (2026-10-05T10:55Z). It sits below the frozen charter-global section, which was not edited after its freeze hash eb82e80b…a9d5. **The difficulty is NOT closed**, because not every task passes all four relationships.

- **Per-task files:** `0.md` and `1.md` match tasks 0 and 1 one-to-one, alongside this file. Revision 1; there is no older revision. Neither comparison section carries an overall PASS:
  - task 0: SOURCE-CHAIN RED (T0-2) + SOURCE-TASK RED (T0-1, rooted in F1);
  - task 1: SOURCE-FACTOR RED (T1-1, rooted in F3).
- **Coverage, scopes and tools:**
  - The six extended policies are fully covered. `charter_scope` for task 0 is {late_fee, additional_premium_bill, renewal_down_payment, assisted_payment}, and for task 1 it is {installment_charge, term_payoff}. The two are pairwise disjoint, each spans its whole problem tree, and together they cover all six policies.
  - Task tools and GT are closed: the 6 tools are used by exactly one task each.
  - Each uuid8 is independent and unreused.
- **Trees:**
  - Task 0 has n = 3 with 3 value_input edges. Task 1 has n = 1 with 1 value_input edge.
  - Each root is an owner=user write, and there are no cycles.
  - The difficulty-wide graph is two disjoint depth-1 stars, so it is acyclic.
- **Factors:**
  - Every computation declares 4-6 factors, with at least 2 parameter and 1 method, ladders of 3 tiers stated in the rule, and a definite whole-baseline figure different from gold.
  - Each task has at least one multi-source factor and at least one cross-difficulty (auto) factor, and the auto rows are seeded.
  - Every factor bears weight.
  - The payoff prepaid-fee-share ladder fails the realism test (F3 / T1-1).
- **Gates:** the instantiation-stage gates were not re-run by this auditor. Per Step 0 the auditor only cites the conductor's snapshot. A closing re-run on a final form is moot while the difficulty has open REDs.

## revision_2

### charter_global_frozen (revision 2)

- Auditor: same erl-task-policy-audit subagent as revision 1. Freeze time: 2026-10-05T12:15Z, written before any revision-2 GT was revealed.
- Revision-1 text above is untouched. The three report files before this append hashed to:
  - `_difficulty.md` fbcec46f…899f
  - `0.md` 7b3b3795…b0ef
  - `1.md` 26dc2c4e…4c1d
- Inputs, as rebuilt views `/tmp/erl35_views/billing_and_nonpayment_cancellation.r2/`. The MANIFEST verified OK, and the in-place `billing.extended.yaml` and `task_tools.py` hash identically:
  - `billing.extended.yaml` 9f68cfa47760ab82b3beab5b9598fb0ade3958eee5c6c45f3e1db5f76e233687
  - `task_tools.py` 1ae7834c9c36f42cf8759399bbcbe022df65eec861dd89671e5f120e823e610b
  - `task_0.view.json` 60d6a201…640a
  - `task_1.view.json` c22e0685…7918
- Both charter hashes changed from revision 1 (d662720f…, e6e71eed…), so every charter-global section is re-derived in full below rather than carried forward.
- Gate snapshot `GATES.txt` (r2): EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK; CACHE-DIFF INFO; traceability deferred. Entry conditions are met.
- Method:
  - A line diff of r1 → r2 charter and tools, and a field diff of r1 → r2 views, located the reworked text.
  - Every changed policy was then re-read whole.
  - The base section (lines 1-1134) is still byte-identical to `blueprint/products/billing.yaml`.
- Masked until the freeze of all three revision-2 sections: revision-2 `tasks/*.json` and `worklog.md`.
- contamination_disclosure: the auditor saw revision-1 GT (round-1 reveal). Every quantity whose inputs did not change (the task-0 late fee 3.80 and AP bill 96.38) therefore coincides with a GT value already known. Those two were derived blind in revision 1 before that reveal, and are re-derived here on the r2 charter. All changed quantities are derived without any revision-2 GT.

### What changed (r1 → r2)

- **Charter:**
  - `billing_ext_late_fee_charge`:
    - KY late-fee amount $10.00 → $9.50.
    - The rule now ties the fee "to the installment whose grace days have just ended, which is the installment invoiced last in the current term (an earlier installment left unpaid drew its own late fee charge …)".
    - The baseline sentence is now "The standard late fee charge …".
  - `billing_ext_renewal_down_payment`: the expiring premium is now defined as "the full-term premium of the term the account currently bills as last rated: the full-term premium after the change on the latest additional-premium or return-premium transaction of the auto policy effective in that term, or, when that term had no such transaction, the term premium received for that term". This adds 5 compute bindings (XLATEST on auto_transactions). The increase-base factor becomes cross-difficulty auto.
  - `billing_ext_additional_premium_bill`: KY charge $2.00 → $2.50, and "ap_immediate_due_days" → "the pay plan's immediate-bill due days".
  - `billing_ext_assisted_payment`: new binding `as_fee_due` (0 on `notice_pending`/`cancelled_nonpay`) multiplied into `as_fee`, with basis "No fee is charged when the payment cures a notice of cancellation or reinstates the account."
  - `billing_ext_installment_charge`: KY charge $5.00 → $4.50, and "invoice_lead_days" → prose.
  - `billing_ext_term_payoff`, rewritten:
    - The prepaid-fee share is removed.
    - The payoff carries no installment fee ("installment fees attach only to installments as they are invoiced").
    - The standard payoff is the posted balance + premium still to be invoiced − a standard credit (1.0 % of one even installment share).
    - The credit-rate ladder is now 1.5 / 1.25 / 1.0 %.
    - A new `payoff_tenure_rate` factor (1.25 / 1.10 / 1.00) multiplies the credit.
- **Tools:** the return descriptions now say "the resulting balance" instead of "the balance after …". The bodies are unchanged.
- **Views:**
  - Task 0: the persona drops "including my renewal down payment" and "Your auto policy renews on October 20 and you want to get ahead of it". The renewal term premium is now 2148.70 (ledger `c6edfa21…`, auto `c7a7aaae…`), and the renewal offer `8e3fdcb9…` `full_term_premium_after` is 1358.96 (notice 2026-09-20).
  - Task 1: the persona closing is now "Once the payment goes through and you have the confirmation number…". KY-dependent history is reseeded (installment fees 2.25 / 4.00 / 1.69, late fee 5.94, and the matching payments and return).

### policy_conflict_scan (revision 2)

- The six extended policies, the task claims (task 0: late fee, renewal down payment, AP bill, assisted payment; task 1: installment charge, term payoff), the overlapping subjects and their disjoint scopes are unchanged from revision 1, and every conclusion there still holds.
- **Payoff vs installment charge.** The rewritten payoff now states that the payoff carries no installment fee and that the remaining installments are drawn from the credit. This no longer conflicts with `billing_ext_installment_charge` over the price of future installment fees, which closes the r1 F2/O4 wording. What remains is recorded as O4′ under findings.
- **Assisted payment vs base.** `as_fee_due` keys on account status and not on whether the payment cures or reinstates. See N2.
- **Cross-category reads:** still `auto` only. The renewal down payment additionally reads `auto_transactions.full_term_premium_after` through XLATEST.
- No conflict in the charter produces two values for one scored quantity.

### rule_compute_equivalence (revision 2)

- **Late fee.**
  - The new tie sentence is equivalent to `lf_installment_premium` (LATEST by due_date in the account term). The bracketed claim is true for every plan: the next invoice is issued (interval − lead days) after the due date, which is at least 10 days, later than the longest grace of 7.
  - The KY value $9.50 is consistent across params, rule, basis and ladder.
- **Renewal down payment.**
  - `dp_expiring_premium` implements the new definition: the latest-dated AP or RP transaction (by effective_date) whose effective date is on or after the account term's first day, else the term-premium entry.
  - Observation N3 (no consequence in either world): two edge cases are underspecified.
    - The compute's tie rule (AP wins on an equal date) is not stated in the rule.
    - The compute bounds "effective in that term" only from below, not by the term expiration date.
- **AP bill:** only the KY value changed, consistently across all faces.
- **Assisted payment.**
  - O1 is closed: the rule sentence now has a binding.
  - Observation N2: the binding zeroes the fee whenever the status is `notice_pending` or `cancelled_nonpay`. The rule says only "when the payment cures a notice of cancellation or reinstates the account". A whole-balance payment on a `notice_pending` account does cure, so these normally coincide. On a `cancelled_nonpay` account past its reinstatement window, a payment reinstates nothing, yet the compute gives no fee. Neither world is in that state.
- **Installment charge:** only the KY value and the lead-days wording changed, consistently.
- **Term payoff:** every new binding (`po_credit_rate` with `standard_rate`, `po_tenure_months`, `po_tenure_rate`, `po_credit`, `result`) has a verbatim basis. The sweep back finds no rule sentence without compute. The opening scope sentence and the "carries no installment fee" sentence are descriptive and require no binding.
- **Round-1 miss, recorded now (N4).** Unchanged since revision 1, some arithmetic glue bindings have no `compute_basis` key: `lf_installment_total`, `dp_rate_pct`, `iv_remaining`, `iv_unbilled`.
  - Each is the direct arithmetic of a rule phrase: "the installment's premium plus its installment fee"; "subtracted from / added to that percentage"; "installments of the term not yet invoiced"; "the premium of the term not yet invoiced".
  - Each is fully determined, and COMPUTE is green.
  - Observation only.
- **Factor tiers** on both faces remain one-to-one. Every `baseline.rule` sentence is in its `rule` (scripted check).

### action_binding_and_uuids (revision 2)

- The six `(target_tool, computes)` pairs, the uuid8s and the owners are unchanged, so the revision-1 conclusion stands.
- Docstrings: the return descriptions now read "the resulting balance". The only remaining "first" is "the renewal term's first day / the first day of the renewal term", which names a date, not a sequence position. O6 is closed.
- Bodies are unchanged and validate nothing.

### prerequisite_graph and prerequisite_sentences (revision 2)

- The edges E1-E4 are unchanged in problem, kind, gate, form and resolved_by, and all four `policy_source` strings are verbatim in their rules (scripted). The E4 `condition` now says "the plan's invoice lead days" instead of the token.
- The graph is acyclic, and no authoring-viewpoint phrasing was found. The four-point tests and single-reading derivations of revision 1 still hold word for word.
- No reworked sentence introduces a cross-problem order:
  - The new late-fee bracket ("an earlier installment left unpaid drew its own late fee charge on the first day after its own grace days") describes the late-fee policy's own earlier writes, not another problem.
  - The new expiring-premium definition reads auto history, which no task write changes.

### override_declarations (revision 2)

- The `overwrite` entries are unchanged in base sentence and replacement.
- The rewritten payoff keeps `overwrite: []`. Its new "the payoff itself carries no installment fee" agrees with base "The installment_fee is added to every installment after the down payment and to no other bill." Its "part above the balance stays on the account as a credit" agrees with base `overpayment_applied_to_next_installment`.
- The renewal down payment's new expiring definition touches no base sentence, because base has no increase base.
- No undeclared override.

### factor_ladders (revision 2)

- **Unchanged structure:** late fee 5 factors (4P, 1M); renewal down payment 6 (5P, 1M; increase base now also cross-difficulty auto); AP bill 4 (3P, 1M); assisted payment 5 (4P, 1M); installment charge 5 (4P, 1M).
- **Term payoff:** 4 factors (3P, 1M):
  - credit rate (P): 1.5 / 1.25 / 1.0 %, fall-through = standard 1.0 % = baseline;
  - credit base (M): whole / less one share / one share, fall-through = one share = baseline, cross-difficulty auto;
  - eligibility (P): 0 / ½ / 1, fall-through 1;
  - tenure rate (P): 1.25 / 1.10 / 1.00, fall-through 1, cross-difficulty auto.
- `payoff.baseline.rule` now states the standard credit, so each payoff factor's baseline is what `baseline.rule` states for that input. O5 is closed.
- **Per-task coverage:** the payoff no longer has a multi-source factor. Task 1's multi-source factor is the installment relief rate (last payment method AND auto inception), which still satisfies "at least 1 per task". Task 0 is unchanged.
- **Tier distinctness (O7):** with KY now $9.50 (late fee), $2.50 (AP charge) and $4.50 (installment charge), no state tier equals any plan's fall-through on any plan:

  | Ladder | Plan values | KY tier | VA/WV tier |
  |---|---|---|---|
  | Late fee | 15 / 10 / 10 / 15 / 15 / 10 | 9.50 | 12 |
  | Installment fee | 8 / 5 / 2 / 5 / 5 / 0 | AP 2.50, installment 4.50 | AP 4, installment 6 |
  | Phone fee | 5 / 0 / 0 / 5 / 5 / 5 | 2 | 3.50 |

  O7 is closed.
- **Realism:** the payoff's fee-share ladder (F3) is gone. The new tenure-boosted, NSF-reduced prepayment credit, rising with the installments outstanding, is a treatment a personal-auto carrier plausibly publishes (paid-in-full or prepayment incentives). F3 is closed as a factor-ladder defect. O8 is unchanged by design.

### findings (revision 2)

- **Round-1 items:**

  | Item | Status | Basis |
  |---|---|---|
  | F1 / T0-1 | Closed | The rule now defines the expiring premium uniquely and the compute implements it. Demonstrated per task in `0.md` revision_2. |
  | T0-2 | Closed | Persona text; see `0.md` revision_2. |
  | F3 / T1-1 | Closed | The fee-share ladder is removed and no unreal tier replaces it; see `1.md` revision_2. |
  | F2 / O4 | Wording closed, substance persists as O4′ below | "so that no further installment is left to pay" and the plan-fee pricing are gone. |
  | O1 | Closed | Residual imprecision is N2. |
  | O2, O3, O5, O6, O7, O9 | Closed | |
  | O8 | Unchanged, as declared by the reworker | Still observation. |

- **O4′ (observation, task 1; no scored value changes).** The payoff deducts a prepayment credit from the amount paid but posts no credit entry. `billing_ext_installment_charge` later invoices the remaining installments at the full "premium of the term not yet invoiced … divided evenly" plus their computed charges, so the credit is re-billed. Demonstration on task 1's world:
  - The payoff leaves a credit of 257.94.
  - Installments 5 and 6 will invoice 129.99 + 129.98 premium plus about 3.42 + 3.42 in charges, so about 8.87 remains owed after the payoff.
  - The customer will therefore still receive invoices with an amount due, against his stated motive "so I quit getting a bill every month".
  - The rule no longer asserts otherwise, and the persona no longer closes on "nothing more to pay", so neither the scored solution nor the persona's close is contradicted. Observation only.
  - This was present at a smaller magnitude in revision 1 (0.52) and is not a new class.
- **N2 (observation):** `as_fee_due` keys on status rather than on cure or reinstatement. See rule_compute_equivalence.
- **N3 (observation):** the expiring-premium tie rule and the term upper bound are unstated.
- **N4 (observation, revision-1 miss):** four arithmetic glue bindings have no compute_basis key.
- **New charter defect demonstrable against either world:** none. No regression in sections that were PASS in revision 1.

### closing_checklist (revision 2)

Written after both revision-2 reveals (2026-10-05T12:13Z). It sits below the revision-2 charter-global sections, which were frozen at 986fabed…c564 and not edited since.

- Per-task files `0.md` and `1.md` (each with `## revision_2`) and this file are one-to-one with tasks 0 and 1. Revision 1 is preserved verbatim above, and both revision-2 comparison sections carry PASS.
- The six extended policies are fully covered. The scopes (task 0: late fee, AP bill, renewal down payment, assisted payment; task 1: installment charge, term payoff, per the r2 `charter_scope`) are pairwise disjoint, and each spans its whole tree. Each of the 6 task tools is used by exactly one task, with its uuid8 unchanged, independent and unreused.
- **Trees:**
  - Task 0: n = 3 with 3 value_input edges.
  - Task 1: n = 1 with 1 value_input edge.
  - Each root is an owner=user write. The difficulty graph is acyclic (two disjoint depth-1 stars).
- **Factors:**
  - Every computation has 4-6 factors with at least 2 parameter and 1 method.
  - Each task has at least one multi-source factor (task 0: loyalty, record %, relief, assisted loyalty, purpose; task 1: installment relief) and cross-difficulty auto factors reading seeded rows.
  - Every ladder has 3 distinct tiers stated in its rule. On every plan, no two tiers of a ladder share a value.
  - Every factor bears weight against an honest baseline, and every whole baseline is definite and differs from gold.
- **Gates:** the conductor's re-run on the final form (`GATES.txt` r2) is all green with traceability deferred. Per Step 0 the auditor cites it and does not re-run it.
- **Open observations, not grounds for rework:** O4′, O8, N2, N3, N4, N5, plus the find_drivers / find_vehicles read-set notes.
- **Result:** the difficulty passes the source-layer audit at revision 2.
