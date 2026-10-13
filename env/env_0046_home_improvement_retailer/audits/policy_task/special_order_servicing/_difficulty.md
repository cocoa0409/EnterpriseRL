# Policy-task audit — special_order_servicing / charter-global

## charter_global_frozen

- Auditor: Claude (independent erl-task-policy-audit run; did not author these artifacts). Revision 1.
- Freeze time: 2026-10-08T07:51Z, written before any task's GT was revealed. Nothing in this section comes from a revealed GT.
- Frozen inputs:
  - `tasks/special_order_servicing/special.extended.yaml` sha256 `08564726cec445af3227949ea8d40525f4c0f03843f09b4357b92e3897ffcb74`
  - `tasks/special_order_servicing/task_tools.py` sha256 `2c1355c35317c1dbe6af50a77cba97b0dab7915a974cbd36a00a42dcf2f02893`
  - `blueprint/` (blueprint.yaml, db_schema.json, share_tools.py, products/special.yaml, plus the cross-read products pro/card/trade/install.yaml)
  - Masked views `/tmp/e46/views/special_order_servicing/task_0.blind.json` (sha256 `bcecc666…cecac`) and `task_1.blind.json` (sha256 `7a8b112d…a93c7`); both hashes re-verified locally and match the brief.
- Fields permitted: the charter (base + `extended_policies`), the tool contracts and bodies, the blueprint, and each task's `frozen_time`/`user_scenario`/`initial_state` (from the masked views).
- Fields masked until every task's derivation was frozen: all of `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`. `tasks/*.json` were not opened, and no recursive search had them in scope.
- Entry conditions (Step 0): the gate snapshot came with the brief. EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE all report OK. CACHE-DIFF is INFO only. TRACEABILITY NOT OK, which the coordinator says is expected before the KB is rendered (only the hidden tool names fail). Masked views and their hashes were supplied. The input is complete. Per the skill, I cite the gates and do not re-run them.
- Mechanical recomputation: I used my own scratch evaluator, `/tmp/aud_special_sos_lzuo/ev.py`. It imports `build_env`/`eval_compute`/`substitute` from `skills/erl-task-instantiate/scripts/check_compute.py` and reads only the masked views plus the charter.
- Hygiene note: a scratch directory I first used (`/tmp/e46audit/`) turned out to be shared with a concurrent auditor of another difficulty, whose script overwrote mine. All numbers below were recomputed in the private directory above. The only foreign content I saw was the other script's header lines (a file path). I read no sibling task or GT.

### policy_conflict_scan

The charter has six extended policies. They split into two families by `deposit_pct`. Every variant in the charter has `deposit_pct` 100 (Catalog, Cut-to-Order Flooring, Made-to-Measure Window Coverings) or 50 (Windows and Exterior Doors, Semi-Custom Cabinetry, Fabricated Countertops).

| policy | subject / quantity | scope gate | target_tool (owner) |
| --- | --- | --- | --- |
| special_ext_prepaid_delivery_charge | special_fee_charged / home_delivery_fee | deposit_pct 100, delivered | bill_prepaid_delivery_3669e7a4 (agent) |
| special_ext_prepaid_damage_allowance | special_credit_applied / damage_allowance | deposit_pct 100, covered cosmetic damage at handover, customer keeps item | accept_damage_allowance_e64dc664 (user) |
| special_ext_deposit_delivery_charge | special_fee_charged / home_delivery_fee | deposit_pct 50, delivered, not linked | bill_deposit_delivery_6add7fad (agent) |
| special_ext_deposit_damage_allowance | special_credit_applied / damage_allowance | deposit_pct 50, covered cosmetic damage, claim already records keep-with-allowance | post_damage_allowance_1c94fd89 (agent) |
| special_ext_storage_fee | special_fee_charged / storage_fee | deposit_pct 50, storage_fee_per_day_usd > 0, not linked, item has left the store | bill_storage_fee_4a2244a6 (agent) |
| special_ext_delay_credit | special_credit_applied / delay_credit | deposit_pct 50, special_msr_delay_days > vendor_delay_threshold_days, customer keeps order | accept_delay_credit_eaface8f (user) |

- **Overlapping subjects.** The two delivery-charge policies both write a `home_delivery_fee` line, and the two allowance policies both write a `damage_allowance` credit. Their scopes are disjoint (`deposit_pct` 100 vs 50, which partitions all six variants), so no order falls under two policies for the same quantity.
- **Overlap with base.** The base delay credit (special_vendor_delay) stays in force for deposit-100 programs. special_ext_delay_credit replaces it only for deposit-50 programs. The base storage fee is replaced only for deposit-50 programs. Deposit-100 programs all have `storage_fee_per_day_usd` 0.00, so nothing is left open.
- **Triggers and time anchors.** Every policy anchors its tiers on order fields (`promised_ready_date`, `ready_date`, `shipped_date`, `completed_date`, `production_started_date`), ledger rows, or the one clock `today` (= frozen date). No two policies anchor one quantity differently.
- **Terminal states.** None of the six writes changes `special_orders.status`. Each adds one ledger line and moves `balance_due`. The two allowance writes also close the damage claim (`status completed`). The accept_* user tools record the remedy choice. No policy's terminal state contradicts another's.
- **Cross-category reads.** These are pro (status, qualifying_spend_ytd, pro_activity, tier parameter order_delivery_discount_pct), trade (status, opened_date), card (status, opened_date, card_transactions) and install (status, job_address, cancelled_date, install_charges). All are read-only. Observation: pro.yaml `pro_tier_benefits` says "order_delivery_discount_pct to Ridgeline Orders & Delivery delivery fees", while special_ext_prepaid_delivery_charge also applies it to special-order delivery. The pro sentence enumerates benefits and does not say "only", and the special rule states the use outright. So no situation yields two answers. This is an observation only.
- **Scope exclusivity and completeness (from the masked user_scenarios and the charter only).**
  - Task 0's root is the prepaid damage allowance, and its tree is {prepaid_damage_allowance, prepaid_delivery_charge}.
  - Task 1's root is the delay credit, and its tree is {delay_credit, deposit_damage_allowance, deposit_delivery_charge, storage_fee}.
  - The two sets are disjoint, and together they cover all six extended policies.
  - The authors' `charter_scope` is compared after the reveal.

### rule_compute_equivalence

I swept each policy's `compute` binding by binding against its `compute_basis` quotation and back against the `rule`.

- **special_ext_prepaid_delivery_charge.** Equivalent in both directions. That covers base_charge (three branches incl. `int(...)` = "every full load_step_usd", small-order MN cap = "never more than home_delivery_fee_usd"), handover counts (functional OR wrong_item, then cosmetic), late_share, member_discount (the active×lines conjunction), site_share, no_charge (free threshold / linked), and the single product rounded once.
  - Observation: `inputs.history` lists the handover count without the condition filter. That is a declarative-ledger imprecision with no effect on compute.
- **special_ext_prepaid_damage_allowance.** Equivalent. delivered_price = billed + home_delivery_fee lines. The member, report, account, damage and wait ladders match the rule. core_amount = one product rounded. The lateness method (×1.5 rounded / +late_goodwill_usd / as is) matches.
- **special_ext_deposit_delivery_charge.** Equivalent. load_charge = `MX(fee, RND(pct))` / fee − light_discount / fee. Shares and the single rounding match.
- **special_ext_deposit_damage_allowance.** Equivalent: allowance_pct, custody, holding, plain_figure, settlement.
- **special_ext_storage_fee.** Not equivalent in one binding. Finding **G4** below: `quote_payments` sums installation payments across all of the customer's contracts, while the rule speaks of the contract at the delivery address. Everything else matches:
  - free hold = pickup_hold_days + late extension + receipt extension;
  - storage days with the "to today while still at the store" end point;
  - weekly conversion `int(d/7)*paid + d − int(d/7)*7`;
  - card count over channels special_order + installation within 12 months;
  - size share; cap; one rounding.
  - Observation: `inputs.history` lists the card count without the purchase_channel filter (declarative only).
- **special_ext_delay_credit.** Equivalent:
  - credit_base = billed + delivery fees − damage allowances;
  - late_by follows special_msr_delay_days (ready_date once ready, otherwise estimated);
  - the delay rate has a 1.5× middle threshold;
  - prompt bonus (0 before handover), allowance cut, installation bonus (cancelled after / on-or-before promised_ready_date), production bonus;
  - MN cap after rounding, then the own-wait method (halve rounded / −wait_deduction never below 0 / stands).
- **Interval convention (observation).** "in the last 12 months" is implemented as whole-month `MONTHS(date, today) < 12` (check_compute `_within`). The rule states no boundary convention. Neither task world has a row near the boundary: the closest are 12 months 16 days (task 0) and 13 months 25 days (task 1) back. This is an observation only.

### action_binding_and_uuids

- **(target_tool, computes) pairs.** These are (bill_prepaid_delivery_3669e7a4, delivery_charge), (accept_damage_allowance_e64dc664, allowance_amount), (bill_deposit_delivery_6add7fad, delivery_charge), (post_damage_allowance_1c94fd89, allowance_amount), (bill_storage_fee_4a2244a6, storage_fee) and (accept_delay_credit_eaface8f, credit_amount). Each pair is claimed by exactly one policy, so the check passes.
- **Function bodies.** None refuses, errors or hints on an unmet prerequisite or eligibility. Each one does `find` the order, `create` one ledger row, and `update` balance_due (and the request where applicable). No branch reads another fee/credit line. So the tool layer judges no prerequisite.
- **Docstrings.** None names another tool or a position in a sequence.
  - Observation: bill_deposit_delivery_6add7fad says "(one paid by deposit at order and balance before release)". The word "before" describes the program's payment terms, not the order of tool calls.
  - post_damage_allowance_1c94fd89's "whose customer has already chosen" names a record state (remedy_choice on the claim) that is the policy's own scope gate. It states no cross-tool order.
- **Owners.** Two tools are owner=user (accept_damage_allowance, accept_delay_credit) and four are owner=agent. This is consistent with the blueprint summary ("choosing between remedies are the customer's own steps").
- **uuid8s.** 3669e7a4, e64dc664, 6add7fad, 1c94fd89, 4a2244a6, eaface8f. They are pairwise distinct, with no shared prefix or suffix, no sequence and no adjacent values. Nothing shows batch derivation, so the check passes.

### prerequisite_graph

- `prerequisite` is filled in on all six policies. Four have `[]`. special_ext_prepaid_damage_allowance has 1 edge and special_ext_delay_credit has 3.
- Edges: prepaid_damage_allowance → prepaid_delivery_charge (value_input, gate `delivery_billed`); delay_credit → deposit_damage_allowance (value_input, `allowances`); delay_credit → deposit_delivery_charge (value_input, `delivery_fees`); delay_credit → storage_fee (state_gate, `special_order_events.fee_type`).
- Every `problem` is an extended id in this file, never a base policy or the policy itself. The graph is acyclic, with two disjoint stars.
- Each `policy_source` is a substring of its own policy's `rule` after whitespace normalisation (machine-checked).
- All edges are `form: state` with no `fallback_reason`, which is correct.
- Each value_input `gate` names a binding that exists in the blocked policy's compute (`delivery_billed`, `allowances`, `delivery_fees`). The state_gate uses a field path, which the reference schema permits.
- Each `resolved_by` equals the depended-on policy's `target_tool`, and the write genuinely creates the line the condition names. That was checked against the tool bodies: fee_type home_delivery_fee / credit_type damage_allowance / fee_type storage_fee.
- `condition` strength matches each sentence (see below).
- Observation: the `effect` of delay_credit → deposit_damage_allowance asserts "moving the allowance cut onto its upper tier". Whether the cut reaches the upper tier depends on the allowance's size relative to 20% of the billed total, so that sentence is world-specific, not general. The field is unpublished and changes no relationship, so this is an observation only.

### prerequisite_sentences

Four-point test, applied edge by edge:

1. **prepaid_damage_allowance:** "The allowance on a delivered order is fixed only after the home delivery charge owed for that delivery stands on the order as a fee line."
   - Connective: "only after".
   - Waited-on state: a home delivery fee line on the order. That is record-visible (`special_order_events` fee_type home_delivery_fee) and is stated without an actor or tool.
   - It names no tool, id or code token.
   - Its strength ("a delivered order", "the charge owed for that delivery") equals the condition.
   - Derivation: the records show a delivered deposit-100 order with no home delivery fee line. The reader looks for the policy whose own rule bills the home delivery charge on such an order. That is special_ext_prepaid_delivery_charge, whose scope is "a program whose deposit_pct is 100 ... delivered". The other policy that books the same kind of line (deposit delivery) is scoped to deposit_pct 50, and base special_delivery's charge clause is superseded. So exactly one reading remains.
   - Verdict: PASS.
2. **delay_credit (allowance edge):** "The delay credit is not worked out until every damage allowance owed for a damage claim registered on the order stands as a credit on it."
   - Connective: "not ... until".
   - Waited-on state: damage-allowance credit lines on the order, record-visible.
   - "Owed for a damage claim registered on the order" is a closed set named by kind. It matches the condition (claims whose remedy is keep-with-allowance).
   - Derivation: a deposit-50 order, a damage_claim with remedy_choice damage_allowance and no damage_allowance credit. The policy covering this is special_ext_deposit_damage_allowance (deposit_pct 50, choice already recorded). The prepaid allowance is scoped to deposit_pct 100.
   - Verdict: PASS.
3. **delay_credit (delivery edge):** "Before the delay credit is fixed, the home delivery charge owed for a delivered order must stand on the order as a fee line."
   - Connective: "Before".
   - State: a fee line.
   - Derivation: deposit-50 delivered and unlinked order → special_ext_deposit_delivery_charge.
   - Verdict: PASS.
4. **delay_credit (storage edge):** "A delay credit on an order the store has released is booked only after the storage charge owed for the days held past the free hold period stands on the order."
   - Connective: "only after".
   - State: a storage fee line.
   - Only one write of this difficulty books a storage_fee line (bill_storage_fee).
   - Its scope ("released order", "held past the free hold period") matches the condition.
   - Verdict: PASS.

General checks on the sentences:
- No rule carries a second wording, tool name or other problem's id for these dependencies. That was machine-checked: no rule contains any `target_tool` or extended policy id.
- No depended-on rule restates the blocked sentence.
- No extended rule states a cross-problem order that grounds no declared edge. "First ... then" in the two allowance rules and the delay-credit rule orders steps inside one computation. "once the item has left the store" in the storage rule names a lifecycle state, not another problem.
- Base rules that state cross-problem orders ground no edge, so they are observations only:
  - special_cancellation "recorded first as a special_requests record";
  - special_payments "the remaining balance is due before the item is released";
  - special_pickup_storage_abandonment "The item is released only when balance_due, including storage, is 0.00";
  - special_order_placement "production may start only after template_completed is true".
- Observation, state-form uniqueness: the home-delivery-fee state can be booked by two tools, and the damage-allowance state by two tools. In each case the depended-on rules' `deposit_pct` scopes leave one write per order, so the hop resolves uniquely. This is not a RED.

### override_declarations

I compared each extended policy, sentence by sentence, against its `base_policy_refs`. The criterion is the scored quantity.

**special_ext_prepaid_delivery_charge and special_ext_deposit_delivery_charge**
Base refs: special_agg_install_link, special_cancellation, special_pickup_storage_abandonment, special_delivery, special_returns.
- **special_delivery s1** ("offered only where home_delivery_available is true" + "its charge is home_delivery_fee_usd, free when ... billed as fee_type home_delivery_fee before release").
  - The charge clause, including "before release", is declared in `overwrite`, and the replacement is unique.
  - The availability gate is inherited. Flooring and Cabinetry have it set to true.
  - The prepaid rule restates the free-threshold and linked-order zeroing outside the replaced clause, and compute applies them first, so the merged reading is unique.
  - The deposit rule drops the free-threshold branch. Every deposit-50 variant has `free_delivery_threshold_usd` 0.00, so that branch never fires: a dropped branch with no reachable case. Observation only.
- special_delivery s2 (reschedule) and s3 (failed delivery) govern other fee types. Followed.
- **special_agg_install_link s4** ("Home delivery charges are not billed on an order linked to an installation contract"). Followed: the prepaid policy has `no_charge`, and the deposit policy has the scope exclusion plus `result` 0 if linked.
- special_pickup_storage_abandonment ("released only when balance_due, including storage, is 0.00"): governs release, not the delivery quantity. Inherited. See observation G13.
- special_cancellation and special_returns: no overlap with the delivery quantity. Followed.
- The 0/1 multiplier `functional_share` 0 / `bad_handover_share` 0 zeroes the charge. It sits inside the declared replacement of the charge clause, so it is declared.

**special_ext_prepaid_damage_allowance and special_ext_deposit_damage_allowance**
Base refs: special_cancellation, special_vendor_delay, special_receipt_and_damage, special_returns, special_price_protection.
- **special_receipt_and_damage s4.** "keeping the item with an allowance of damage_allowance_pct percent of the order total as credit_type damage_allowance" is declared in `overwrite` on both policies.
  - The prepaid baseline uses the delivered price (billed + delivery fees) instead of the order total. That falls inside the declared clause.
  - The base gate "for cosmetic damage only and where damage_allowance_pct is above 0" sits outside the replaced clause, so it is inherited. Window Coverings and Countertops (pct 0) therefore get no allowance under either extended policy. That is consistent, not a conflict.
- receipt_and_damage s2/s3 (damage_report_hours window, full-hour counting) and s5 (late or post-handover damage not covered): inherited, and both task worlds satisfy them (see task files).
- **special_vendor_delay.** The lateness uplift inside the allowance (×1.5 / +late_goodwill_usd / +lateness_goodwill_usd) is part of the allowance quantity, not one of the two named delay remedies. "one delay remedy, never both" is not contradicted. Observation: this is a stacked lateness compensation, but it is not an override.
- special_cancellation, special_returns, special_price_protection: no shared quantity. Followed.

**special_ext_storage_fee**
Base refs: as for delivery.
- **special_pickup_storage_abandonment s1** (hold, per-day charge for special_msr_storage_days, cap, "billed when the item leaves the store") is declared.
- s2 (linked items stored free): followed through the scope exclusion and `result` 0 if linked.
- s3 (release only at zero balance) and s4 (abandonment) are inherited. Neither task's order is abandoned.
- The base measure special_msr_storage_days ("from the day after ready_date plus pickup_hold_days to ... pickup") counts the same as the baseline sentence (DAYS(ready, completed) − pickup_hold_days). So the baseline and the base agree.

**special_ext_delay_credit**
Base refs: special_cancellation, special_vendor_delay, special_receipt_and_damage, special_returns, special_price_protection.
- **special_vendor_delay s3** ("receive a delay credit of delay_credit_pct percent of the order total, capped at delay_credit_max_usd, posted once as credit_type delay_credit") is declared. The extended rule re-asserts "posted once as credit_type delay_credit".
- vendor_delay s1 (threshold), s4 (no later fee-free cancel; no remedy for a customer-caused delay) and s5 (shipped orders earn only the credit) are inherited.
- Observation: the replacement wording "rather than as delay_credit_pct percent of the order total" names the base quantity, while the extended baseline itself is "delay_credit_pct percent of the credit base". The merged meaning is still unique: the rules below decide, and the baseline is the extended standard.

No undeclared override was found. No anonymous intermediate factor, undeclared 0/1 multiplier or dropped branch with a reachable case was found. No author note calls base output wrong.

### factor_ladders

This section covers structure only. Weight is assessed per task. "Multi-source" means each non-fall-through tier is a conjunction or disjunction over distinct records.

**special_ext_prepaid_delivery_charge** — 5 factors (1 method, 4 parameter).
- order_size_basis: method, 3 tiers. The algorithm changes (fee + per-step surcharge / % of total capped at fee / flat fee). Honest. Single-source.
- handover_condition_share: parameter, values 0 / 0.5 / 1. Single table (handover rows).
- vendor_lateness_share: parameter, values 0.6 / 0.8 / 1. Date.
- probuild_delivery_discount: parameter, values = tier `order_delivery_discount_pct` / 10 / 0. Multi-source (membership status × pro_activity rows). Labelled cross_difficulty `pro`. **Finding G1.**
- job_site_share: parameter, values 0.75 / 0.9 / 1. Install, a real difficulty.
- Every tier is stated in the rule and implemented in compute. Fall-throughs equal the baseline.

**special_ext_prepaid_damage_allowance** — 6 factors (1 method, 5 parameter).
- probuild_member_rate: values 13 / 11.5 / damage_allowance_pct. Fall-throughs are 10 / 10 / 0 by program, so the values are distinct. Single record (membership status + qualifying_spend_ytd). `pro`.
- report_day_bonus: 1.5 / 0.75 / 0.
- credit_account_bonus: 1 / 0.5 / 0. Trade, a real difficulty.
- delivery_damage_multiplier: 1.2 / 1.1 / 1. Multi-source (fulfillment_method on the order × store-receipt rows). Deposit-100 programs have receipt_inspection_required false, so the "no receipt on record" tier is live.
- store_wait_multiplier: 1.05/1.1 tiers, then 1.
- vendor_lateness_adjustment: method (×1.5 rounded / +flat / as is). Honest.

**special_ext_deposit_delivery_charge** — 4 factors (1 method, 3 parameter).
- load_value_basis: method (max(fee, %) / fee − discount / flat). Honest.
- late_arrival_share: 0.5 / 0.75 / 1.
- handover_condition_share: 0 / 0.75 / 1.
- cardholder_tenure_share: 0.85 / 0.9 / 1. Card, a real difficulty. Single record.

**special_ext_deposit_damage_allowance** — 4 factors (1 method, 3 parameter).
- measure_and_install_rate: values 10 / 16 / damage_allowance_pct (15, 15, 0). Distinct. Install. Declared multi-source (measured_by × install status). **Finding G2.**
- custody_multiplier: 1.1 / 0.9 / 1. Declared multi-source (store-receipt good × fulfillment_method). **Finding G3.**
- holding_multiplier: 1.1 / 1.05 / 1.
- lateness_settlement: method. Honest.

**special_ext_storage_fee** — 6 factors (1 method, 5 parameter).
- late_arrival_hold: 14 / 7 / 0 days.
- receipt_delay_hold: 4 / 2 / 0 days.
- weekly_day_count: method (5-of-7 / 6-of-7 / every day). Honest.
- cardholder_project_share: 0.75 / 0.9 / 1. Multi-source (card status × card_transactions). Card.
- order_size_share: 0.85 / 0.95 / 1.
- quoted_installation_share: 0.8 / 0.9 / 1. Multi-source (install status × install_charges). Install. Rule/compute mismatch, **G4**.

**special_ext_delay_credit** — 6 factors (1 method, 5 parameter).
- delay_length_rate: 7.5 / 6 / delay_credit_pct (5).
- prompt_claim_bonus: 1 / 0.5 / 0.
- allowance_cut_rate: 1 / 0.5 / 0.
- lost_installation_bonus: 1.5 / 0.5 / 0. Install. Single record (status + cancelled_date).
- production_length_bonus: 1 / 0.5 / 0.
- own_wait_settlement: method (halve / −flat / stands). Honest.

**Common checks.** Every ladder has 3 pairwise-disjoint tiers, each stated in its rule's prose and implemented in `decides`. No tier lives only in compute. Each `decides` is an input, never `result`. Bindings are disjoint between the factors of one policy. Every baseline matches its `baseline.rule`, and every `baseline.rule` sentence appears verbatim in its rule with the `params` it names.

**Counts per task.** (The root/tree assignment is derived from the masked scenarios.)
- Task 0's computations carry 2 multi-source factors (probuild_delivery_discount, delivery_damage_multiplier). They carry 2 factors reading a real other difficulty (job_site_share → install, credit_account_bonus → trade) plus 2 labelled `pro`.
- Task 1's computations carry multi-source factors cardholder_project_share and quoted_installation_share. The two deposit-allowance factors declared multi-source collapse (G2, G3). Cross-difficulty factors: card (×2) and install (×3).

**Realism observations (no RED).**
- quoted_installation_share discounts storage for a customer whose quoted installation was cancelled.
- lost_installation_bonus pays a delay-credit bonus (0.5) even when the installation was cancelled before the promised date, for reasons unrelated to the delay.
- I cannot show that no business in this line would publish either rule, so both are recorded only.

### findings

- **G1 — SOURCE-FACTOR RED (unreal ladder; two tiers select the same value). Bears on task 0.**
  - Symptom: in special_ext_prepaid_delivery_charge / probuild_delivery_discount, the top tier's value is "the membership tier's order_delivery_discount_pct" (`CPARAM('pro','order_delivery_discount_pct')`).
  - Root cause: pro.yaml gives ProBuild Member `order_delivery_discount_pct: 0` (line 123) and ProBuild Bronze `0` (line 175).
  - Evidence: rule sentence "an active membership with at least busy_lines spend lines posted from special orders in the last 12 months gives the membership tier's order_delivery_discount_pct; an active membership with fewer than busy_lines such lines gives light_member_pct; otherwise the member delivery discount is 0 percent".
  - Demonstrated consequence: for an active Member or Bronze with 3 or more special-order lines, tier 1 selects 0, the same value as the fall-through. Such a member's busier history earns *less* discount (0%) than a light member's 10%. That is an inverted treatment no retailer would publish.
  - Affected: extended.yaml `special_ext_prepaid_delivery_charge.rule` (member discount sentence), `compute.member_discount`, `factors[probuild_delivery_discount]`.
  - Task 0's own customer is Gold (50%), so its scored number is not moved. The ladder defect is structural (see 0.md).
- **G2 — SOURCE-FACTOR RED (a compound-condition part holds of every customer reaching the write). Bears on task 1.**
  - Symptom: special_ext_deposit_damage_allowance / measure_and_install_rate conditions both non-fall-through tiers on "an item measured by a Ridgeline installer".
  - Root cause: the policy covers only deposit_pct-50 programs. Windows and Exterior Doors, Semi-Custom Cabinetry and Fabricated Countertops all have `pro_measure_required: true` (extended.yaml lines 263, 315, 367). Base special_agg_install_link says "Where pro_measure_required is true, the order may be placed only when ...; such an order records measured_by ridgeline_installer."
  - Demonstrated consequence: the conjunct `F('measured_by') == 'ridgeline_installer'` is true for every order that reaches this write. It restates scope rather than dividing customers. The declared two-record conjunction is in effect a single-source ladder on install status.
  - Affected: rule sentence "The allowance percentage depends on who measured the item and on the customer's Ridgeline installation contract at the delivery address: ...", `compute.allowance_pct`, `factors[measure_and_install_rate]`.
- **G3 — SOURCE-FACTOR RED (same shape as G2). Bears on task 1.**
  - Symptom: special_ext_deposit_damage_allowance / custody_multiplier conditions both non-fall-through tiers on "after a store receipt inspection recorded good".
  - Root cause: all three deposit-50 programs have `receipt_inspection_required: true` (lines 268, 320, 372). Base special_receipt_and_damage s1 says "Where receipt_inspection_required is true the store inspects the item ... and makes it ready only when the condition is good". The policy's scope requires covered damage reported at the customer handover, i.e. an order that was made ready and handed over.
  - Demonstrated consequence: `receipt_good_lines > 0` holds for every order reaching this write. The ladder in effect reads fulfillment_method alone (home_delivery / store_pickup / installer_job_site).
  - Affected: rule sentence "The custody multiplier depends on how the item reached the customer after a store receipt inspection recorded good: ...", `compute.custody_mult`, `factors[custody_multiplier]`.
- **G4 — SOURCE-POLICY RED, charter-global (rule/compute not equivalent). Bears on task 1 structurally.**
  - Symptom: the storage rule says "The quoted-installation share depends on the customer's Ridgeline installation contract at the delivery address: a cancelled contract on which the customer made payments gives quoted_paid_share; a cancelled contract with no payments gives quoted_unpaid_share". Compute instead has `quote_payments: "XSUM('install', 'install_charges', 'amount', event_type='install_payment_received')"`, which is not restricted to that contract. The factor ladder text ("the customer made payments on installation contracts") follows compute, not the rule.
  - Demonstrated consequence, on a constructed situation: take a customer with a cancelled Window and Door Installation contract at the delivery address (measure_fee_usd 0.00, so no payment rows) and paid rows on a different contract. The rule gives quoted_unpaid_share 0.9 and compute gives quoted_paid_share 0.8.
  - On task 1's world the two agree: there is one contract, with one 99.00 payment. No scored value moves there (see 1.md).
  - Affected: `special_ext_storage_fee.compute.quote_payments` vs its rule sentence and `compute_basis.quote_payments`.
- **G11 — candidate two-readings in a tool argument, charter-global half. Demonstrated per task (task 1).**
  - bill_storage_fee_4a2244a6 takes `storage_days` ("the number of storage days billed on the line"), and the event field is "storage_days: Days of storage billed".
  - No compute binding produces this argument (`computes: storage_fee` only).
  - The storage rule defines two distinct quantities: "The storage days are the calendar days from ready_date to completed_date ... less the free hold" and "The storage days are converted into billable days by the length of the stay".
  - Wherever the weekly conversion applies, "storage days billed" admits both values. Whether this is a RED depends on whether the argument is scored, which is settled per task after the reveal.
- **Observations (no RED):**
  - G5: probuild factors are labelled `cross_difficulty: pro`, but ProBuild Rewards is no difficulty's claimed category in blueprint.yaml. Each task has other genuine cross-difficulty factors.
  - G6: inputs.history declarations omit filters that compute applies.
  - G7: the "last 12 months" boundary convention is unstated.
  - G8: the bill_deposit_delivery docstring contains "before release".
  - G9: one edge `effect` is world-specific.
  - G10: base rules state cross-problem orders that ground no edge.
  - G12: two tools can book the home-delivery-fee and damage-allowance states. Resolved by the deposit_pct scopes.
  - G13: both seeds hold released orders without a delivery or storage line. That contradicts base "The item is released only when balance_due, including storage, is 0.00", but the inconsistency is exactly what makes the charges "owed" and does not change the derivation.
  - G14: realism notes on quoted_installation_share and lost_installation_bonus (see factor_ladders).

## closing_checklist

Written after both reveals. Nothing above this heading was changed after the reveals. One disclosure: the freeze time in § charter_global_frozen ("07:51Z") is an estimate. The file's real mtime is 07:53:25Z, which is still before any reveal at ≥07:56:34Z.

**The difficulty is NOT closed.** Step 4 closes a difficulty only when all four relationships PASS for every task. Here:
- task 0: SOURCE-FACTOR RED (G1, T0-2);
- task 1: SOURCE-POLICY RED (G4) + SOURCE-FACTOR RED (G2, G3).

Checklist status for the record:
- **Audit files.** `_difficulty.md`, `0.md` and `1.md` correspond one-to-one with tasks 0 and 1. This is revision 1, with no older revisions.
- **Coverage.** The six extended policies are fully covered. Task scopes are pairwise disjoint (charter_scope: task 0 has the two prepaid policies; task 1 has the four deposit policies), which matches the pre-reveal scan. Task tools and GT are closed, and the uuid8s are independent.
- **Trees.**
  - Task 0: n=1, 1 value_input edge, user write = accept_damage_allowance.
  - Task 1: n=3, 2 value_input edges plus 1 state_gate, user write = accept_delay_credit.
  - Both are acyclic, and the difficulty-wide graph is a DAG.
- **Factors.**
  - Counts and weight: all pass on both worlds, and every baseline gives a definite non-gold number.
  - Ladder reality: G1 fails, and G2/G3 have vacuous conjuncts.
  - Rule/compute equivalence: G4.
  - Stamp: T0-2.
- **Gates.** The instantiation-stage gates were not re-run on a final form, because no final form exists yet. The gate snapshot in the brief (all OK except the expected TRACEABILITY pending the KB) is the last state on record.

## revision_2

### charter_global_frozen (revision 2)

- **Auditor:** Claude, independent re-audit, round 2.
- **Written:** 2026-10-08, about 12:13–12:16Z, before either round-2 task file was opened. Nothing in this section comes from a revealed round-2 GT.
- **Frozen inputs:**
  - `special.extended.yaml` sha256 `3d76be7c4891aefa55095ddb679e1d3092d6f4ec130d57c3512353d56fc67027` (round 1: `08564726…`)
  - `task_tools.py` sha256 `e8618e25dc2967040f1764d7b2c380ff07cce6e69af2aecfeaa116780513ed5f` (round 1: `2c1355c3…`)
  - Masked views `r2/task_0.blind.json` `03565376…7c27f` (changed) and `r2/task_1.blind.json` `7a8b112d…a93c7` (unchanged). I re-verified both hashes locally.
- **Re-derivation basis:** both shared hashes changed, so every charter-global section below was re-derived in full. None is carried forward by reference.
- **Old text not available:** the round-1 extended.yaml is no longer on disk (searched by file name only). I compared the new file sentence by sentence against the round-1 quotations in the sections above.
- **Entry conditions:**
  - The gate snapshot came with the brief: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE are all OK.
  - CACHE-DIFF is INFO only.
  - TRACEABILITY is NOT OK, expected while the KB is not yet rendered.
  - Masked views and hashes were supplied, so the input is complete.
- **Scratch directory:** private `/tmp/aud_sos_r2_on9oRo/` (not `/tmp/e46audit`).
- **Masking:** unchanged from round 1. No `tasks/*.json` was opened, and no recursive search had them in scope.

### what changed (charter and tools)

- **Base section:** still verbatim identical to `blueprint/products/special.yaml` (machine check: every top-level key is equal).
- **special_ext_prepaid_delivery_charge:**
  - New param `busy_member_pct: 50`.
  - The member-discount sentence now reads "... at least busy_lines spend lines ... gives busy_member_pct; ... fewer ... gives light_member_pct; otherwise ... 0 percent".
  - `compute.member_discount` uses `K('busy_member_pct')`.
  - The `order_delivery_discount_pct` read was dropped from `cross_category.reads`.
  - `probuild_delivery_discount.cross_difficulty` is now null.
  - `inputs.history` handover count now carries a `damaged_cosmetic` filter.
- **special_ext_prepaid_damage_allowance:** only `probuild_member_rate.cross_difficulty` changed (`pro` to null). Rule, compute and params are textually unchanged.
- **special_ext_deposit_delivery_charge:** unchanged.
- **special_ext_deposit_damage_allowance:**
  - The allowance-percentage sentence now conditions on installation-contract status alone ("a contract there that is scheduled or in_progress ... gives onsite_rate; a contract there that is cancelled ... gives self_install_rate; otherwise ... damage_allowance_pct"). Factor renamed `installation_status_rate`.
  - The custody multiplier (truck_mult / pickup_mult) was removed. It is replaced by a report multiplier: "a claim registered on completed_date itself ... gives same_day_report_mult; a claim registered on the next calendar day gives next_day_report_mult; otherwise the report multiplier is 1". The new params are same_day_report_mult 1.1 and next_day_report_mult 1.05. The compute adds bindings `claim_registered`, `report_gap` and `report_mult`.
  - The product sentence now names the report multiplier.
- **special_ext_storage_fee:**
  - New binding `quote_contract: CFIELD('install','install_contract_id', job_address=F('delivery_address'))`.
  - `quote_payments` is now an XSUM filtered by `install_contract_id=quote_contract`.
  - The factor ladder text now reads "on that contract".
  - The rule's last sentence adds "The storage fee line records the billable days as its days of storage billed." (also quoted in `compute_basis.result`).
  - `inputs.history` card count is split by channel.
- **special_ext_delay_credit:** only the allowance-edge `effect` changed ("moves the allowance cut off its zero tier").
- **task_tools.py:**
  - Only the bill_deposit_delivery docstring changed ("one paid by a deposit at order with the balance due at release").
  - AST check: no tool body contains an `if` statement or `raise`. Owners and decorators are as in round 1. The bodies are as read in round 1.

### policy_conflict_scan (revision 2)

- Six policies, the same two `deposit_pct` families, and the same targets and owners, so scopes stay disjoint.
- No subject, trigger, time anchor, terminal state or cross-category read boundary conflicts with another.
- The pro.yaml applicability observation from round 1 (order_delivery_discount_pct outside Orders & Delivery) **no longer applies**: the special charter no longer reads that parameter.
- Scope exclusivity from the masked scenarios is unchanged. Task 0 covers {prepaid_damage_allowance, prepaid_delivery_charge}. Task 1 covers {delay_credit, deposit_damage_allowance, deposit_delivery_charge, storage_fee}. They are disjoint and jointly complete.

### rule_compute_equivalence (revision 2)

- **Unchanged policies:** re-swept and still equivalent (prepaid allowance, deposit delivery, delay credit).
- **special_ext_prepaid_delivery_charge:** `member_discount` matches the new sentence. The other bindings are unchanged and equivalent.
- **special_ext_deposit_damage_allowance:** all bindings are equivalent.
  - `allowance_pct` is the three-tier status ladder.
  - `report_gap = DAYS(F('completed_date'), LATEST(damage_claim created_at))` matches "in calendar days from completed_date".
  - `report_mult`, `holding_mult`, `plain_figure` ("by the report multiplier and by the holding multiplier in one product"), `settled_figure` and `result` all match.
- **special_ext_storage_fee:** **G4 is closed.** `quote_payments` now sums only the payments on the contract at the delivery address, matching "a cancelled contract on which the customer made payments".
  - I re-ran the round-1 constructed situation (a cancelled contract at the address with no payments, plus a paid contract elsewhere) in `/tmp/aud_sos_r2_on9oRo/g4.py`: compute now gives quote_payments 0.00 and install_share 0.9, the same as the rule.
  - Observation: when several contracts share the delivery address, `CFIELD` takes the first. The rule says "the ... contract at the delivery address", and neither world has two, so this is an observation as in round 1.
- **Observation G6, partly acted on:**
  - The prepaid-delivery `inputs.history` handover row now filters `damaged_cosmetic` only, while compute also counts damaged_functional and wrong_item.
  - The storage `install_charges` input lists no contract filter.
  - Both are declarative ledgers with no effect on compute.
- **Observation G7 kept:** the "last 12 months" boundary convention is unstated.

### action_binding_and_uuids (revision 2)

- The six `(target_tool, computes)` pairs are unchanged and each is claimed once.
- The uuid8s are unchanged and independent.
- **G8 is closed:** no docstring now contains before / after / first / then / until / prior. The only remaining match is "already chosen", a record state (see round 1).
- No tool judges a prerequisite (AST: no `if`/`raise` in any body).

### prerequisite_graph (revision 2)

- Edges, kinds, gates, forms and resolved_by are unchanged.
- Each policy_source is a verbatim substring of its own rule (machine check, all True).
- The graph is acyclic.
- Each value_input gate exists in compute.
- **G9 is closed:** the delay-credit allowance edge `effect` now reads "moves the allowance cut off its zero tier", which holds for every booked allowance above 0.00.

### prerequisite_sentences (revision 2)

- All four sentences are verbatim as in round 1, and all four pass for the same reasons.
- No changed rule adds a cross-problem order.
  - The new deposit-allowance clauses ("so a Ridgeline installer will handle the item on site", "while the delivery or pickup is still fresh") are explanatory and order nothing.
  - The new storage sentence ("The storage fee line records the billable days as its days of storage billed") defines a field value and orders nothing.
- No rule names a tool or policy id (machine check).
- Observations G10 and G12 are kept as in round 1.

### override_declarations (revision 2)

- All overwrite blocks are unchanged.
- The changed text sits entirely inside the already-declared replacements:
  - the member discount, inside prepaid delivery's replacement of the special_delivery charge clause;
  - the report multiplier, inside the deposit allowance's replacement of the receipt_and_damage allowance clause;
  - quote_payments and the storage_days sentence, inside storage's replacement of the pickup_storage first sentence.
- No undeclared override was found.
- The inherited base gate "where damage_allowance_pct is above 0" still applies.

### factor_ladders (revision 2)

**special_ext_prepaid_delivery_charge** — 5 factors (1 method, 4 parameter).
- **G1 is closed.** probuild_delivery_discount's values are busy_member_pct 50, light_member_pct 10 and 0. They are pairwise distinct for every member. The busier tier earns more, which is a treatment a retailer would publish.
- The factor is multi-source: membership status × pro_activity rows.
- `cross_difficulty` is null (G5 acted on). The factor still reads pro, which is no difficulty's claimed category.

**special_ext_prepaid_damage_allowance** — 6 factors (1 method, 5 parameter).
- Structure is unchanged.
- probuild_member_rate is now `cross_difficulty: null`.
- credit_account_bonus reads trade.
- delivery_damage_multiplier is multi-source.

**special_ext_deposit_delivery_charge** — 4 factors (1 method, 3 parameter). Unchanged.

**special_ext_deposit_damage_allowance** — 4 factors (1 method, 3 parameter).
- **installation_status_rate** (parameter, install):
  - Values onsite_rate 10, self_install_rate 16, and damage_allowance_pct as the fall-through (15 / 15 / 0 across the three deposit programs). These are distinct.
  - Its only condition is the contract status at the delivery address. That condition divides deposit-50 customers: placement required a measured, contracted or scheduled contract, which can later be scheduled, in_progress, cancelled, completed and so on. So the fall-through is reachable.
  - **G2 is closed:** the vacuous `measured_by` conjunct is gone.
- **report_timing_multiplier** (parameter): values 1.1 / 1.05 / 1, distinct.
  - Claims are covered within 48 or 72 h of 00:00 of completed_date, so a gap of 0, 1 or 2+ days is reachable.
  - Not vacuous. Single-source (claim created_at against the order's completed_date).
- holding_multiplier and lateness_settlement are unchanged.
- **G3 is closed:** the custody multiplier, whose `receipt good` conjunct was vacuous, has been removed.
- This computation has no multi-source factor. The task-level count (task 1) is met through storage.

**special_ext_storage_fee** — 6 factors (1 method, 5 parameter).
- quoted_installation_share now binds [quote_status, quote_contract, quote_payments, install_share].
- It is multi-source (contract status × that contract's install_charges payments). The Window and Door program has a free measure, so a cancelled contract with no payment is reachable, and the tier is not vacuous.
- The other factors are unchanged.

**special_ext_delay_credit** — 6 factors (1 method, 5 parameter). Unchanged.

**Common checks.** Every ladder has 3 disjoint tiers, each stated in the rule and implemented in its `decides` binding. Every fall-through equals its baseline. Bindings stay disjoint within each policy. Every `baseline.rule` is verbatim in its rule.

**Realism observation G14 kept:** quoted_installation_share and lost_installation_bonus.

### findings (revision 2, charter-global)

**Closure of round-1 REDs.** Each was verified against the new text, not taken from the reworker's claim.

| item | round 1 | round 2 | evidence |
| --- | --- | --- | --- |
| G1 | SOURCE-FACTOR RED | **closed** | Ladder values 50 / 10 / 0 are fixed params, distinct and monotone. No tier-parameter lookup remains. |
| G2 | SOURCE-FACTOR RED | **closed** | measured_by conjunct removed. The allowance percentage now reads install status alone, and every tier is reachable. |
| G3 | SOURCE-FACTOR RED | **closed** | Custody factor removed. The replacement report multiplier has no vacuous condition. |
| G4 | SOURCE-POLICY RED | **closed** | quote_payments is filtered to the delivery-address contract. The constructed world now gives 0.9 under both the rule and compute. |
| G11 | candidate (observation) | **closed** | The storage rule now says the line records the billable days. |

**Observations acted on:**
- G5: `pro` no longer labelled as cross-difficulty.
- G6: partly acted on. Declaration rows still omit some filters.
- G8: docstring has no ordering word.
- G9: effect is general.

**Observations kept as in round 1:** G7, G10, G12, G13, G14.

**New charter-global defects:** none found. Regressions: none (unchanged policies re-swept).

### closing_checklist (revision 2)

Written after both round-2 reveals at 12:17:40Z. Nothing above this heading in revision 2 was changed after the reveals. The approximate "written" time in § charter_global_frozen (revision 2) was corrected before the reveal; the real mtime then was 12:16:10Z.

**Closure status.** Both tasks PASS on all four relationships, so this difficulty passes the source-layer audit and is closed.

- **Audit files.** `_difficulty.md`, `0.md` and `1.md` correspond one-to-one with the tasks. Each carries its revision 1 text untouched and an appended `revision_2`. Both comparison sections carry PASS.
- **Coverage and scopes.**
  - All six extended policies are covered.
  - Scopes are pairwise disjoint: task 0 has the two prepaid policies, and task 1 has the four deposit-program policies (charter_scope matches my pre-reveal scan).
  - Task tools and GT are closed.
  - The uuid8s are independent and frozen.
- **Problem trees.** Every tree has 1 to 3 prerequisite problems, at least max(n − 1, 1) value_input edges, and an owner=user write. The difficulty graph is a DAG.
  - Task 0: n = 1, 1 value_input edge, user write accept_damage_allowance.
  - Task 1: n = 3, 2 value_input edges plus 1 state_gate, user write accept_delay_credit.
- **Factors.** Every computation has a self-sufficient baseline with a definite number that differs from gold:
  - task 0: 79.00 and 330.05;
  - task 1: 149.00, 729.00, 180.00 and 196.27.

  Every computation has 4 to 6 factors, with ≥ 2 parameter and ≥ 1 method. Each ladder has 3 tiers stated in its rule, with distinct outcomes and no vacuous condition. Every factor bears weight on its own world.

  Per task, the multi-source and cross-difficulty minimums hold:
  - task 0: multi-source probuild_delivery_discount and delivery_damage_multiplier; cross-difficulty install and trade;
  - task 1: multi-source cardholder_project_share and quoted_installation_share; cross-difficulty card and install.
- **Gates.** The coordinator's snapshot on the final form (round-2 hashes) is EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE all OK. CACHE-DIFF is INFO. TRACEABILITY is NOT OK only because the KB is pending render; it is re-judged after the KB step and is not a source-layer relationship.
- **Observations still on record (not grounds for rework):**
  - G6 (partial): inputs.history declarations.
  - G7: the 12-month boundary convention.
  - G10: base cross-problem sentences.
  - G12: two tools per waited-on state, resolved by scope.
  - G13: orders released before their fees were billed.
  - G14: realism of quoted_installation_share and lost_installation_bonus.
  - Task 0: the 2025 spend behind the held Gold tier is not seeded, and P1's near-misses do not flip a tier.
  - Task 1: the persona's storage cue.
