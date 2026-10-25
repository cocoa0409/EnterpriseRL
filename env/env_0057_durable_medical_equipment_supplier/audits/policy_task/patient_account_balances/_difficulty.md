# Policy-task audit — patient_account_balances / charter-global

## charter_global_frozen

- Frozen: 2026-10-12T19:08Z, before any task's GT was revealed. Auditor: independent erl-task-policy-audit agent (did not author the artifacts; an earlier auditor on this unit was cut off before writing anything, and nothing of theirs was read).
- `coverage.extended.yaml` sha256 `0b0f020c3ee67f50c2a341ce11278757f982ae75c4d97bc7462f8cbff42cc01e`; `task_tools.py` sha256 `32e89e33479db4c5f11ef468ac6320a62bfd92c6ae4dd966ef6b6ad5908b19f9`. Both match the coordinator's HASHES.txt.
- Read: blueprint.yaml, db_schema.json, share_tools.py (signatures), products/coverage.yaml, products/oxygen.yaml (variant parameter lines only), the extended charter, task_tools.py, and the compute primitives in `skills/erl-task-instantiate/scripts/check_compute.py` (lines 225-390), which give the restricted expressions their meaning.
- Masked and unread at freeze time: every `tasks/*.json`, including evaluation_criteria, computations, design_rationale, solvability_contract, prerequisite_closure, charter_scope, required_documents and the db_closure fields. Tasks were read only through `.audit_views/.../{0,1}.view.json`.
- Entry conditions (Step 0): the coordinator supplied the gate snapshot (all rc=0 except check_traceability rc=1, with the reason given as the pre-render unlock-tool names, deferred by design), the masked views with hashes, and HASHES.txt. Input is complete. check_traceability being red before render is the coordinator's stated design, so I recorded it here and did not re-run it.
- Base section: a `yaml.safe_load` comparison of every base key (category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies) against `blueprint/products/coverage.yaml` returned equal for all ten. The base copy is verbatim.
- Engine semantics used in the analysis below (check_compute.py): `SUM/COUNT/LATEST` are scoped to the target holding (`coverage_id = HID`). `within_months=N` keeps a row when `0 <= MONTHS(row_date, NOW) < N`. `MONTHS` counts whole calendar months and subtracts one when the day of month has not been reached. `LATEST` keeps the first row on a date tie (strict `>`), so ties resolve in insertion order. `XCOUNT/XLATEST` read another category's event rows that belong to the customer. `RND` is Python `round(float(x), 2)`, which is banker's/binary rounding and not half up.

### policy_conflict_scan

The extended charter has six policies, and the graph is acyclic:

| policy | write tool (owner) | computes | prerequisite edges |
| --- | --- | --- | --- |
| coverage_ext_hardship_discount | apply_hardship_discount_c60f16b6 (agent) | amount | [] |
| coverage_ext_prompt_pay_discount | apply_prompt_pay_discount_12f1a0eb (agent) | amount | [] |
| coverage_ext_arrangement_deposit | pay_arrangement_deposit_e794f585 (user) | amount | hardship (value_input d_balance), prompt_pay (value_input d_balance) |
| coverage_ext_arrangement_installment | set_payment_arrangement_62cec67a (user) | monthly_amount | deposit (value_input r_balance) |
| coverage_ext_medicaid_crossover | post_crossover_payment_b661a2ed (agent) | amount | [] |
| coverage_ext_arrangement_revision | revise_payment_arrangement_5f5b46f9 (user) | monthly_amount | crossover (value_input m_balance) |

The two connected components are {hardship, prompt_pay} -> deposit -> installment and crossover -> revision. With M=2, the two trees cover all six policies only if one task claims the first component and the other claims the second. Scope exclusivity and joint completeness are confirmed against `charter_scope` after the reveal (see the task files). The pre-reveal expectation is that task 0 holds the first component and task 1 the second.

Overlapping subjects:
- **Hardship vs prompt-pay on one charge.** Both post a coverage_adjustment on a charge. The prompt-pay rule says "A charge that also earns a hardship discount keeps only the larger of the two discounts, and QMB protection displaces both". The hardship rule says "when QMB protection applies to a charge no hardship discount is posted on it". Neither write reads the other's adjustment as an input (hardship reads charges, payments and statements; prompt-pay reads payments, statements and charges). The two parallel edges into deposit therefore do not interact through values. They interact only if one charge qualifies for both, and that is checked per task.
- **Installment vs revision.** Both write `coverage_payment_plan_set`. Installment applies to "a coverage account with no arrangement active" and revision to "an arrangement already in force", so their triggers are disjoint.
- **Deposit vs base payment allocation.** See override_declarations O-3.
- **Crossover vs base coordination and QMB.** See override_declarations O-5.

Time anchors: every policy works at the handling date (NOW). The prompt-pay rule adds a self-anchoring clause, "it is figured as of the day it is posted". No policy depends on a future event.

Cross-category read boundaries: hardship, deposit, installment and revision read mobility, oxygen and pap holdings and rental_paid billing rows. Crossover reads the oxygen holding, the oxygen variant parameters and oxygen_billing. All are read-only and consistent with the charters' declared fields.

### rule_compute_equivalence

Mechanical sweep: every `compute_basis` sentence is a verbatim sentence of its policy's `rule`. Every `overwrite.replaced_by` is verbatim in its rule. Every `baseline.rule` sentence is in the rule. Every factor's `decides` and `bindings` name existing compute bindings, and every ladder tier is stated in the rule prose.

Findings from the semantic sweep:

- **E-1 (deposit: a rule cap with no compute).** The rule says "it is applied to the account's oldest open charge ... and it never exceeds that charge's open amount". Compute has `d_figured`, `d_deposit` and `result: RND(d_deposit, 2)`, with no `MN(..., oldest open amount)`. The rule promises a cap that compute does not implement. The consequence exists only where the figured deposit exceeds the oldest open charge's open amount, which is checked per task (task 0).
- **E-2 (hardship: an object selector absent from the rule).** `h_charge_amount: LATEST('coverage_ledger','amount', event_type='coverage_patient_charge')` takes the most recently posted charge on the account, of any responsibility_type. The rule ("each such charge receives one adjustment ... The hardship discount on a charge is ... the charge's amount as posted") discounts every eligible charge posted while the approval is in force and never says "latest". It also excludes self_pay, upgrade_difference, non_covered_with_notice and unreturned_equipment, which the selector does not filter. This is an invented selector. Its consequence (the wrong charge, or a missed second eligible charge) depends on the world and is checked per task.
- **E-3 (prompt-pay: proxy selectors).** `p_paid_amount`, `p_paid_on` and `p_paid_method` are the LATEST coverage_payment on the account, and `p_charge_date` and `p_charge_source` are the LATEST *coinsurance* charge. The rule speaks of "the payment that paid the charge in full" and "the charge paid", and no rule sentence restricts the charge to coinsurance. Compute also does not test the eligibility clause "pays in full no later than `prompt_pay_window_days` calendar days after the first statement showing it": `result` fires for any class with pct > 0. A consequence arises only where the latest payment or the latest coinsurance charge is not the qualifying pair. Checked per task.
- **E-4 (installment: a wheelchair paid-month count with no period or reversal netting).** The rule says "the class's `capped_rental_months` less the paid rental months billed for that wheelchair". Compute uses `XCOUNT('mobility','mobility_billing', event_type='mobility_rental_paid')`, which counts all of the customer's paid rental rows on every wheelchair and in every period, with no netting of `mobility_claim_reversal`. The base program rule says title passes "after `capped_rental_months` paid months in one continuous rental period". This bears only if the world has reversals, a restart or a second wheelchair. Checked per task.
- **E-5 (crossover: the pricing line is not the settled charge's line).** The rule says "worked from the claim line the primary adjudicated most recently for the patient's oxygen equipment". Compute uses `XLATEST(...)` over every oxygen_billing row (paid, denied, reversal or contents) of the customer, with no event or coverage filter. The tool writes the settled charge's own `source_bill_id`. Base coverage_agg_payment_allocation says "A secondary payment is never reallocated: it settles only the charge it adjudicated". If the charge being settled does not stem from the latest oxygen line, the payment settles charge A while being priced from line B. Checked per task (task 1).
- **E-6 (rounding).** Every policy states "rounded to the cent half up", but `RND` is Python `round` on binary floats. This bears only on exact .xx5 intermediates. Recorded as an observation and checked per task.
- **E-7 (scope of "the patient charges").** The hardship burden ("the patient charges in the medical-burden window"), the deposit exposure ("the patient charges posted in the current benefit year") and similar aggregates are computed on this coverage account only (SUM is holding-scoped). The rules read naturally as patient-wide. This bears only if the patient has a second coverage account carrying charges. Checked per task (task 1 has two holdings).

### action_binding_and_uuids

- `(target_tool, computes)` pairs are all distinct: (apply_hardship_discount_c60f16b6, amount), (apply_prompt_pay_discount_12f1a0eb, amount), (pay_arrangement_deposit_e794f585, amount), (set_payment_arrangement_62cec67a, monthly_amount), (post_crossover_payment_b661a2ed, amount), (revise_payment_arrangement_5f5b46f9, monthly_amount). Each tool is claimed by exactly one policy.
- uuid8s: c60f16b6, 12f1a0eb, e794f585, 62cec67a, b661a2ed, 5f5b46f9. They share no prefix, are not sequential, have no tails copied from each other and show no adjacency pattern, so they are consistent with independent generation.
- Docstrings: the only ordering-like word is "then" at lines 161 and 172 ("statements then show the installment due", "installments then fall due on the same day"). Both describe a consequence of the same call, not a position in a sequence. No docstring names another tool.
- No tool judges a prerequisite. All six bodies are unconditional: find holding, create or update rows, return a receipt. None raises, refuses or hints when hardship, prompt-pay, deposit or crossover rows are missing. `set_payment_arrangement` and `revise_payment_arrangement` do not even read the ledger. The SOURCE-CHAIN "tool judging prerequisite" check passes charter-wide.
- Observation: `pay_arrangement_deposit` derives its confirmation code deterministically from (coverage_id, entry, method, amount). This is consistent with the deposit overwrite ("the confirmation code the payment network issues").

### prerequisite_graph

- `prerequisite` is filled on all six policies (`[]` on hardship, prompt_pay and crossover).
- Every `problem` names an extended policy in this file. None is a base policy and none points at itself. The graph is acyclic: hardship and prompt_pay -> deposit -> installment, and crossover -> revision.
- Every `policy_source` is verbatim in the blocked policy's own rule (mechanical check), and none appears in the depended-on policy's rule.
- `form: state` on all four edges, and no `fallback_reason` is present, as required.
- `resolved_by` equals the depended-on policy's `target_tool` on all four edges.
- `kind: value_input` with `gate` ∈ {d_balance, r_balance, m_balance}, each an existing compute binding (`F('patient_balance')`) of the blocked policy. Each depended-on write lowers `coverage_holdings.patient_balance` (tool bodies), so `effect` holds in kind.
- `condition` vs sentence:
  - hardship->deposit: the condition narrows to "a discountable responsibility_type", which the sentence ("every charge ... carries its hardship discount") carries through "its", read with the hardship rule's own type list. No strengthening.
  - prompt->deposit: the condition adds "on a class offering prompt pay", which the sentence implies through "within the prompt-pay window".
  - deposit->installment: the condition adds "applied to the account's oldest open charge", taken from the deposit rule.
  - crossover->revision: the condition matches the sentence.
- Observation G-1 (installment edge `effect`): it reads "The deposit payment lowers the account's patient_balance by the deposit, which is the balance divided by the arrangement term (r_balance)". That description of the deposit is false: the deposit rule makes it "the deposit percentage of the account's patient_balance", settled by rentals. It does not change the edge's validity, because the deposit does lower the balance r_balance reads. It is an assertion about the world, so the per-task file checks it against the gold figures.
- No authoring-viewpoint phrasing ("in this task", "at the opening") appears in any `prerequisite` entry.

### prerequisite_sentences

Four-point test, edge by edge:

1. **deposit <- hardship.** "The arrangement deposit is figured only after every charge posted while a hardship approval is in force carries its hardship discount."
   - Connective: "only after".
   - Waited-on state: a record-visible fact, namely that each such charge has a coverage_adjustment with adjustment_reason hardship_discount whose applied_to_entry_id is that charge. No action, performer or tool is named.
   - No tool name, policy id, snake_case token or row id.
   - Strength matches the condition.
   - Exactly one write of this difficulty produces a hardship_discount adjustment: `apply_hardship_discount_c60f16b6`. The prompt-pay tool writes prompt_pay_discount.
   - Derivation: the sentence names the state "carries its hardship discount". The hardship rule ("each such charge receives one adjustment with adjustment_reason hardship_discount, posted against that charge") describes the write that produces it, so the reader resolves the hop to the hardship policy's write. Single reading.
2. **deposit <- prompt-pay.** "The arrangement deposit is not worked out until every charge the patient paid in full within the prompt-pay window carries its prompt-pay discount."
   - Connective: "not ... until".
   - State: an adjustment_reason prompt_pay_discount row against the charge.
   - Only `apply_prompt_pay_discount_12f1a0eb` produces it.
   - The prompt-pay rule ("posted as one adjustment with adjustment_reason prompt_pay_discount against the charge paid ... A prompt-pay discount that was not posted on the paying day is posted when the omission is found") makes the late write legitimate. Single reading.
3. **installment <- deposit.** "The monthly installment of a new arrangement is fixed only after the arrangement deposit stands on the account as a patient-payment entry posted on the day the arrangement is set."
   - Connective: "only after".
   - State: a coverage_payment row dated the handling date.
   - "Arrangement deposit" is a business term that the deposit rule defines ("An arrangement deposit is the patient's own payment that opens a monthly payment arrangement").
   - The only write that produces it is `pay_arrangement_deposit_e794f585` (owner=user). The agent therefore has to hand that write over to the customer. Single reading.
4. **revision <- crossover.** "A revised installment is not fixed until every coinsurance charge for a date of service on or after the Medicaid record's effective date carries the crossover payment that Medicaid owes on it."
   - Connective: "not ... until".
   - State: a coverage_secondary_payment row with payer_coverage_id = the Medicaid record against each such charge.
   - The only write is `post_crossover_payment_b661a2ed`. Single reading.

Further checks across all edges:
- No rule carries a second wording of any of these dependencies, a tool name or another problem's id.
- The depended-on rules do not restate the sentences.
- No other rule sentence states a cross-problem order without grounding a declared edge. The hardship/prompt-pay "keeps only the larger" sentence is a choice rule, not an order.
- No task tree rests on a base sentence stating a cross-problem order.

### override_declarations

Findings only, swept sentence by sentence against every `base_policy_refs` entry. Each affected task demonstrates the consequence in its own file.

**O-1. hardship vs base coverage_hardship. Undeclared override (dropped branch), candidate SOURCE-POLICY RED.**
- Base: "charges already open on the approval date receive it only if posted within `hardship_lookback_days` before the approval date." Under base, open charges posted up to 180 days *before* the approval date receive the hardship discount.
- Extended scope sentence: "Summit Ridge grants a financial-assistance discount on each patient charge ... that is posted while the account's hardship approval is in force". Charges posted before the approval date are not "posted while ... in force", so the base lookback branch is dropped.
- This is not named in `overwrite`, whose two entries are the "open amount" clause and the QMB clause.
- The deposit edge sentence ("every charge posted while a hardship approval is in force") inherits the narrowed scope.
- Other base sentences: the tier ladder, individual decision, documentation window and validity are followed. The excluded types are followed. "Equal to the tier's discount_pct of the charge's open amount" is declared (replaced by "amount as posted" plus points).
- Bears on: the task whose tree contains hardship (expected task 0). The demonstration needs an open discountable charge posted in [approval − 180 days, approval).

**O-2. prompt-pay vs base coverage_evt_adjustments. Undeclared conflict with the no-stacking sentence, candidate SOURCE-POLICY RED.**
- The superseded prompt-pay sentence is declared in full, including "on the paying day" and "the payment due is reduced by it".
- The base sentence "Adjustments on one charge never stack beyond its open amount" is not superseded. The extended rule grants the discount on a charge "that the patient pays in full", and the late-posting clause ("A prompt-pay discount that was not posted on the paying day is posted when the omission is found, against the same charge") posts it after the payment has brought the charge's open amount (coverage_msr_open_charges) to 0.00.
- Under the inherited base sentence, the adjustment on that charge cannot exceed its open amount of 0.00, so the discount is 0.00 (or not posted). Under the extended rule it is the figured prompt-pay amount.
- Two clauses in force govern the same quantity and give different values.
- Bears on: the task whose tree contains prompt_pay (expected task 0), when the qualifying charge is fully paid at the opening.
- Base sentences followed: "QMB protection displaces both" and "only the larger one is posted" (restated). The missing-notice, small-balance and claim-reversal sentences are not touched.

**O-3. deposit vs base coverage_evt_payment and coverage_agg_payment_allocation.**
- The two declared overrides (reference copying and dedup) are in order.
- Not declared:
  - (a) Base allocation: a payment naming no charge "is allocated across all of the patient's coverage accounts, oldest open charge first ... until the payment is used up". The extended rule says "applied to the account's oldest open charge ... and it never exceeds that charge's open amount", which narrows the scope to one account and replaces spreading with a cap.
  - (b) Base evt_payment: "When the payment exceeds the open amount of the charges it is applied to, the remainder posts with an empty applied_to_entry_id and leaves a credit". Under the extended cap that branch can no longer arise.
- Whether (a) bears needs a second coverage account with an older open charge. Whether the cap bears needs a figured deposit greater than the oldest open charge's open amount. Both are checked in the deposit task's file.
- Recorded here as a finding and per task as RED only if demonstrated.

**O-4. installment vs base coverage_payment_plan.**
- The installment sentence is declared.
- The other base sentences are followed: min balance, signed agreement, account status, start date within one cycle, default and completion.
- Extended adds "on the terms the patient signed in the approved payment_plan_agreement request". coverage_requests carries `requested_amount`, so where the approved agreement row holds a requested_amount, "the terms the patient signed" offers a second reading of the monthly amount. Checked per task (task 0).

**O-5. crossover vs base coverage_agg_coordination and coverage_agg_payment_allocation.**
- The coinsurance clause is declared, and its replaced_by is verbatim in the rule.
- Observation: the replaced_by text names only the pricing method. The extra "less the Medicaid copayment" deduction from the secondary payment is not named in replaced_by, although it changes the same quantity the named base clause governed. The base clause itself is named, so the declaration exists, but its stated replacement is narrower than the rule.
- Base "on the deductible charge only when its `as_secondary_covers_deductible` is true": Medicaid's value is true. The extended rule prices *every* charge from the latest oxygen line's cost share and does not distinguish deductible charges. Checked per task.
- Base allocation "it settles only the charge it adjudicated": see E-5. Checked per task.
- Base QMB (coverage_qmb_protection): when the Medicaid record is QMB and active, Medicare deductible and coinsurance charges are removed in full by a qmb_cost_share_prohibited adjustment on their posting date, so their open amount is 0. The extended rule keeps "never exceeds the open amount" and a "qmb record owes no copayment" tier. Checked per task.

**O-6. revision vs base coverage_payment_plan.**
- The installment sentence is declared.
- Inherited: min balance 150 (a "set" of the plan), the signed agreement (the extended rule says it "rests on the agreement the patient signed for it"), account status, and the no-reinstatement of a defaulted plan.
- Observation: the extended rule says the revision "keeps the arrangement active", while the tool writes payment_plan_status="active" unconditionally. That matches only if the arrangement is active at the opening. Checked per task.

**O-7. QMB-clause overwrites (hardship, prompt-pay).**
- Both "supersede" the base sentence "The QMB protection applies only while the Medicaid record is active" with text that changes no scored quantity: hardship and prompt-pay never needed a Medicaid record under base.
- Observation only. It is a declaration of a non-conflict, with no second answer.

### factor_ladders

Each policy declares 6 factors. All ladders have ≥3 tiers, every tier is stated in the rule, every `decides` is an input binding (never `result`), binding sets within a policy are disjoint, and no two tiers of a ladder select the same value or method.

| policy | parameter | method | cross_difficulty factors | multi-source factor(s) |
| --- | --- | --- | --- | --- |
| hardship | 5 (burden 12/5/0, rental 8/5/0, tenure 3/1/0, effort 3/1/0, statement-age 3/1/0) | 1 (window: wheelchair-rental anchor / plan-year anchor / trailing 12) | window (mobility), ongoing rental (mobility, also reads oxygen and pap) | ongoing rental ("two or more of" wheelchair/oxygen/PAP: distinct records); window tier 2 (no rental wheelchair ∧ plan_year class) |
| prompt-pay | 5 (speed 2/1/0, channel 1/0.5/0, loyalty 1/0.5/0, aged −1/−0.5/0, size 1/0.5/0) | 1 (speed start day: charge date / charge+7 / latest statement) | **none** | loyalty (coverage tenure ∧/∨ payment count) |
| deposit | 5 (proven 4/2/0, hardship 4/2/0, exposure 4/2/0, dunning 3/1/0, bank 1/0.5/0) | 1 (rental settlement: half floor-$ / ¾ ceil-$ / as is) | rental settlement (mobility, also oxygen and pap) | proven payer (plan status ∧/∨ latest payment date) |
| installment | 5 (proven 2/1/0, rental-load 2/1/0, loyalty 2/1/0, size 2/1/0, regularity 2/1/0) | 1 (core term: hardship months left / months to wheelchair ownership / max months) | core term (mobility), rental-load (mobility) | balance size (balance ∧ statement cycle) |
| crossover | 4 (rate share 96/92/allowed%, copay band 0/0.65/1.30/1.90/class copay, flow ×1.5/×0.5/×1, usage 90/75/100) | 2 (pricing method, fee composition) | all six (oxygen) | pricing method (qmb_status ∧ line kind) |
| revision | 5 (rental-burden 2/1/0, new-charge 2/1/0, record 2/1/0, tenure 2/1/0, relief −2/−1/0) | 1 (core term: left / left+6 / 12 afresh) | rental-burden (oxygen) | core term (payment count ∧ installments left) |

The counts meet the bounds per policy (4-6 factors, ≥2 parameter, ≥1 method). Prompt-pay alone carries no cross-difficulty factor, which is permissible only if every task containing it also contains a policy that does. Every factor's fall-through equals its `baseline`, and every `baseline.rule` is self-sufficient (rate × balance, or balance / max months, or class pct, with its default params).

Structural findings:

- **F-1. crossover_copay_band: a scope-restating conjunct. SOURCE-FACTOR RED, charter-global.**
  - Tiers 2-4 each require "the line's date of service is on or after the Medicaid record's effective_date". The policy's own scope sentence is "every patient charge the primary leaves on a claim line whose date of service falls on or after the Medicaid record's effective_date receives the Medicaid crossover payment". The revision edge's sentence restricts the same way ("for a date of service on or after the Medicaid record's effective date").
  - So for every customer who reaches this write on a charge priced from its own line, that conjunct of tiers 2-4 already holds. It restates the policy's scope instead of dividing its customers.
  - Compute implements it as `DAYS(F('effective_date'), s_line_start) >= 0`.
  - The ladder still divides customers on price bands and QMB, so this does not by itself strip the factor's weight. It is a ladder-reality defect.
  - The task containing crossover (expected task 1) cites this and shows whether the priced line's DOS is on or after the effective date.
- **F-2. Method labels that are numeric offsets. Observation.**
  - prompt_speed_start_day tier 2 is tier 1 minus the constant `supply_transit_days` (DAYS(charge, paid) − 7).
  - revision_core_term_convention tier 2 is tier 1 plus the constant `extend_months` (m_left + 6).
  - In each factor the third tier changes the anchor or algorithm (latest statement date, or 12 counted afresh), so each factor still has a genuine method tier. One pair of tiers in each is a parameter substitution under a method label.
- **F-3. hardship assistance percentage capped at `max_pct` 100. Per-task weight risk.**
  - `h_assist_pct = MN(100, tier + points)`. On a full_100 tier, every point factor substitutes to an unchanged 100.
  - At partial tiers, points beyond the 100 cap also lose weight.
  - Checked per task.
- **F-4. Realism observations** (no tier has a demonstrable unreal outcome):
  - Coverage-tenure and payment-effort points that raise a financial-hardship discount, and loyalty months that lengthen an installment term, reward tenure rather than need. They are unusual in DME financial-assistance policies but not demonstrably unpublishable.
  - "Usage share" of the Medicaid oxygen rate (sleep_only/exertion_only at 75%) is not a standard Medicaid crossover feature.
  - The copay bands (0.65/1.30/1.90) mirror real state Medicaid nominal copay bands.
  - The lesser-of crossover pricing (cost share vs Medicaid rate − primary paid) is the real Medicaid crossover method.
  - All are recorded as observations.
- **F-5. Stamp check.**
  - deposit_dunning_points and installment_balance_size read `statement_cycle` on the latest statement. That is an ordinal the statement history stamps, not a tier name, so it is acceptable.
  - deposit_hardship_points and installment_core_term tier 1 read `hardship_tier`/`hardship_approved_date`, which are the authoritative approval record (the hardship_set event output) and not a stamp naming the factor's outcome.
  - No field named after a factor tier was found in the schema.

### findings

| id | kind | summary | bears on |
| --- | --- | --- | --- |
| O-1 | SOURCE-POLICY candidate | base hardship lookback branch dropped without overwrite | task with hardship (exp. 0) |
| O-2 | SOURCE-POLICY candidate | prompt-pay discount on a fully paid charge conflicts with inherited "never stack beyond its open amount" | task with prompt-pay (exp. 0) |
| O-3 / E-1 | SOURCE-POLICY candidate | deposit cap "never exceeds that charge's open amount" not in compute; single-account narrowing of base allocation undeclared | task with deposit (exp. 0) |
| O-4 | SOURCE-TASK candidate | "on the terms the patient signed" vs computed installment where requested_amount exists | task with installment (exp. 0) |
| O-5 / E-5 | SOURCE-POLICY candidate | crossover priced from latest oxygen line, not necessarily the settled charge's line; deductible-charge and QMB interplay | task with crossover (exp. 1) |
| E-2, E-3 | SOURCE-POLICY candidate | LATEST proxies for "the charge"/"the qualifying payment" with no rule sentence | tasks with hardship / prompt-pay |
| E-4 | observation / candidate | wheelchair paid months counted without period/reversal netting | task with installment |
| E-6 | observation | RND is not half-up | all |
| E-7 | observation / candidate | holding-scoped aggregates vs "the patient charges" | task 1 (two holdings) |
| F-1 | SOURCE-FACTOR RED | copay-band DOS conjunct restates the policy scope | task with crossover |
| F-2, F-4, G-1, O-7 | observation | method labels on offsets; realism; false edge-effect description; no-op QMB overwrites | — |
| F-3 | per-task weight risk | max_pct cap can neutralise hardship points | task with hardship |

## closing_checklist

Written 2026-10-12, after both tasks' frozen derivations and GT comparisons were on disk. Everything above this heading was written before any reveal and is left untouched.

- **Per-task files.** `0.md` and `1.md` match tasks 0 and 1 one-to-one, and this file sits alongside them. This is the first revision, so there are no older revisions. Each comparison section carries a verdict:
  - Task 0: **SOURCE-POLICY RED** (T0-1).
  - Task 1: **SOURCE-FACTOR RED** (T1-1).
  - So "every comparison section carries a PASS" is **not met**.
- **Coverage and scope.**
  - charter_scope task 0 = {hardship, prompt_pay, deposit, installment}; task 1 = {crossover, revision}. The scopes are pairwise disjoint and jointly cover all six extended policies.
  - Task tools match their policies one-to-one.
  - uuid8s are independent (`§action_binding_and_uuids`).
- **Trees.**
  - Task 0: 3 prerequisite problems and 3 value_input edges (floor 2).
  - Task 1: 1 prerequisite problem and 1 value_input edge (floor 1).
  - Each tree has at least one owner=user write: deposit and installment in task 0, revision in task 1.
  - No cycle, and the union graph of the difficulty is a DAG.
  - Every edge was unmet at the opening and bears weight (figures in the task files, matching prerequisite_closure).
- **Factors.**
  - Every computation declares 6 factors with a self-sufficient baseline, and every factor bears weight on its task's world (all GT factor_sensitivity figures reproduced).
  - Each task has ≥1 multi-source and ≥1 cross-difficulty factor, with the other product's rows seeded.
  - **Exception:** crossover_copay_band's DOS conjunct restates the policy scope (F-1 / T1-1).
- **Charter-global outcomes after the per-task demonstrations:**

| Finding | Outcome |
| --- | --- |
| O-2 | demonstrated in task 0 → RED |
| F-1 | demonstrated in task 1 → RED |
| O-1 (hardship lookback) | no consequence on task 0's world (every lookback charge already discounted; the author's seed reads base lookback cumulatively) → observation |
| O-3 / E-1 (deposit cap and single-account scope) | no consequence (one account; 43.00 ≤ 252.44) → observation |
| O-4 (signed terms) | no consequence (requested_amount is the total balance) → observation |
| O-5 / E-5 (crossover line vs charge) | no consequence (lines coincide) → observation |
| E-2 / E-3 / E-4 / E-6 / E-7 | no consequence on either world → observations |
| F-2 / F-4 / G-1 / O-7 | observations |

- **Gate re-run on final form.** Not applicable: the difficulty does not close while T0-1 and T1-1 stand. The auditor did not re-run gates. The coordinator's snapshot was taken on the same artifact hashes (yaml `0b0f020c…`, task_tools `32e89e33…`), which were re-verified at the start of this audit.

**Difficulty result: does not pass the source-layer audit** (task 0 SOURCE-POLICY RED; task 1 SOURCE-FACTOR RED).

## revision_2

### charter_global_frozen (round 2)
- Re-derived 2026-10-12, before any round-2 GT was read. Auditor: the same independent auditor as round 1.
- Inputs changed, so every charter-global section is re-derived rather than carried forward:
  - `coverage.extended.yaml`: round-1 hash `0b0f020c…`, now `f9b0f64ff57b8336c7dab8d0789b46a18b752621ac99ce18b80573f7ba60de88`.
  - `task_tools.py`: round-1 hash `32e89e33…`, now `3aec55640db365c4b933cf74523985bc01137b6b6bfc4ead8a919b5a53877fc1`.
  - Both new hashes match HASHES.txt. The views 0/1 are unchanged (`bbb03e23…`, `df1acddb…`).
- No copy of the round-1 charter exists on disk, so the new charter was read in full rather than diffed.
- Entry: the coordinator's round-2 gate snapshot is all green, except check_traceability, which is pre-render by design. Input complete.
- Mechanical sweep, all clean:
  - The base section equals the blueprint (all 10 keys).
  - Every compute_basis, baseline.rule and replaced_by sentence is verbatim in its rule.
  - Every superseded_clause is verbatim in its base policy.
  - Every factor binding exists.
  - Every edge's policy_source is verbatim in its blocked rule, and every resolved_by equals the depended-on target_tool.
  - The graph is unchanged: {hardship, prompt_pay} → deposit → installment, and crossover → revision. All edges are state-form and value_input. Acyclic.

### Round-1 item status (verified against the artifacts, not the reworker's list)

| id | round-1 | round-2 evidence | status |
| --- | --- | --- | --- |
| T0-1 / O-2 | prompt-pay vs undeclared base no-stacking sentence | prompt-pay `overwrite[2]` now supersedes "Adjustments on one charge never stack beyond its open amount: …" with "A prompt-pay discount is posted for its full figure even though the qualifying payment has already brought the charge's open amount to 0.00 …", verbatim in the rule | **closed** (declared; the merged reading is unique on that quantity) |
| T1-1 / F-1 | copay-band DOS conjunct restates scope | copay ladder now bands on the line's Medicare cost share (≤10 / ≤45 / ≤75 / larger) with a qmb tier; no DOS conjunct; compute `s_copay` reads `s_copay_share` | **closed** |
| O-1 | hardship lookback dropped | rule scope now states "a charge posted while the approval is in force, and a charge already open on the approval date that was posted no more than `hardship_lookback_days` calendar days before it"; compute `h_charge_covered` | closed |
| O-3 / E-1 | deposit cap absent in compute; allocation narrowing undeclared | cap removed from rule ("a deposit larger than that charge's open amount is still posted whole on that one entry"); two new overwrites supersede the base allocation sentence and the base remainder-credit sentence | closed |
| O-4 | "terms the patient signed" | rule now reads "once a payment_plan_agreement request for the account is approved" | closed |
| O-5 / E-5 | crossover line vs settled charge; deductible; copay not in replaced_by | rule: "it settles the coinsurance charge that stems from that line"; "A deductible charge in that scope is paid by Medicaid under the coordination rule's deductible clause and is not priced here"; replaced_by is now the payment sentence including the copay | closed |
| E-2 | hardship LATEST selector absent from rule | rule: "A hardship discount is figured for the account's most recently posted patient charge; it is 0.00, and nothing is posted, when that charge is of a type the discount never reaches or was posted more than `hardship_lookback_days` …" | closed as a rule/compute gap. See N-1 for the tension this creates |
| E-3 | prompt-pay proxies and unchecked eligibility | rule: "figured for the account's most recent patient-payment entry and the account's most recently posted coinsurance charge; it is 0.00 … when that entry is smaller than that charge or was posted before, or more than `prompt_pay_window_days` … after, the latest statement"; compute `p_eligible`; result now on `p_charge_amount` | closed as a rule/compute gap. **The re-anchored window opens N-2** |
| E-4 | wheelchair paid months not netted | rule "net of any paid month later reversed"; compute subtracts mobility_claim_reversal count | closed (observation remains: "one continuous rental period" is still not modelled) |
| E-6 | RND not half up | every RND now adds +0.000001 | closed |
| E-7 | holding-scoped aggregates | the rules now say "on this coverage account" / "posted on the coverage account" | closed |
| F-2 | numeric-offset method tiers | prompt speed tier 2 is now weekdays = ⌊5/7 × calendar days⌋. The revision core tier 2 is now the benefit-year re-anchor `benefit_year_months − MONTHS(benefit_year_start, NOW)` | revision closed. The prompt tier 2 is a proportional scaling, not a real weekday count. That is a realism observation only, as no task's world reaches the supply tier |
| G-1 | installment edge effect misdescribed | effect now "lowers … patient_balance by the deposit amount … and adds one patient-payment entry" | closed |
| O-6 | revise tool forced status active | tool body now updates only payment_plan_monthly_amount and echoes the stored status | closed |
| F-3, F-4, O-7 | — | unchanged | unchanged observations |

### New charter-global findings (round 2)

- **N-1. "Each such charge" vs "figured for the most recent" (hardship, prompt-pay, crossover). Candidate SOURCE-POLICY.**
  - Each of these three rules now carries a scope sentence that grants or requires the write on every qualifying charge:
    - Hardship: "each such charge receives one adjustment".
    - Prompt-pay: "grants a prompt-pay discount when a patient-payment entry pays a coinsurance charge … in full …".
    - Crossover: "every coinsurance charge … receives the Medicaid crossover payment".
  - Each also carries a sentence that figures the write for one record only: the most recent charge, the most recent payment/coinsurance pair, or the most recent oxygen line.
  - The deposit and revision edge sentences wait on "every charge … carries its …". Where a world has a second qualifying charge that lacks the write, the scope sentence and the edge demand a write that the figuring sentence never prices.
  - Bears on task 0 (prompt-pay, see N-2). It does not bear on task 1, where the only uncrossed coinsurance charge stems from the latest line, or on task 0's hardship, where the only uncovered charge is the latest.
- **N-2. Re-anchored prompt-pay window. Candidate SOURCE-POLICY / SOURCE-TASK, demonstrated in task 0.**
  - The base sentence "no later than `prompt_pay_window_days` calendar days after the first statement showing it" is superseded. Its replacement is now "no later than `prompt_pay_window_days` calendar days after the latest statement issued on the account before the payment".
  - A charge paid more than 30 days after the first statement that showed it, but within 30 days of the latest statement before the payment, now qualifies under the grant sentence. Under round 1's anchor it did not.
  - Combined with N-1, this produces a qualifying charge the figuring sentence does not reach.
- **N-3. Two policies supersede the same base sentence (observation).**
  - Hardship `overwrite[2]` and prompt-pay `overwrite[2]` both name the base no-stacking sentence, with complementary replacements. Each lets its own discount exceed the open amount and both keep "only the larger … QMB displaces both". They agree on every charge where both could apply.
  - Superseding the whole sentence also drops the general no-stacking cap for missing_notice, small_balance and claim_reversal adjustments, which neither replacement restates. Neither task posts those, so this is an observation only.

### Charter-global structure re-checked (round 2)
- `(target_tool, computes)` pairs are unchanged and unique. The uuid8s are unchanged and independent.
- No tool body judges a prerequisite or raises an error. The revise tool no longer writes status.
- Docstrings: "once" (balance once booked) and "then" (statements then show) describe consequences of the same call, not a sequence.
- Prerequisite sentences: the four-point test still holds on all four edges.
  - Deposit←hardship now reads "every charge the account's hardship approval covers carries its hardship discount". Its condition was updated to the lookback scope.
  - Each state is brought about by exactly one write.
- Factor ladders: every policy still has 6 factors, with the same parameter/method/cross-difficulty profile as round 1.
  - The new copay band has 5 distinct tiers (0 / 0.65 / 1.30 / 1.90 / class 3.00) on the cost share. Its tiers 2-5 carry the conjunct "a not_qmb record", which is the complement of tier 1 and not a scope restatement, because QMB customers do reach this write.
  - Revision core term tier 2 is a genuine method change.

### closing_checklist (round 2)

Written after both round-2 comparisons.

- **Per-task verdicts:**
  - Task 0: **SOURCE-POLICY RED** (R2-T0-1, new, introduced by the E-3/window rework), with the consequent SOURCE-TASK RED. T0-1 itself is closed.
  - Task 1: **PASS** on all four relationships. T1-1 is closed.
- **Scopes:** unchanged, disjoint, and jointly complete.
- **Trees and factors:**
  - The trees satisfy the bounds.
  - Every factor bears weight against an honest baseline.
  - All GT sensitivities were reproduced: task 0 unchanged from round 1; task 1 new figures 14.66 and 29.11.
- **Gate re-run on final form:** not applicable, since the difficulty does not close while R2-T0-1 stands.

**Difficulty result (round 2): does not pass.** The remaining defect is R2-T0-1: the prompt-pay grant sentence, together with the deposit's "every charge" prerequisite sentence, reaches d6db8a40, while the figuring sentence and compute price only the latest payment/coinsurance pair. That makes the gold installment 33.52 one of two defensible values; the other is 33.42.

## revision_3

### charter_global_frozen (round 3)
- Re-derived 2026-10-13, before any round-3 GT was read. Auditor: the same independent auditor as rounds 1-2.
- **Gates (step 1).** `bash /tmp/erl0057_coord/gates.sh patient_account_balances`, run by the auditor from the repo root:
  - check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK; check_grounding GROUNDING OK; check_cache_diff CACHE-DIFF INFO; check_cross_fire SCOPE OK.
  - All 8 lines are OK/INFO. The coordinator reports the same after the resume.
- **Views (step 2).** `make_views.py patient_account_balances` produced:
  - 0.view.json `bbb03e23…` (unchanged) and 1.view.json `df1acddb…` (unchanged).
  - coverage.extended.yaml `b3962d537140795b932a2d00019b7df25ee234c8fd359fd37eb7e6203bbbe92c` (changed from round 2's `f9b0f64f…`).
  - task_tools.py `3aec5564…` (unchanged from round 2).
- **Carried forward and re-derived.** The tool-module sections (`§revision_2` action binding: uuids, docstrings, tools judging nothing) are carried forward on the unchanged `3aec5564…` hash. The charter sections are re-derived.
- **Mechanical sweep (clean):**
  - The base section equals the blueprint.
  - Every compute_basis, baseline, replaced_by and superseded sentence is verbatim.
  - Every binding exists.
  - Every edge source is verbatim in its blocked rule, and every resolved_by matches.
  - The graph is unchanged and acyclic, with 4 state-form value_input edges. Each policy has 6 factors, with the same label and cross-difficulty profile.
- **Compute.** Unchanged in the figuring paths. Re-evaluated on both views with the engine's own `build_env`/`eval_compute` (scratch script). The results equal round 2's: task 0 43.30 / 5.07 / 43.00 / 33.52; task 1 14.66 / 29.11. Every factor sensitivity and all-baseline figure also equals round 2's.

### R2-T0-1 / N-1 / N-2: quantifier alignment across grant, figuring, compute and prerequisite

| policy | grant scope (rule S0) | figuring sentence | compute | prerequisite sentence |
| --- | --- | --- | --- | --- |
| prompt-pay | a coinsurance charge paid in full within the window; "the discount can be claimed only while that payment is the account's most recent patient-payment entry and that charge is the account's most recently posted coinsurance charge, an unclaimed discount lapses once a later payment or a later coinsurance charge posts" | "figured for the account's most recent patient-payment entry and the account's most recently posted coinsurance charge alone" | LATEST payment / LATEST coinsurance, `p_eligible` | deposit: "not worked out until the account's most recently posted coinsurance charge, when the account's most recent patient-payment entry paid it in full within the prompt-pay window, carries its prompt-pay discount" |
| hardship | lookback charges discounted on the approval date; "a charge posted on or after the approval date while the approval is in force receives it while it is still the account's most recently posted patient charge, and a covered charge that passes that moment without the discount keeps its amount" | "After the approval date the discount is therefore figured for the account's most recently posted patient charge alone" | LATEST charge; `h_charge_covered` requires DAYS(approved, charge) ≥ 0 | deposit: "figured only after the account's most recently posted patient charge, when the hardship approval covers it, carries its hardship discount" |
| crossover | "Medicaid crosses over each claim line … while that line is the newest one the primary has adjudicated … a coinsurance charge from an older line that carries no crossover was refused at its turn and stays with the patient" | "worked from the claim line the primary adjudicated most recently … alone" | XLATEST oxygen line | revision: "until the coinsurance charge stemming from the newest oxygen line the primary adjudicated, when that line's date of service is on or after the Medicaid record's effective date, carries the crossover payment" |

In all three policies the grant scope, the figuring sentence, the compute and the prerequisite sentence now quantify over the same single record. The prerequisite conditions match (deposit edge conditions name the latest charge or the latest payment/coinsurance pair; the revision edge names the newest oxygen line's charge). **R2-T0-1 is closed in the charter.** The world demonstration is in `0.md §revision_3`.

The four-point test still holds on all four edges:
- connectives "only after" / "not … until";
- the waited-on state is record-visible;
- no tool, id or snake_case token;
- strength equals the condition;
- exactly one write brings each state about.

### New charter-global findings (round 3)

These findings come from sweeping base sentence by sentence against the new lapse clauses.

- **N3-1. Hardship lapse narrows a base sentence not named in `overwrite` (candidate SOURCE-POLICY).**
  - Base coverage_hardship says "While it is in force, each charge of responsibility_type deductible, coinsurance, copay or repair_patient_share receives a coverage_adjustment with adjustment_reason hardship_discount".
  - The extended rule says "a covered charge that passes that moment without the discount keeps its amount".
  - The three hardship overwrites name the amount clause, the QMB clause and the no-stacking clause; none names this sentence.
  - The consequence arises only where a charge posted on or after the approval date is no longer the latest charge and carries no discount. Task 0 has no such charge (`0.md §revision_3`). **Observation.**
- **N3-2. Crossover "refused at its turn" narrows base coordination (candidate SOURCE-POLICY).**
  - Base says "When a secondary record exists, the secondary pays on those charges", and its only refusal is "a secondary payment refused for late filing leaves the charge with the patient".
  - The extended rule adds a refusal for an older uncrossed line. The overwrite names only the coinsurance-amount clause.
  - The consequence arises only where an in-scope coinsurance charge older than the newest oxygen line lacks a crossover. Task 1 has none (`1.md §revision_3`). **Observation.**
- **N3-3. Prompt-pay lapse (declared; observation).** The lapse is part of the superseded base prompt-pay sentence's replacement scope, so it is declared. It coexists with S2 ("posted when the omission is found"): an omission found before the lapse is posted, and after it the discount is gone. No second value arises on task 0.
- **N3-4. Realism (observation).**
  - The lapse clauses withdraw a discount or a Medicaid crossover because of when the desk acted rather than because of anything about the patient. In particular, Medicaid does not deny a crossover because a newer line exists, and a financial-assistance program does not forfeit a discount through posting latency.
  - These are scope rules, not factor tiers, so the SOURCE-FACTOR "unreal ladder" test does not apply. No world here makes them bind. Recorded so that a later world exercising them is checked.
- Round-2 items (T0-1, T1-1, O-1, O-3/E-1, O-4, O-5/E-5, E-2, E-3, E-4, E-6, E-7, F-2, G-1, O-6) were re-checked in the new text and none has regressed. N-3 (two overwrites of the no-stacking sentence) is unchanged.

### closing_checklist (round 3)

Written after both round-3 comparisons.

- **Verdicts.** The per-task files correspond one-to-one with the tasks, and all revisions (1-3) are kept in place. Every round-3 comparison section carries PASS:
  - Task 0: PASS on all four relationships. R2-T0-1 is closed.
  - Task 1: PASS on all four relationships, with no regression.
- **Scopes:** coverage is complete (6/6 extended policies), and the scopes are disjoint (task 0: hardship, prompt_pay, deposit, installment; task 1: crossover, revision).
- **Tools:** closed, with independent and unchanged uuid8s. No tool judges a prerequisite.
- **Trees:**
  - Task 0 has 3 prerequisite problems with 3 value_input edges; task 1 has 1 prerequisite problem with 1 value_input edge.
  - There are owner=user writes in both trees: deposit and installment in task 0, revision in task 1.
  - The union graph is a DAG. Every edge is unmet at the opening and bears weight.
- **Factors:**
  - Every computation declares 6 factors over a self-sufficient baseline, and each ladder has ≥3 distinct tiers stated in its rule.
  - Every factor bears weight on its world: all GT factor_sensitivity figures were reproduced with the engine's evaluator.
  - The all-baseline figure differs from gold in every computation.
  - Each task has multi-source and cross-difficulty factors, with seeded rows.
- **Gates on the final form.** Re-run by the auditor this round (`gates.sh`): all 8 OK/INFO. check_traceability remains pre-render-deferred per the coordinator.
- **Open observations** (no demonstrated consequence on either world): N3-1, N3-2, N3-3, N3-4, N-3, F-3, F-4, O-7, and the E-4 continuous-period remainder. If a later world exercises N3-1 or N3-2, they must be re-checked as candidate SOURCE-POLICY REDs.

**Difficulty result (round 3): passes the source-layer audit** (policy self-consistency, problem tree, factors and unique solution are PASS for both tasks).

## revision_4

### charter_global_frozen (round 4)
- Re-derived 2026-10-13, before any round-4 GT was read.
- **Gates.** `bash /tmp/erl0057_coord/gates.sh patient_account_balances`, run by the auditor: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / CACHE-DIFF INFO / SCOPE OK. All 8 are green.
- **Views.** `make_views.py` produced the following. Everything changed from round 3, so every section is re-derived:
  - 0.view.json `30882976f5eca78dfefbb4b419ced8dd88e04e6c7b3d895f5b1714a41b521ec2`
  - 1.view.json `41792789ad80e6c450a613e5adb6db973a1c1034721ddb95882e3faf0046bb70`
  - coverage.extended.yaml `24cd94a2a67860ef112fa74463d4b35d993cd7351e2bff4b45c165adb5f76fb2`
  - task_tools.py `7f99a817ec9a69de78b0f7ea5f4820e48e3ab6db6150a85a85425161b4202bf5`
- **Items to verify.** These were read from `audits/render_source/patient_account_balances/render_r1_source_mismatches.md` (15 items) plus N3-1, N3-2 and N3-4.
- **Audit-miss disclosure.** Render items 1-9, 11, 14 and 15 are defects that were present in the charter or tools I passed in rounds 1-3 and that I did not report. Items 12 and 13 equal my N3-1 and N3-2. My round-3 PASS was therefore wrong in scope. Rounds 1-3 checked factor weight but not factor-to-factor independence, did not check the full reach of each overwrite beyond the task's quantity, and did not compare tool docstrings with tool bodies. Round 4 adds all three checks.
- **Mechanical sweep (clean):**
  - The base equals the blueprint.
  - All compute_basis, baseline, replaced_by and superseded sentences are verbatim.
  - All bindings exist; all edge sources are verbatim; all resolved_by values match.
  - The graph is unchanged and acyclic, with 4 state-form value_input edges.
  - Each policy has 6 factors: hardship 1m/5p, prompt 1m/5p, deposit 1m/5p, installment 1m/5p, crossover 1m/5p (pricing-method factor removed, rental-phase share added), revision 1m/5p.
- **Factor-independence check (new).** For each factor, I took the transitive dependency closure of every one of its bindings over the compute graph and tested it against the bindings of every other factor. Result: **no factor reads another factor's binding or output, in any of the six policies.** The only bindings that read factor outputs are non-factor aggregates (h_assist_pct, p_rate, d_pct/d_figured/d_deposit, r_term, s_medicaid_rate/s_price, m_term). Those are the computation's combination step, and no factor reads them.

### Render items and N3-x: verification against the artifacts

| # | item | round-4 evidence | status |
| --- | --- | --- | --- |
| 1 | fee factor read flow factor | `crossover_addon_reckoning` reads its own `s_addon_lpm`/`s_addon_use`/`s_addon_portable` and the class params, not `s_flow_mult` | closed |
| 2 | pricing factor read three factors | the pricing-method factor is removed; the lesser-of price is now in the baseline rule; `s_medicaid_rate` is read only by the non-factor `s_price` | closed |
| 3 | speed points read start-day factor | merged into one method factor `prompt_speed_reckoning` (points = 2 − ⌊days/8⌋, weekday variant for supply lines, 0 otherwise) | closed |
| 4 | burden points read window factor | merged into one method factor `hardship_medical_burden_points` (one point per full `burden_step` 300 since the anchor; no points otherwise) | closed |
| 5 | new-charge read core-term binding | `revision_new_charge_months` has its own `m_charge_window`, so no dependency on `m_due_so_far` | closed |
| 6 | p_eligible read factor bindings | `p_eligible` now reads its own `e_paid_amount`/`e_paid_on`/`e_statement_on` | closed |
| 7 | prompt base amount | rule: "applied once to the amount of the charge paid in full"; compute `p_charge_amount` | closed |
| 8 | prompt statement date | rule: "pays in full on or after the latest statement issued on the account and no later than `prompt_pay_window_days` … after it"; compute latest statement with DAYS ≥ 0 | closed |
| 9 | prompt rental lines | rule: "a charge stemming from a wheelchair, an oxygen or a PAP line"; compute category test | closed |
| 10 | hardship lookback vs `h_charge_covered` | compute now `DAYS(h_charge_date, approved) <= lookback`, so lookback charges are covered. Residual: the rule's "already open on the approval date" is not tested in compute. It bears only if the latest charge predates the approval, which neither world has | closed as a gap; residual observation N4-2 |
| 11 | crossover ceiling | declared: `overwrite[1]` supersedes base "never exceeds the open amount of that charge" for priced crossovers only ("never exceeds the line's cost share, any part above the charge's open amount staying … as a credit"); compute `MN(s_cost_share, …)` | closed |
| 12 / N3-1 | hardship lapse | the lapse clause is removed. Rule: "a discount missed at that moment is posted when the omission is found", which agrees with base "each charge … receives" | closed (see N4-1) |
| 13 / N3-2 | crossover "refused at its turn" | removed. Rule: "every coinsurance charge … receives the Medicaid crossover payment … Crossover remittances are posted one line at a time, starting from the newest oxygen line" | closed (see N4-1) |
| 14 | retired clauses wider than replacements | every replaced_by is now scoped "for X, and only for X …; every other … remains under the base rule". I checked each one: stacking (non-hardship/prompt adjustments keep the cap); QMB (the active requirement is restated); secondary coinsurance share (other secondaries keep the base pct); the four payment clauses (non-deposit payments keep the base); prompt-pay on non-coinsurance charges keeps the base; installment and revision formulas cross-reference each other | closed |
| 15 | docstring statement effects | no docstring now mentions statements. Every docstring describes only the ledger row and holding fields that the body writes. set and revise: "the account's arrangement fields then carry …" | closed |
| N3-4 | realism of timing lapses | hardship and crossover lapses are removed. Prompt-pay now closes a missed discount at the next statement ("once a later statement has gone out showing the account without it, the account stands as statemented"), which is a recognisable billing practice and declared (base prompt-pay clause superseded for coinsurance) | closed |
| base-log | "three adjustments exist" lists four; `prompt_pay_window_days` description says first statement | base-text issues for the blueprint's log, not this difficulty's charter; the extended rule governs coinsurance prompt-pay explicitly | observation (forwarded) |

### New charter-global observations (round 4)
- **N4-1.** "Every" scope vs one-at-a-time figuring persists in a softened form in hardship, prompt-pay and crossover.
  - The rules now say missed items are "worked one charge/payment/line at a time, starting from the most recent". But the figuring sentence and compute still price only the most recent item.
  - Where a world has two or more missed items, the older ones have no figuring path. The deposit's hardship and prompt-pay edge sentences still say "every …".
  - Neither world has more than one missed item per policy (verified in the task files), so this is an **observation, with no demonstrated consequence**. It must be re-checked if a world exercises it.
- **N4-2.** Hardship compute does not test "already open on the approval date" for a pre-approval latest charge (residual of item 10). No bearing on either world.
- **N4-3.** The `hardship_medical_burden_points` and `revision`/`installment` core-term method labels: tiers 1-2 of the burden factor share one formula and differ in the window anchor date. Same class as F-2: recorded as an observation, with the label defensible because the anchor selects a different measure.
- **Structure re-checked:**
  - Each ladder has ≥3 distinct tiers stated in the rule, and every fall-through equals the baseline. The crossover baseline is now self-sufficient: (stationary + add-on) × allowed% → lesser-of → minus class copay.
  - Every task has a multi-source factor (task 0: hardship ongoing-rental, prompt loyalty, deposit proven-payer, installment balance-size; task 1: crossover copay band [qmb_status ∧ line cost share], revision core term).
  - Every task has a cross-difficulty factor.
  - Tools: uuid8s unchanged and independent; no tool body tests a prerequisite (no `if`/`raise`); docstrings name no other tool and no sequence.

### closing_checklist (round 4)

Written after both round-4 comparisons.

- **Verdicts.** The per-task files map one-to-one to the tasks, and revisions 1-4 are kept in place. The round-4 comparisons are:
  - Task 0: **PASS** on all four relationships.
  - Task 1: **PASS** on all four relationships.
- **Scopes:** complete (6/6 extended policies) and disjoint.
- **Tools:** closed, with independent uuid8s. No tool judges a prerequisite. The docstrings match the bodies.
- **Trees:**
  - Task 0: 3 prerequisite problems, 3 value_input edges. Task 1: 1 and 1.
  - There are owner=user writes in both trees: deposit and arrangement (task 0), revision (task 1).
  - The union graph is a DAG.
  - Every edge is unmet at the opening and bears weight, matching GT figure for figure.
- **Factors:**
  - Every computation has 6 factors, and factor-to-factor independence was verified mechanically.
  - Every baseline is self-sufficient and its all-baseline figure differs from gold.
  - Every factor bears weight: all GT sensitivities were reproduced by the engine.
  - Each task has a multi-source factor and a cross-difficulty factor, with the other product's rows seeded.
- **Overwrites:** each is checked against the full reach of its base clause, and every replacement now scopes itself and returns every other case to the base rule.
- **Gates:** re-run by the auditor on the final form; all 8 OK/INFO.
- **Open observations** (no demonstrated consequence on either world): N4-1, N4-2, N4-3, N-3 (superseded by the scoped replacements; residual none), F-3, F-4, O-7, and the base-text items forwarded to the blueprint log.

**Difficulty result (round 4): passes the source-layer audit.**

Caveat recorded for the coordinator: my round-3 PASS missed the render-found items listed in `§revision_4`, so round 4's added checks (factor independence, full-reach overwrites, docstring against body) are what this pass rests on.

## revision_5

### charter_global_frozen (round 5)
- Re-checked 2026-10-13, before any round-5 GT was read.
- **Gates.** `bash /tmp/erl0057_coord/gates.sh patient_account_balances traceability`, run by the auditor: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / CACHE-DIFF INFO / SCOPE OK / **TRACEABILITY OK**. All 9 are green; traceability is now green post-render.
- **Views.** `make_views.py` printed:

  | file | sha256 | vs round 4 |
  | --- | --- | --- |
  | 0.view.json | `bfa2253ad4639cce80d80911f02d0b38e0bd723ea77c727d364cdf56814c2f8b` | changed |
  | 1.view.json | `41792789…` | unchanged |
  | coverage.extended.yaml | `24cd94a2…` | unchanged |
  | task_tools.py | `7f99a817…` | unchanged |

- **Carried forward.** The charter and tool hashes are identical to round 4, so every charter-global section of `§revision_4` is carried forward by reference, on the grounds of those two hashes: sweep, factor independence, overwrite reach, prerequisite graph and sentences, uuids and docstrings, and factor ladders. That includes the open observations N4-1, N4-2 and N4-3.

### S2-1 (KB audit): cross-category seeded rows checked against their owning charters
The PAP rework in task 0 is S2-1's subject. I verified it against `blueprint/products/pap.yaml`:
- **The record now matches a self-pay purchase.** pap_holdings be722523 has status patient_owned, ownership_date = setup_date = 2021-09-14 and no coverage_id. pap_service 01d813c6 has delivery_purpose `self_pay_delivery`. pap_billing 7f3c2a91 is a `pap_purchase_sale` with NU, sale_amount 899.00 and fee_amount 49.00. Those amounts equal the Auto-Adjusting class's `self_pay_retail_price` 899.00 and `self_pay_delivery_fee` 49.00. The transaction date is 2021-08-30 (the order date: "paid in full when the order is placed") and service_from is the 2021-09-14 delivery. This is the transition order_received→patient_owned "A self-pay device is delivered; title passes to the patient on delivery".
- **The repairs match pap_repair_responsibility.** The rule says "an owned self-pay device is repaired at the patient's cost (repair_coverage patient_paid)". All three are outside the 24-month warranty from the 2021-09-14 setup, and each patient share equals labor units × `repair_labor_rate_per_unit` 23.86 + parts:
  - 23.86 + 37.34 = 61.20
  - 23.86 + 51.04 = 74.90
  - 2 × 23.86 + 50.68 = 98.40

  Each is below the replace threshold (100% of 862.40), and `loaner_issued` = true matches `loaner_during_owned_repair` true.
- **The coverage charges match the PAP trigger.** The pap_repair trigger posts coverage_patient_charge with responsibility_type repair_patient_share, source_bill_id = pap_service_id and posting_date = service_date. The three ledger charges (35047fc7, e227947c, 3318422e) match this. pap_purchase_sale has no coverage trigger, so a 2021 self_pay coverage charge is not required.
- **The persona was updated:** "the CPAP is your own — you bought it outright with your own money back in 2021 — so its repairs are billed to you". That line is a passive answer that duplicates DB facts. The clause "so its repairs are billed to you" is the customer's own lay account of a billing fact, not a policy judgement the agent needs. Observation only.
- **S2-1: closed.**

The other cross-category rows were re-checked the same way:
- **Task 0, mobility.** K0823 fee 402.48 / 301.86 × Commercial PPO allowed 112% gives 450.78 / 338.08. Modifiers are KH, KI ×2 and KJ. The cost-share split (deductible 1500, then 20%) gives 450.78 ×3, 147.66 + 38.08, then 67.62. Payer paid is 152.34 and 270.46. Every row is producible.
- **Task 1, oxygen.** Medicare 100% × (172.61 + 28.43) = 201.04. Month 16 (DOS 09-09, after the rx of 08-25 raised the flow to 4.5) is QF at max(258.915, 201.04) = 258.92. The 2026 deductible splits are 201.04, then 81.96 + 23.82. Every row is producible.

Observations (no bearing on any scored value):
- **O5-1.** Task 0's mobility rental runs under Commercial PPO (prior_auth_pmd_required true), but no mobility_requests row is seeded. That is an absence, not a contradiction, and nothing reads it.
- **O5-2.** Task 1's coverage ledger has a 2026-01-01 `coverage_oop_reset` but no `coverage_deductible_reset`, while the 2025 oxygen months carry coinsurance only (the deductible was already met). Base coverage_accumulators resets both. This is a coverage-own row (present since round 1), and neither the crossover nor the revision reads deductible accumulators.

### closing_checklist (round 5)
- **Verdicts.** The per-task files map one-to-one to the tasks, and revisions 1-5 are kept in place. Both round-5 comparisons carry **PASS** on all four relationships.
- **Scope, tools, tree bounds, factor bounds and independence, overwrite reach:** unchanged from `§revision_4` (charter and tool hashes are identical).
- **S2-1:** closed. Every cross-category seeded row in both tasks is a state its owning charter produces: PAP self-pay sale and patient-paid repairs; mobility rental months; oxygen months including QF.
- **Gates (9, including traceability):** all green, re-run by the auditor.
- **Open observations:** N4-1, N4-2, N4-3, O5-1, O5-2, F-3, F-4, O-7, and the base-text log items. None has a demonstrated consequence on either world.

**Difficulty result (round 5): passes the source-layer audit.**
