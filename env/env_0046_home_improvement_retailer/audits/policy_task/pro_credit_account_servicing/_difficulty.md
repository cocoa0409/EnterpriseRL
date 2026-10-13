# Policy-task audit — pro_credit_account_servicing / charter-global

## charter_global_frozen

- auditor: erl-task-policy-audit subagent (independent of the instantiating agent), round 1
- freeze time: 2026-10-08T07:10Z (written before any task's derivation and before any GT reveal)
- frozen inputs (sha256, re-verified at audit start, equal to the brief):
  - `tasks/pro_credit_account_servicing/trade.extended.yaml` 6a954eb2d5d710a2730ecfa3509fc903e8f1908615143181048071f520652732
  - `tasks/pro_credit_account_servicing/task_tools.py` 52c1f08ded3f6642f740c215a99f174cfccbb5b3e918dae92065a2b192e89628
  - masked views `/tmp/e46/views/pro_credit_account_servicing/task_0.blind.json` 463ed6f8… and `task_1.blind.json` 58b2797c… (they hold only frozen_time, user_scenario and initial_state)
- read so far: blueprint/products/trade.yaml (base copy), blueprint/products/pro.yaml (only its variants' `dedicated_account_rep` and the pro_spend_* event definitions), blueprint/db_schema.json (enums of trade_requests / trade_accounts), blueprint/share_tools.py (list of tools only), the extended charter, task_tools.py, skills/erl-task-instantiate/scripts/check_compute.py (the semantics of MONTHS/DAYS/LATEST/COUNT within_months/CFIELD/CPARAM/XSUM).
- masked and not read: tasks/0.json and tasks/1.json in their entirety (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure). I ran no recursive search over tasks/.
- entry conditions: the brief's gate snapshot gives every gate's last line: EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; CACHE-DIFF INFO; TRACEABILITY NOT OK, which the brief says is expected until docs/ are rendered. I cite these lines and did not re-run the gates.

Policies (P-ids used in every file of this audit):

| P | id | target_tool (owner) | computes | prerequisite |
|---|---|---|---|---|
| P1 | trade_ext_dispute_settlement_credit | post_dispute_credit_3cc5c337 (agent) | credit_amount | [] |
| P2 | trade_ext_statement_late_charge | assess_late_payment_charge_c9e93ff5 (agent) | charge_amount | [] |
| P3 | trade_ext_phone_payoff | submit_payoff_payment_22b2623b (user) | payment_amount | P2 value_input (fees), P1 value_input (dispute_credits) |
| P4 | trade_ext_credit_line_sizing | decide_credit_line_increase_746194e9 (agent) | new_credit_limit | P3 state_gate |
| P5 | trade_ext_late_fee_rerating | reverse_late_fee_excess_4d4f7d34 (agent) | reversal_amount | [] |
| P6 | trade_ext_statement_minimum_payment | submit_minimum_payment_92c17bdd (user) | payment_amount | P5 value_input (reversals_since) |

### policy_conflict_scan

- **Base copy**: every top-level key of the extended file except `extended_policies` compares equal (python `==` on the parsed YAML) to `blueprint/products/trade.yaml`, so the base section is verbatim.
- **Subjects / triggers**: P3 and P6 both write `trade_payment_received`, but their triggers are disjoint by account type: P3 covers "a business holding a pay-in-full commercial account", while P6 covers "a business holding a revolving Pro Credit account". P1, P2, P4 and P5 write distinct event types (dispute credit, fee_assessed late_payment_charge, credit_limit_changed, fee_reversed). P2 is limited to pay-in-full accounts and P5 to revolving accounts, so the two never meet on one account.
- **Eligibility / time anchors**: every extended policy anchors its clock to "the date the charge/credit/payment/decision is made" (= frozen date), and every month window is counted back in whole calendar months. This is consistent with base `trade_credit_line_increase` and with the compute engine (`0 <= MONTHS(d, NOW) < N`).
- **Cross-category read boundary**: all six read only the `pro` category (pro_memberships holding: variant_name, status, enrolled_date, the variant parameter dedicated_account_rep; pro_activity spend posted/reversed). Each `cross_category` block declares what it reads.
- **Interacting writes inside one tree**: P2's late payment charge raises the count of late payment charges that P3 (repeat-lateness loading) and P4 (late-charge share) read. P1's credit is read by P3 only. P5's reversal is read by P6 only. None of the depended-on writes reads the others' results, so parallel edges P1 and P2 under P3 commute (see prerequisite_graph).
- **Claimed scope** (inferred from the policy graph and the two personas; charter_scope is masked and will be compared after the reveal): the tree {P4 ← P3 ← (P2, P1)} has a commercial-account root, and the tree {P6 ← P5} has a revolving-account root. Together they cover all six extended policies and do not overlap.

### rule_compute_equivalence

I swept each policy sentence by sentence against its `compute_basis` and `compute`. The restricted-expression semantics come from `check_compute.py` (`LATEST` = the row with the maximal date_field string; `COUNT/SUM within_months=N` = rows with `0 <= MONTHS(date, NOW) < N`; `MONTHS` = whole months with day-of-month borrow).

- **P1**: every tier of tax_back, clock_days, goodwill_rate, protection_rate, handling_credit and first_dispute_rate is a rule sentence and a branch of the binding. tax_back's else-branch (`disputed*inv_tax/inv_total if inv_tax>0`) covers every category other than wrong_price/wrong_quantity. db_schema's `dispute_category` enum is {wrong_price, wrong_quantity, not_received, unauthorized_buyer, not_applicable}, and an approved invoice_dispute carries one of the first four, so the else-branch is exactly "not received or unauthorized buyer". In clock tier 2, "runs from the day after the filing date" maps to `DAYS(filed_on, approved_on) - 1`, which is equivalent. Rounding is once on the total. PASS.
- **P2**: every factor tier is in both faces. **Gap (F-1)**: the rule's first sentence makes a late payment charge "owed for every closed statement that shows a past-due amount … one is charged per statement period". It sets every quantity per statement ("the statement's past-due amount", "the statement's days past due"). Yet every statement-level binding of `compute` (`stmt_pd`, `stmt_date`, `stmt_dpd`) is `LATEST(... event_type='trade_statement_issued')`. So compute can price only the latest statement, while the rule (and P3's prerequisite condition "Every trade_statement_issued row … with a past_due_amount above zero is referenced …") ranges over every statement. The rule therefore promises charges that compute cannot produce whenever an earlier statement with a past-due amount has no charge. Whether this has a consequence depends on the world; it is demonstrated per task.
- **P3**: ledger_balance lists exactly the in/out event types of the rule sentence. accrued_days maps tier 1 to `-grace`, tier 2 to `-1` and tier 3 to `-0`, each MX(0, ·). year_fraction maps "half-month periods begun" to `int((d+14)/15)/24` = ceil(d/15)/24. tolerance, regular_cut and repeat_load match. PASS.
- **P4**: count_window maps "every whole calendar month since the account was opened, including the current month" to `opened_months + 1` under the engine's `< N` window, which is equivalent. stepped_line maps floor-to-increment, limited_line is MN of three, and result keeps the current line when not above. PASS. Observation O-2 below concerns the base relationship cap.
- **P5**: all tiers match. **Same scope gap as F-1, in observation form (O-4)**: P6's prerequisite sentence speaks of "every late fee standing on the account above its re-rated amount", but P5's `fee_posted` is `LATEST(... fee_type='late_fee')`, so compute prices only the latest late fee. This bears on a task only where an earlier late fee also stands above its re-rated amount (checked per task).
- **P6**: all tiers match. Minor: the rule defines "entries posted since the statement date" as entries "that carry a later statement period than the latest statement", but compute sums only entries whose `statement_period == open_period` (the period of the single latest-dated entry), guarded by `open_period > stmt_period`. The two agree whenever at most one later period exists. Observation O-5, with no consequence unless a world has two later periods.

### action_binding_and_uuids

- (target_tool, computes) pairs: there are six distinct tools, each claimed by exactly one policy. Every docstring describes only its own atomic write. None names another tool. The words "then", "after" and "once" appear only inside a tool's own effect ("The charge then shows in the account's activity", "the account balance after the charge"), never as a cross-tool order (I grepped task_tools.py for before/after/first/then/prior/until/once).
- No tool validates eligibility, prerequisites or amounts. Every body is find → create/update, landing the given value (module docstring and bodies, task_tools.py lines 38-55, 82-97, 121-136, 160-169, 194-209, 233-248). The tool layer therefore judges no prerequisite.
- uuid8s: 3cc5c337, c9e93ff5, 22b2623b, 746194e9, 4d4f7d34, 92c17bdd. All are pairwise distinct, share no prefix or suffix, and show no sequence. PASS.
- Observation O-6: submit_payoff_payment_22b2623b and submit_minimum_payment_92c17bdd have identical runtime effects (one trade_payment_received row, phone_ach, held on account). Their business readings are distinguished only by the docstring ("commercial account" vs "revolving account") and by P3's and P6's account-type triggers. That separation is sufficient (see prerequisite_sentences E1).

### prerequisite_graph

- `prerequisite` is filled on all six (P1, P2, P5 `[]`). Every `problem` is an extended policy id of this file. None points at a base policy or at itself. Edges: P4→P3, P3→P2, P3→P1, P6→P5. The graph is acyclic.
- Every `policy_source` is locatable verbatim in the blocked policy's own rule. E1 is P4 rule sentence 2, E2 is P3 rule sentence 3, E3 is P3 rule sentence 4 and E4 is P6 rule sentence 3.
- All four edges are `form: state` with no `fallback_reason`, which is consistent.
- `kind`/`gate`: E2 gate `fees` and E3 gate `dispute_credits` are bindings of P3 compute, and E4 gate `reversals_since` is a binding of P6 compute, so the value_input kinds are honest. E1 is `state_gate` with gate `trade_transactions.amount`. P4 has no eligibility block, and the gate is the rule sentence itself. That is acceptable but does not point at a structured gate (observation O-7).
- `resolved_by` equals the depended-on policy's target_tool on all four edges. Effects: P2's write enters `fees` and `late_charges_12`. P1's write enters `dispute_credits`. P3's payment line is a trade_payment_received row dated today, after the latest statement. P5's reversal lands with statement_period = today's YYYY-MM, which `reversals_since` reads only when today's period is later than the latest statement's period. That is a world fact, checked per task.
- Conditions restate their sentences at the same strength (E2 "every … statement … with past_due_amount above zero", E3 "every … approved", E4 "every late_fee … whose amount exceeds its re-rated late fee"). No authoring-viewpoint phrasing appears.

### prerequisite_sentences

| edge | sentence (verbatim) | connective | form test | names no tool/id |
|---|---|---|---|---|
| E1 P4←P3 | "A new credit line is not decided until the ledger shows a payment credited after the latest statement date that at least equals that statement's past-due amount." | not … until | record-visible state (payment row date/amount vs statement row) | yes |
| E2 P3←P2 | "The payoff figure is fixed only after the ledger carries a late payment charge for every closed statement that showed a past-due amount." | only after | record-visible state (fee row per statement period) | yes |
| E3 P3←P1 | "The payoff figure is not fixed until every invoice dispute standing approved on the account has its dispute credit on the ledger." | not … until | record-visible state (dispute credit row per approved request) | yes |
| E4 P6←P5 | "The minimum-satisfying payment is fixed only after every late fee standing on the account above its re-rated amount carries a correction entry on the ledger." | only after | record-visible state (fee_reversed row per late fee); "above its re-rated amount" points the reader at P5's rule | yes |

The hop each sentence leads to (sentence + records + depended-on rule → resolving write):

- **E1**: "a payment credited" on a commercial account. The only payment policies are P3 (pay-in-full commercial) and P6 (revolving). On a pay-in-full account only P3's rule, "asks to pay the account off in full by phone … one debit … for the payoff figure", produces a payment row, and the payoff figure ≥ ledger balance ≥ the latest past-due amount. On a revolving account the hop would resolve to P6. So the hop is unique per account type. Observation O-6 records that two tools could mechanically bring the state about, separated only by the account-type triggers.
- **E2**: "a late payment charge for every closed statement …" resolves to P2 (the only policy whose rule writes a late payment charge). There is a single reading, and it ranges over **every** closed statement with past_due_amount > 0. Combined with F-1, a world with more than one uncharged past-due statement needs several P2 writes, and compute can price only one of them (demonstrated per task).
- **E3**: "dispute credit" resolves to P1, with a single reading.
- **E4**: "a correction entry" on a late fee above its "re-rated amount" resolves to P5 (its rule carries "re-rated late fee" and "one correction entry referencing that late fee"). A courtesy waiver (base trade_evt_courtesy_waiver) is a waiver, not a correction entry, and base text says "When the charge is owed a correction … the correction applies instead". So there is a single reading.

No rule restates another's prerequisite sentence: P1, P2 and P5 rules do not mention payoff, line increase or minimum payment, and P3 does not mention the line increase. I found no undeclared cross-problem order in any extended rule. The base rule sentences that order things, such as trade_evt_courtesy_waiver's "the correction applies instead", ground no edge of these trees.

### override_declarations

Each base_policy_refs entry was checked sentence by sentence.

- **P1 vs trade_evt_invoice_dispute**: sentences S1-S4 (filing, window, counting, resolution/past-due exclusion), S6 (quote-price decisions) and S7 (one credit per invoice) are followed or inherited. In S5, "it credits the disputed amount against the invoice …" is superseded and declared. PASS.
- **P2 vs trade_evt_late_charges**: S2 (pay-in-full charge amount *and trigger*, through `trade_msr_past_due_invoice_balance`, which carries late_charge_grace_days) is superseded and declared. Note that this drops the grace-day exclusion from the **trigger**: the new trigger is the statement's own `past_due_amount`. S3 (references, period), S4 (one per period) and S5 (dispute exclusion) are inherited. vs trade_evt_payment_application / trade_evt_returned_payment: nothing in them is altered (they supply only the payment and return counts). PASS on declarations; the consequence of the widened trigger is world-dependent (see the task files).
- **P3 vs trade_evt_payment_application**: S3 (authorization) and S6 (one row per invoice) are superseded and declared. S1 (cutoff), S2 (methods: phone_ach is accepted on all four commercial tiers), S4 (payable statuses) and S7 (surcharge, not bank card) are inherited. **S5 ("A payment is applied first to the invoices the business names … the oldest past-due invoice first … whatever remains … is held on account") is not named**, yet P3 says the payoff is "held on account … applied … on the next statement". This is an undeclared override (O-1). It is not scored: the tool takes no invoice argument and fixes `applied_invoice_number=""`, so no second reading changes a scored value. Recorded as an observation.
- **P4 vs trade_credit_line_increase**: S6 (negative history) and S8 (new-line formula) are superseded and declared. S1-S5 (request, active, tenure, cooldown, month counting) and S7 (financials threshold) are inherited. vs trade_agg_relationship: S2's exposure cap ("an approval or increase that would exceed it is reduced to the cap minus trade_msr_other_open_credit_limits …") is **not named**, while the replaced S8 drops "the headroom under trade_agg_relationship" from the "lowest of" list. The cap therefore remains in force as an inherited limit. It binds only where the business holds other open lines totalling close to 1,250,000 (O-2, checked per task).
- **P5 vs trade_evt_fee_correction**: S1 (full reversal) is superseded and declared. S2 enumerates the posting_error cases, and P5 adds a new posting_error case (the excess over the re-rated fee) without naming S2 (O-3). The tool hard-codes posting_error, so this is not scored. S3 (owed regardless of tier, waiver history or age) and S4 (no second reversal) are inherited. vs trade_evt_late_charges: S1 (the revolving late fee amount) is superseded and declared, while P5 sentence 1 restates its trigger verbatim in business words. PASS.
- **P6 vs trade_evt_payment_application**: S3 and S6 are superseded and declared, and S5 is undeclared as for P3 (O-1, not scored). vs trade_evt_invoicing: S6 (the revolving minimum formula) is superseded and declared, and the rest is inherited. PASS.

### factor_ladders

| P | factor | label | decides | tiers (fall-through last) | fall-through = baseline | cross_difficulty | multi-source |
|---|---|---|---|---|---|---|---|
| P1 | dispute_tax_add_back | method | tax_back | ×tax/merch; ×tax/total; 0 | yes (0) | – | yes (invoice row + request category) |
| P1 | dispute_resolution_clock | method | clock_days | from invoice date; from day after filing; from filing | yes | – | yes (request dates + account opened_date) |
| P1 | slow_resolution_goodwill | parameter | goodwill_rate | 0.10; 0.05; 0 | yes | pro | yes (request dates + pro membership) |
| P1 | dispute_price_protection | parameter | protection_rate | 10; 5; 0 | yes | – | yes (invoice pricing_basis + request category) |
| P1 | dispute_handling_credit | parameter | handling_credit | 75; 40; 0 | yes | – | yes (request amount + opened_date) |
| P1 | first_dispute_courtesy | parameter | first_dispute_rate | 2; 1; 0 | yes | (reads pro, declared null — O-8) | yes |
| P2 | late_charge_standing_reduction | parameter | standing_cut | 0.50; 0.25; 0 | yes | pro | yes |
| P2 | late_charge_volume_reduction | parameter | volume_cut | 0.10; 0.05; 0 | yes | pro | yes |
| P2 | late_charge_dispute_relief | parameter | dispute_relief | 0.25; 0.10; 0 | yes | (reads pro tier, null) | yes |
| P2 | late_charge_small_balance_allowance | parameter | allowance | 1000; 500; 0 | yes | – | yes (returns + payment lines) |
| P2 | late_charge_month_share | method | month_share | days_counted/30; 0.5; 1 | yes | – | yes (statement dpd + account tier) |
| P2 | late_charge_days_counted | method | days_counted | dpd−grace; dpd−⌊grace/2⌋; dpd | yes | pro | yes |
| P3 | payoff_regular_payer_reduction | parameter | regular_cut | 0.50; 0.25; 0 | yes | – | yes |
| P3 | payoff_repeat_lateness_loading | parameter | repeat_load | 0.25; 0.10; 0 | yes | – | yes |
| P3 | payoff_accrual_start | method | accrued_days | days−grace; days−1; days | yes | – | yes |
| P3 | payoff_accrual_day_count | method | year_fraction | d/365 (Net45/60); ceil(d/15)/24 (Net30/Select); d/360 (other) | yes | – | no (tier only) |
| P3 | payoff_accrual_tolerance | parameter | tolerance | 40; 20; 0 | yes | pro | yes |
| P4 | line_increase_percentage | parameter | increase_pct | max+10; max+5; max | yes | pro | yes |
| P4 | line_late_charge_share | parameter | late_charge_share | 0.80; 0.50; 1 | yes | – | no (count only) |
| P4 | line_late_charge_window | method | count_window | 6; opened_months+1; 12 | yes | pro | yes |
| P4 | line_seasoning_points | parameter | seasoning_points | 5; 2.5; 0 | yes | pro | yes |
| P4 | line_guarantee_share | parameter | guarantee_share | 1.10; 1.05; 1 | yes | – | yes |
| P4 | line_usage_multiplier | parameter | usage_multiplier | 1.15; 1.05; 1 | yes | – | yes |
| P5 | late_fee_schedule | parameter | scheduled_fee | 25; 32; tier fee | yes | – | yes |
| P5 | late_fee_repeat_window | method | repeat_window | 6; 12; 24 months | yes | pro | yes |
| P5 | late_fee_member_reduction | parameter | member_cut | 5; 2; 0 | yes | pro | yes |
| P5 | late_fee_tenure_reduction | parameter | tenure_cut | 4; 2; 0 | yes | – | yes |
| P5 | late_fee_lateness_share | parameter | lateness_share | 0.50; 0.75; 1 | yes | – | yes |
| P6 | minimum_preferred_percentage | parameter | minimum_pct | pct−1.00; pct−0.50; pct | yes | pro | yes |
| P6 | minimum_preferred_floor | parameter | minimum_floor | 25; 35; tier floor | yes | – | yes |
| P6 | minimum_selection | method | minimum_used | MN(recomputed, printed); recomputed; printed | yes | – | yes |
| P6 | minimum_netted_credits | method | netted_credits | all credit kinds; reversals+waivers; nothing | yes | – | yes |

Structure checks:
- Counts as declared: P1 6 (4 param / 2 method), P2 6 (4/2), P3 5 (3/2), P4 6 (5/1), P5 5 (4/1), P6 4 (2/2). Bindings within each policy are disjoint, and no `decides` is `result`.
- Every tier of every ladder is a rule sentence with its condition and value or method, and a branch of its `decides` binding. Within each ladder no two tiers select the same value or method. Each baseline.rule is a verbatim rule sentence (P3 and P4 use two), and their default keys match `baseline.params`.
- **Labels that fail the honesty test (F-2, SOURCE-FACTOR)**: two factors labelled `method` only substitute a different number into the same unchanged formula.
  - P5 `late_fee_repeat_window`: compute `other_fees = COUNT('trade_transactions', within_months=repeat_window, … fee_type='late_fee') - 1` with `repeat_window ∈ {K('repeat_window_member_months')=6, K('repeat_window_standard_months')=12, K('repeat_window_newer_months')=24}`. The tiers pick a lookback length, which is a threshold number, while the counting rule stays the same.
  - P4 `line_late_charge_window`: compute `late_charges_window = COUNT(…, within_months=count_window, … fee_type='late_payment_charge')` with `count_window ∈ {6, opened_months + 1, P('cli_clean_history_months')=12}`. Again only a lookback length changes. The middle tier's length is derived from the opening date but still enters the unchanged COUNT as a number.
  - Each is its policy's **only** `method` factor. With the label struck, P4 and P5 each carry 0 honest `method` factors, below the floor of 1. The consequence falls on the task that claims P4 (task 0) and the task that claims P5 (task 1).
- **Borderline labels kept as observations (O-9)**: P2 `late_charge_days_counted` (dpd − x, x ∈ {grace, ⌊grace/2⌋, 0}) and P3 `payoff_accrual_start` (days − x, x ∈ {grace, 1, 0}) are also number substitutions in form. Their rule text, however, frames them as the start anchor of a day count, an interval-counting convention that lending treats as methodology. Each of these policies also has another clearly honest method (P2 month_share proration vs flat share; P3 half-month-periods vs actual/365 vs actual/360). I record them as observations, not REDs.
- **Dead fall-through (F-3, SOURCE-FACTOR)**: P3 `payoff_accrual_day_count`. P3's rule restricts the payoff to "a business holding a pay-in-full commercial account". In the base variants, the pay-in-full tiers (revolving_balance_allowed false) are exactly Commercial Account Net 30, Net 30 Select, Net 45 and Net 60 Enterprise. The ladder's first two tiers name exactly these four ("on a Commercial Account Net 45 or Net 60 Enterprise …; on a Commercial Account Net 30 or Net 30 Select …"). The fall-through "on any other tier it is the accrued days divided by 360", which is also the baseline method, is reachable only by a Pro Revolving Charge / Plus account, and no such account can reach this write. So the ladder has two live tiers, not three, and its fall-through/baseline is a treatment the business gives no customer of this write. The baseline itself stays computable: a reader of the baseline sentence gets a definite number. The defect is the ladder's realness. The consequence falls on the task that claims P3 (task 0).
- Realness of the other conditions and outcomes: every remaining condition divides the customers who reach the write (membership tier, spend, tenure, guarantee, returned payments, days past due, dispute state). None is a scope restatement. The outcomes are plausible business treatments for a trade-credit program: loyalty or tenure rate cuts, small-balance allowances, proration, guarantee- and usage-scaled line increases, first-time and second-time late fee schedules. Observation O-10: P4's middle count-window tier makes an account open ≥ 24 months without a dedicated rep count late charges over its entire life, a longer lookback than the 12 months a younger account gets. This is unusual but not shown impossible.
- Cross-difficulty factors per policy (all read `pro`): P1 1, P2 3, P3 1, P4 3, P5 2, P6 1. Whether each task's tree carries ≥1 multi-source factor and ≥1 cross-difficulty factor, and whether each bears weight, is decided in that task's `factor_weight`.

### findings

- **F-1 (SOURCE-POLICY; bears on the task that claims P2+P3 = task 0)**. Symptom: P2's rule and P3's prerequisite E2 oblige a late payment charge on **every** closed statement with a past-due amount, but P2's compute prices only the latest statement. Root cause: `stmt_pd`, `stmt_date` and `stmt_dpd` are `LATEST(...)` bindings, while rule sentence 1 reads "a late payment charge is owed for every closed statement that shows a past-due amount". Evidence: trade.extended.yaml P2 rule line 1689 and compute lines 1708-1709 and 1726; P3 prerequisite condition lines 1914-1915. The widened trigger (the base's grace-day-filtered measure was superseded by the statement's own past_due_amount) makes earlier statements that the base had correctly left uncharged newly owed. The consequence is demonstrated in task 0's file.
- **F-2 (SOURCE-FACTOR; task 0 via P4, task 1 via P5)**: mislabelled `method` factors that only substitute a lookback length. This leaves P4 and P5 with 0 honest method factors. Evidence is in factor_ladders above.
- **F-3 (SOURCE-FACTOR; task 0 via P3)**: P3 `payoff_accrual_day_count` has a dead fall-through/baseline tier that no customer reaching this write can occupy. Evidence is in factor_ladders above.
- Observations (not grounds for rework unless a task file demonstrates a consequence):
  - O-1: base payment_application S5 (application order) is overridden by P3 and P6 without being named. Not scored.
  - O-2: base trade_agg_relationship's exposure cap is not named and remains in force for P4. It binds only with other open lines near 1,250,000.
  - O-3: fee_correction S2's posting_error enumeration is extended by P5 without being named. Not scored.
  - O-4: P5 compute prices only the latest late fee while E4 says "every late fee". This matters only if an earlier fee also stands above its re-rated amount.
  - O-5: P6's "later statement period" vs compute's `== open_period`.
  - O-6: two payment tools have identical effects and are separated only by account-type triggers.
  - O-7: E1's `gate` names a field, not a structured gate.
  - O-8: P1 first_dispute_courtesy and P2 dispute_relief read the pro membership tier but declare `cross_difficulty: null`. The label understates.
  - O-9: borderline method labels P2 days_counted and P3 accrual_start.
  - O-10: P4's lifetime count window for older accounts without a rep.

## closing_checklist

Written after both reveals (2026-10-08T07:35Z). It sits below the frozen charter-global section, which was not edited.

- Per-task audit files 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json, alongside this file. This is the first revision.
- Coverage and disjointness: the charter_scope of task 0 is {P1, P2, P3, P4} and of task 1 is {P5, P6}. Together they cover all six extended policies with no overlap. The tools are closed, and every uuid8 is distinct (§ action_binding_and_uuids).
- Trees: task 0 has 3 prerequisite problems, 2 value_input edges and a user write (payoff). Task 1 has 1 prerequisite problem, 1 value_input edge and a user write (root). The difficulty-wide graph is acyclic.
- **Not closed. The difficulty does not pass the source-layer audit:**
  - task 0 is SOURCE-POLICY RED (F-1 consequence), SOURCE-TASK RED (two orders), SOURCE-CHAIN RED (E2 still unmet at the gold payoff) and SOURCE-FACTOR RED (F-2 P4, F-3 P3);
  - task 1 is SOURCE-FACTOR RED (F-2 P5).
- Re-running the instantiation-stage gates on a final form does not apply: the artifacts are unchanged since the coordinator's snapshot, and the audit edits nothing.

## revision_2

### charter_global_frozen (revision 2)

- auditor: erl-task-policy-audit subagent, round 2. Freeze time: 2026-10-08, before reading round-2 tasks/0.json and tasks/1.json.
- inputs: trade.extended.yaml **03a090780994a2aa1663ba9b346972f1bbdc9f61c9a071e5681fc7f93fa94225** (changed from 6a954eb2…, so every charter-global section below is re-derived); task_tools.py 52c1f08d… (unchanged, so § action_binding_and_uuids carries forward by reference to round 1 on that hash); masked views r2/task_0.blind.json 463ed6f8… and r2/task_1.blind.json 58b2797c… (byte-identical to round 1).
- gate snapshot as given by the coordinator: EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; CACHE-DIFF INFO; TRACEABILITY NOT OK, pending the KB.
- The base section is still verbatim (all non-extended keys equal to blueprint/products/trade.yaml).
- **contamination_disclosure**: this auditor read the round-1 GT (round-1 tasks/*.json) during round 1. The round-2 derivations therefore cannot be blind to the round-1 conventions or values. They are re-derived from the round-2 charter and the unchanged masked worlds, and every figure is recomputed, not copied. The round-1 blind answers above are left untouched.

### What changed (round-1 text vs round-2 text)

| P | change |
|---|---|
| P1 | first_dispute_courtesy `cross_difficulty: pro` (O-8). Rule unchanged. |
| P2 | rule sentence 1 now: "a late payment charge is owed for the latest closed statement when that statement shows more days past due than the tier's late charge grace days and no late payment charge carries its statement period yet; … a statement whose period already carries a late payment charge, or that shows no more days past due than the grace days, is charged nothing." New bindings: `stmt_period`, `period_charges`, `charge_owed` (`stmt_dpd > P('late_charge_grace_days') and period_charges == 0`) and `relief_tier`. `result` is 0 unless `charge_owed`. dispute_relief is now `cross_difficulty: pro` (O-8). |
| P3 | E2 sentence now: "The payoff figure is fixed only after the latest closed statement, when it shows more days past due than the tier's late charge grace days, carries a late payment charge on the ledger." The condition is restated to match. year_fraction ladder: Net 45/60 → actual/365; **Net 30 Select** → half-month periods begun; **Net 30** (fall-through) → actual/360. Overwrite now also names base payment_application S5 (O-1). |
| P4 | count_window tier 2 is now `K('window_established_months')` = 9 (O-10), and the factor is relabelled `parameter`. **line_guarantee_share is relabelled `method`** and reworked: a new `core_increase` binding (no guarantee term), with `line_increase` = core × 1.10 (PG and ≥ 60 months) / core + 2500.00 flat (PG and < 60 months) / core (no PG). |
| P5 | rule now names "the most recent late fee" (O-4). repeat_window is relabelled `parameter`. **late_fee_lateness_share is relabelled `method`**: PG and dpd ≤ 5 → dpd / `lateness_proration_days` (10); no PG and dpd ≤ 5 → flat 0.75; otherwise 1. |
| P6 | "Entries posted since the statement date are the ledger entries carrying the statement period of the newest ledger entry, when that period is later than the latest statement's period" (O-5, now equal to compute). E4 narrowed to "the most recent late fee". Overwrite also names payment_application S5 (O-1). |

### policy_conflict_scan (revision 2)

The subjects, triggers and read boundaries of round 1 stand. P2's narrowed trigger ("latest closed statement", dpd > grace) and P3's narrowed E2 now cover the same set of statements. Base trade_evt_late_charges S2 (superseded) was already grace-filtered, so the narrowed trigger is closer to base, and the declared supersession still covers it. Claimed scopes are unchanged in shape (to be re-compared after the reveal).

### rule_compute_equivalence (revision 2)

- I scripted the check: every compute binding of every policy has a `compute_basis` entry quoted verbatim from its rule, every baseline.rule sentence and every `policy_source` is in its rule, **except** P3 `ledger_balance`, which has no `compute_basis` entry.
  - That gap was already present in round 1, and I missed it then. Its sentence ("The account's ledger balance is every invoice … dispute credit on the account") is in the rule and is quoted under `invoices`.
  - No basis is invented, so this is recorded as observation **O-11**.
- **F-1 closed**: P2's rule now prices only the latest statement, under the same condition `charge_owed` implements, and E2's condition speaks of the same statement. The rule promises nothing that compute cannot produce. P5 now says "the most recent late fee", which equals `LATEST` (O-4 closed). P6's definition of "since the statement date" equals `open_period` (O-5 closed).
- P4: the guarantee tiers in the rule ("multiplied by the guarantee share" / "the guarantee addition is added … as a flat amount" / "the core line increase") equal the `line_increase` branches. P5: the lateness tiers equal the `lateness_share` branches. P3: the year_fraction tiers equal the branches (else-branch = Net 30; revolving accounts cannot reach P3).

### action_binding_and_uuids (revision 2)

task_tools.py is unchanged (52c1f08d…), so the round-1 section carries forward. The (target_tool, computes) pairs in the charter are unchanged.

### prerequisite_graph and prerequisite_sentences (revision 2)

- The edges, kinds, gates and resolved_by are unchanged, and the graph is acyclic.
- E2 new sentence: the connective is "only after"; the form is state (a fee row on the latest statement's period, qualified by the record-visible dpd > grace); it names no tool or id; the condition has the same strength. The single resolving write is P2, whose trigger is now exactly this state.
- E4 new sentence: "only after" + state (a correction entry on the most recent late fee); the single resolving write is P5.
- E1 and E3 are unchanged.
- No new cross-problem order appears in any rule.

### override_declarations (revision 2)

- O-1 closed: P3 and P6 now name payment_application S5 in `overwrite`.
- O-2 kept: trade_agg_relationship's cap is not named.
- O-3 kept: the fee_correction S2 posting_error enumeration.
- All other round-1 conclusions stand. The changed P2 text sits inside the already-declared supersession of late_charges S2.

### factor_ladders (revision 2)

- Counts: P1 6 (4 parameter / 2 method), P2 6 (4/2), P3 5 (3/2), P4 6 (5/1), P5 5 (4/1), P6 4 (2/2).
- **F-2 closed.**
  - P4's method is now `line_guarantee_share`. Its tiers choose *how* the guarantee enters (multiply the core increase, add a flat 2500.00, or leave it unchanged). That is a change of algorithm, so the label is honest.
  - P5's method is now `late_fee_lateness_share`. Its tiers choose proration by days late (dpd/10), a flat share (0.75) or the whole fee. Tier 1 is a function of the record, not a constant, so the label is honest.
  - Both lookback-window factors are now labelled `parameter`, which is honest.
  - Each ladder is still distinct. P5 tier 1 ≤ 0.5 because dpd ≤ 5 → dpd/10, which differs from 0.75 and 1. P4: ×1.10 vs +2500 vs none. Conditions are real; fall-through = baseline in both.
- **F-3 closed.** P3 day-count tiers are Net 45/60, Net 30 Select and Net 30. All three are pay-in-full tiers that reach the payoff write, so the fall-through/baseline (actual/360, applied to Net 30) is a live treatment.
- O-8 closed (P1 first_dispute_courtesy and P2 dispute_relief now declare `pro`). O-10 closed (P4 middle window is a fixed 9 months). O-9 kept (P2 days_counted, P3 accrual_start).
- Realness of the new outcomes: a flat guarantee addition for newer guaranteed accounts, and day-based proration of a briefly late fee for guaranteed accounts. Both are plausible business treatments, and neither is a scope restatement.

### findings (revision 2)

- F-1, F-2, F-3: closed on the charter (see above). Each task file demonstrates the closure against its own world.
- Observations:
  - O-1, O-4, O-5, O-8, O-10: closed.
  - O-2, O-3, O-6, O-7, O-9: kept, unchanged.
  - **O-11 (new; pre-existing in round 1)**: P3 `ledger_balance` lacks its own compute_basis entry. Its sentence is in the rule, and no consequence follows.
- No new charter-global RED.

### closing_checklist (revision 2)

Written after both round-2 reveals (2026-10-08T12:06Z).

- 0.md and 1.md each carry revision_2 (frozen re-derivation, then comparison). The round-1 text is preserved above.
- Coverage and disjointness: task 0 {P1, P2, P3, P4} and task 1 {P5, P6}. All six extended policies are covered, with no overlap. The tools are closed, and the uuid8s are unchanged and independent.
- Trees:
  - task 0: 3 prerequisite problems, 2 value_input edges, user write P3;
  - task 1: 1 prerequisite problem, 1 value_input edge, user write P6;
  - the difficulty-wide graph is acyclic.
- Factors:
  - every computation has 4-6 factors with ≥ 2 parameter and ≥ 1 honest method (P1 4/2, P2 4/2, P3 3/2, P4 5/1, P5 4/1, P6 2/2);
  - each task carries multi-source and cross-difficulty (pro) factors with seeded rows;
  - every factor bears weight against an honest baseline, and every baseline-only number differs from gold (task 0: 1840 / 870.22 / 102035.64 / 144000 vs gold; task 1: 0 / 89.86 vs gold).
- Round-1 REDs F-1, F-2 and F-3 (and the dependent SOURCE-TASK / SOURCE-CHAIN on task 0) are closed. No new RED was found and nothing regressed.
- Gates: the coordinator's round-2 snapshot is all green except TRACEABILITY, which is pending the KB render (docs/trade), as in round 1. The audit itself edits nothing.
- **The difficulty passes the source-layer audit in revision 2. Both tasks PASS.**
- Open observations, none of them a ground for rework: O-2, O-3, O-6, O-7, O-9, O-11.
