# Policy-task audit — preowned_repossession_recovery / charter-global

## charter_global_frozen

- Round: 1 (first audit of this difficulty; no earlier revision exists).
- Freeze time: 2026-10-15T20:24Z. Auditor: independent erl-task-policy-audit agent. It did not write any audited artifact.
- Frozen inputs (sha256 prefixes, matching the coordinator brief):
  - `tasks/preowned_repossession_recovery/preowned.extended.yaml`: 55fb44b63da012c4
  - `tasks/preowned_repossession_recovery/task_tools.py`: e9810ad98a9094ae
  - masked views `.audit_views/policy/preowned_repossession_recovery/0.json`: 222ace00f04e8414, and `1.json`: 9b4e4da4cf21036b
- Read for this section: blueprint/ (blueprint.yaml, db_schema.json, share_tools.py, products/preowned.yaml, and the lease/retail charters for cross-category seed realism), the extended charter, task_tools.py, the gate snapshot, and the erlbench DSL evaluator (skills/erl-task-instantiate/scripts/check_compute.py, for DAYS/MONTHS/RND/CFIELD/LATEST semantics).
- Masked and unread when this section was written: everything in tasks/*.json except frozen_time, user_scenario and initial_state (so no evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract or prerequisite_closure); worklog.md; the scenario-level worklog.md. Nothing here derives from a revealed GT.
- Entry conditions: the gate snapshot came with the brief (snapshot_r1.txt). check_extended, check_task_tools, replay --check, check_solvability, check_compute, check_grounding and check_cross_fire are OK. The only traceability miss is the unlock tool-name provenance, and validate_scenario reports `documents: 0`. Both are expected before render. Masked views and hashes were supplied and verified. The entry conditions are complete.
- Base copy: every top-level key of the extended file except `extended_policies` is identical to `blueprint/products/preowned.yaml` (parsed comparison: category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures and policies all equal).

### policy_conflict_scan

The charter has seven extended policies, each with one target tool and one claimed `(target_tool, computes)`:

| id | trigger | target_tool | computes | prerequisite |
|---|---|---|---|---|
| ext_recovery_transport_charge | state_due | book_recovery_transport_6b5d55b7 (agent) | amount | [] |
| ext_deficiency_quote | on_request | quote_deficiency_balance_4c162eac (agent) | amount | transport (value_input) |
| ext_deficiency_settlement | on_request | remit_deficiency_settlement_2e6b8900 (user) | amount | deficiency_quote (value_input) |
| ext_release_storage_charge | on_request | bill_lot_storage_d761f3de (agent) | amount | [] |
| ext_redemption_quote | state_due | quote_redemption_amount_aa560e9a (agent) | amount | release_storage (value_input) |
| ext_sale_notice_schedule | state_due | mail_sale_notice_3d21c42f (agent) | days_to_sale | redemption_quote (state_gate) |
| ext_reinstatement_funds | on_request | remit_reinstatement_funds_62601f54 (user) | amount | release_storage (value_input), sale_notice (state_gate) |

Scope partition across the two tasks, read from the masked views alone (the claimed `charter_scope` is masked):
- Task 0 (Tier 4, deficiency): settlement ← deficiency quote ← transport.
- Task 1 (Tier 2, repossessed): reinstatement ← {release storage, sale notice ← redemption quote ← release storage}.

The scopes are disjoint and together cover all seven extended policies. The partition will be confirmed against `charter_scope` at the reveal.

Overlap scan over subjects, triggers, time anchors, terminal states and cross-category reads:
- Three policies price storage: base storage when the vehicle leaves the lot, release storage when the customer asks to get the vehicle back, and the deficiency storage credit. Each declares that it carves itself out of the others ("only for such storage"). The carve-outs are consistent.
- Two policies price payoff quotes (deficiency and redemption) against the base payoff formula. Each declares it, and they carve each other out.
- **Conflicts found:** P-1 (state_due chain bottoming out in an on_request leaf), P-2 (a gate requiring a charge the schedule prices at $0), P-3 (when the transport charge is booked, read two ways by the charter's own consumers), and P-4 (collectability of returned-payment and extension fees during a state reinstatement period). See findings.
- Cross-category read boundaries:
  - The deficiency quote and the settlement read `lease` (status, days_past_due, payments_made_count).
  - The sale notice and the reinstatement read `retail` (status, days_past_due).
  - All four reads are declared in `cross_category` and implemented with `CFIELD(..., status='active')`. See F-3 for the first-match defect.

### rule_compute_equivalence

Mechanical sweep: every `compute_basis` quotation, every `policy_source`, every `replaced_by`, and every `baseline.rule` is a verbatim substring of its own policy's `rule` (whitespace-normalised). Every `superseded_clause` is verbatim in the cited base rule. No misses.

Back-sweep, one sentence at a time, for each policy:

**Transport charge.**
- `search_days` ("calendar days from the assignment date to the repossession date"; with no assignment date, 0): DAYS(assigned, repo), else 0. Matches.
- `per_leg_rate`: the strict `>` thresholds for skip-trace and extended-search match the rule's "more than … no more than".
- `chargeable_legs` 2/0/1 matches.
- `agency_fees_posted` counts only `fee_type='repossession_agency_fee'`, which matches "counted from the repossession agency fees posted".
- Repeat surcharge: ≥3 → third, ==2 → second, else 0. Matches.
- `recovery_weekday = DAYS('2024-01-07', d) % 7`: 2024-01-07 was a Sunday, so 0 = Sunday and 6 = Saturday. Matches.
- `result`: per-leg amounts are added before multiplying by legs, the per-recovery amount is added after, and the total is rounded once. Matches.
- No empty promise.

**Deficiency quote.**
- `pre_sale_days` = DAYS(interest-paid-to, sale) covers "the day after the interest-paid-to date … up to and including the sale date". Matches.
- `post_sale_end_days`: 0 for voluntary; 60 for involuntary when DAYS(sale, NOW) ≥ 60; otherwise DAYS(sale, NOW) + validity. Matches.
- `post_sale_rate` long/short/contract: matches.
- `interest_free_days`: when the notice is more than 3 days after the sale, DAYS(sale, notice); with no notice, DAYS(sale, NOW) + validity; otherwise 0. Matches, given the reading "days after the sale" (see O-6 on wording).
- Disposition credit: MX(0, expenses − RND(share × gross)). Matches for the voluntary and low-value tiers.
- **Fall-through gap (observation O-1):** at 100 % the compute credits MX(0, expenses − gross) whenever auction expenses exceed the gross price, while the rule says "nothing is credited". The fall-through is reached only by an involuntary sale at or above $15,000 (or a sale on a contract with `repossession_type='none'`), so expenses above the gross price are not realistically reachable. Recorded as an observation.
- Storage cap three-tier: matches, including "no notice of intent to sell or no storage charge on record" (both give no credit).

**Settlement.**
- `quote_amount` = LATEST customer_payoff quote. Matches "a payoff quote issued to the customer, and a quote produced for a redemption or for a third party is not one".
- `age_pct` against DAYS(scheduled_sale_date, NOW), `history_points`, `relationship_points` and `size_points` all match their tiers.
- `settlement_base` / `outside_base_part`: the three methods match.
- Floor at the minimum percentage: matches.

**Release storage.**
- `free_days` 0/7/tier, `stored_days` (lot-arrival anchor / repossession date inclusive / day after), `daily_rate` (12/15/tier fee, each "while within a recorded state period", where the compute's `> 0` is the meaning of "recorded"), and oversize (`'HD'`/`'Van'` in the model, age as whole years from January 1 by MONTHS//12): all match.

**Redemption quote.**
- `interest_days` three anchors, reconditioning 350/200/0, projected lot storage at the tier daily fee, and excluded fees (12-month SUM of returned-payment fees, plus extension fees for the longer period; the extension event's `amount` is the extension fee per the events section): all match.

**Sale notice.**
- `notice_period_days` = MX(company, state) + 1, and the reinstatement anchor uses DAYS(NOW, repo) + period + 1. Both match.
- Established, relationship, heavy-preparation and transfer days: match.
- `result` = MX(standard, anchor) + added days. Matches "anchors compared before any days are added".

**Reinstatement funds.**
- Pay-ahead reads `F('days_past_due')`. Matches "at the last nightly cycle", and the schema defines the field that way.
- Relationship reserve, Friday/Saturday weekend storage with `MX(1, service_days)`, and the 12-month returned-payment reserve at `extension_good_faith_pct`: match.

DSL semantics used:
- `DAYS(a, b)` = (b − a).days.
- `within_months` keeps rows with 0 ≤ MONTHS(d, NOW) < N.
- `CFIELD` returns the first matching holding's field (F-3).
- `RND` is Python `round`. The scored halves in this difficulty (219.155 → 219.16; 438.31) round the same way under half-up.

### action_binding_and_uuids

- Seven distinct target tools and seven distinct `(target_tool, computes)` pairs. No policy claims another's.
- uuid8 suffixes are 6b5d55b7, 4c162eac, 2e6b8900, d761f3de, aa560e9a, 3d21c42f and 62601f54. They share no prefix, no tail and no sequence pattern, so they look independently generated.
- Docstrings name no other tool and state no position in a sequence. "before the sale" (redemption) and "applied first to fees due and then to principal" (reinstatement) are business semantics, not tool order.
- No docstring or parameter description carries an example value, so there is no gold-leak path.
- Function bodies validate nothing: each finds the contract, writes one row and updates balances. No prerequisite, status, date or amount check, so the tool layer judges no prerequisite.
- Shared write tools are only `verify_customer_identity` and `transfer_to_human_agent`. Neither can produce any waited-on state.
- **Tool-effect defect:** P-5. `remit_reinstatement_funds_62601f54` and `remit_deficiency_settlement_2e6b8900` post payments in an order the inherited base posting rule forbids, and the reinstatement tool leaves `next_due_date` untouched.

### prerequisite_graph

- Every policy has `prerequisite` filled in. Transport and release storage have `[]`.
- Edges:
  - deficiency_quote → transport (value_input, gate `fees_due`)
  - settlement → deficiency_quote (value_input, gate `quote_amount`)
  - redemption → release_storage (value_input, `fees_due`)
  - sale_notice → redemption (state_gate, `preowned_transactions.quote_purpose`)
  - reinstatement → release_storage (value_input, `fees_due`)
  - reinstatement → sale_notice (state_gate, `preowned_contracts.nois_mailed_date`)
- Every `problem` is an extended policy id in this file. None points at a base policy or at itself. The graph is acyclic: transport → deficiency quote → settlement, and storage → redemption → notice → reinstatement, plus storage → reinstatement.
- Every `policy_source` is verbatim in the blocked policy's own rule (mechanical check above).
- Every edge is `form: state` with no `fallback_reason`. That is consistent.
- `resolved_by` equals the depended-on policy's `target_tool` on every edge.
- Every value_input `gate` names a real compute binding of the blocked policy (`fees_due` in deficiency quote, redemption and reinstatement; `quote_amount` in settlement).
- `condition` against `policy_source`:
  - The transport, storage and notice conditions restate their sentences at the same strength.
  - The settlement condition says "a payoff quote whose quote date is the settlement date, and it is the most recent payoff quote". The sentence says "a deficiency quote". The condition is broader by kind, since a redemption quote dated today would satisfy its letter (O-9).
- The state_gate `gate` values name table fields rather than eligibility-gate ids (O-9).
- No authoring-viewpoint wording appears in any `prerequisite`.

### prerequisite_sentences

Four-point test on each sentence (connective, state named in record words, no tool/id/snake_case, matching strength):

1. Deficiency quote: "The deficiency figure is not stated until the account carries a transport charge dated on or after the repossession date of the most recent recovery." Connective "not … until". The state is a transport-kind repossession expense dated ≥ `repossession_date`. Only `book_recovery_transport_6b5d55b7` writes `fee_type='transport_fee'`. Passes.
2. Settlement: "The settlement figure is fixed only after a deficiency quote dated the settlement date stands on the account." Connective "only after". Only `quote_deficiency_balance_4c162eac` writes `quote_purpose='customer_payoff'`. Passes.
3. Redemption: "The redemption figure is not stated until the account carries a storage charge billed for the current repossession on the quote date." Only `bill_lot_storage_d761f3de` writes `fee_type='storage_fee'`. Passes on form. But see P-1: the policy that brings this state about is triggered only by a customer request, while this policy is owed without one.
4. Sale notice: "The notice of intent to sell is not mailed until a redemption quote dated the mailing date stands on the account." Only `quote_redemption_amount_aa560e9a` writes `quote_purpose='redemption'`. Passes.
5. Reinstatement (a): "Reinstatement funds are taken only after a notice of intent to sell for the current repossession is on the account." Only `mail_sale_notice_3d21c42f` writes a notice of intent to sell. Passes.
6. Reinstatement (b): "The reinstatement amount is fixed only after the account carries a storage charge billed for the current repossession on the statement date." Only the storage tool writes it. Passes.

Derivations (sentence + records + depended-on rule → resolving action), each with a single reading:
- Transport: "transport charge" + the transport rule ("The towing work on a recovery is billed to the contract as one transport charge") → book the transport charge.
- Settlement: "deficiency quote" + the deficiency-quote rule ("A deficiency quote states what a customer … still owes") → issue the deficiency quote.
- Redemption and reinstatement (b): "storage charge billed for the current repossession" + the release-storage rule ("Storage on a repossessed vehicle is billed … as one storage charge when the customer asks to get the vehicle back") → bill the release storage.
- Sale notice: "redemption quote" + the redemption rule → issue the redemption quote.
- Reinstatement (a): "notice of intent to sell" + the notice rule → mail the notice.

Depended-on rules restating the dependency (check 6 requires that they do not). The full class has two members, and both restate a declared edge rather than add an undeclared one (O-2):
- Release storage: "billed … when the customer asks to get the vehicle back, **before any reinstatement or redemption figure is stated**".
- Redemption: "**one dated the mailing date is owed whenever a notice of intent to sell is owed, because the notice states the redemption amount**".

No rule states a cross-problem order that grounds no declared edge. The base sentence that stated an order ("storage is billed up to the reinstatement date before the amount is stated") is superseded by the reinstatement overwrite, and no tree rests on a base ordering sentence.

### override_declarations

Each base sentence of each `base_policy_refs` entry, checked against the extended policy:

**preowned_repossession_charges** (cited by transport, deficiency quote, release storage, redemption):
- Status sentence: superseded for transport only (declared).
- Agency-fee sentence: followed.
- Transport-fee sentence: superseded (declared).
- Condition-report sentence: followed.
- Storage sentence: superseded for deficiency-quote storage and release storage (declared). Every other storage charge stays under base. See O-10 on the base storage charge at release after a reinstatement.
- Personal-property sentences: followed.
- "Expenses are booked to fees due and become part of any reinstatement, redemption or deficiency amount": followed.

**preowned_payoff_and_refunds** (deficiency quote, redemption):
- Status gate: followed.
- Good-through sentence: followed. The tools write today + 10, and every tier has `payoff_quote_valid_days` = 10.
- Per-diem/payoff sentence: superseded by both (declared).
- Good-through funds sentence, third-party sentence and refund sentences: followed or not touched.

**preowned_sale_and_deficiency** (deficiency quote, settlement, sale notice):
- Net-proceeds sentence: superseded inside the deficiency quote (declared).
- Settlement sentence: superseded (declared).
- Notice-period sentence: followed by the sale notice, whose result is always ≥ period + 1.
- Charge-off sentences: not touched.

**preowned_reinstatement_and_redemption** (settlement, redemption, reinstatement):
- Window, count and relationship gates: inherited.
- Amount sentence: superseded (declared).
- Redemption-amount sentence: superseded (declared).
- Funds-type sentence: followed (wire).
- "once the funds post the vehicle is released and, for a reinstatement, the original schedule resumes with next_due_date set to the next installment":
  - The extended rule says "released on the storage lot's next business day". This is not declared. Read as "released after the funds post, on the lot's next business day", it is compatible (O-3).
  - The `next_due_date` half is not carried out by the tool (P-5).

**preowned_payment_posting** (settlement, reinstatement):
- Status, cutoff (20:00 CT) and channel-fee sentences (online_ach and wire both $0.00): followed.
- Allocation sentence ("Each payment is applied in payment_allocation_order: first to simple interest accrued … then to principal … then to fees due"): weakened by the tool layer without a declaration (P-5).

**preowned_repossession_assignment** (sale notice):
- Mailing-period, status and contents sentences: followed.

No anonymous intermediate, no 0/1 multiplier and no dropped base branch was found inside the extended computes.

### factor_ladders

Counts per policy (declared → surviving the structural tests):

| policy | factors | parameter | method | cross_difficulty | multi-source factors |
|---|---|---|---|---|---|
| transport | 4 | 3 | 1 declared → **0 honest** (F-2) | — | none (tow_leg_count tier 2 and the search tiers are single-source) |
| deficiency quote | 5 | 4 | 1 | lease_relationship_rate (lease) | lease_relationship_rate (status + dpd + payments, one holding); disposition share tier 2 (repossession type + sale row) |
| settlement | 5 | 4 | 1 | lease_standing (lease) | settlement_base_rule (both tiers: reinstatement payment row + contract repossession type); installment_history tier 1 |
| release storage | 4 | 3 | 1 | — | repeat_recovery_free_days (both tiers); lot_arrival_anchor tier 1 |
| redemption | 4 | 3 | 1 | — | redemption_interest_end tier 2; projected_lot_storage tier 1 |
| sale notice | 5 | 4 | 1 | retail_relationship_days (retail) | established_customer_days tier 1 |
| reinstatement | 4 | 3 | 1 | retail_relationship_reserve (retail) | second_reinstatement_pay_ahead (both tiers) |

Per task:
- Task 0 has multi-source settlement_base_rule and cross-difficulty lease.
- Task 1 has multi-source second_reinstatement_pay_ahead and repeat_recovery_free_days, and cross-difficulty retail.

Structural checks on every ladder:
- Each ladder has three tiers that are pairwise disjoint as stated.
- Each `decides` names an input binding, never `result`.
- Binding sets are disjoint within each policy.
- Every tier, with its condition and its value or method, is stated in prose in the rule and implemented in `compute`.
- Every fall-through is the baseline, and every factor `baseline` encodes what `baseline.rule` states for that input.
- Each `baseline.rule` is self-sufficient and its sentences are in the rule.
- The `baseline.params` keys are the ones each baseline uses. Reinstatement has `[]`; its baseline uses only record fields.

Method honesty:
- deficiency post_sale_accrual_end: stop at sale / fixed 60-day window / through good-through. Honest.
- settlement_base_rule: three fee treatments. Honest.
- lot_arrival_anchor: transport date / repossession date inclusive / day after. Honest.
- redemption_interest_end: honest.
- reinstatement_right_anchor: state period / company window / none. Honest.
- weekend_release_storage: a derived daily amount from the latest storage row / tier fee / none. Honest.
- transport weekend_recovery: **not honest** (F-2).

Ladder-reality findings:
- F-1: tiers that coincide with the fall-through on reachable variants.
- F-3: first-match cross-holding reads with overlapping tiers.
- F-4: a scope-restating conjunct.
- F-5: realism of the reinstatement add-ons on a state-granted reinstatement.
- Realism observations: O-4 (relationship reserve not monotone), O-5 (redemption reconditioning estimate and projected storage), O-7 (returned-payment reserve priced from the extension good-faith percentage), O-8 (a transport charge added after the deficiency notice).

### findings

Charter-wide REDs, each with the tasks it bears on. Every task file picks up the demonstration.

**P-1 SOURCE-POLICY RED: a state_due chain bottoms out in an on_request leaf. Bears on: no task world (latent); charter-wide.**
- Symptom: in a world where the customer does not ask to get the vehicle back, the notice of intent to sell becomes impossible to mail, although the charter says it is owed.
- Evidence:
  - Sale-notice rule: "the notice of intent to sell is mailed within the notice mailing period after the repossession date … it is owed whether or not the customer calls. The notice of intent to sell is not mailed until a redemption quote dated the mailing date stands on the account."
  - Redemption rule: "one dated the mailing date is owed whenever a notice of intent to sell is owed … The redemption figure is not stated until the account carries a storage charge billed for the current repossession on the quote date."
  - Release-storage rule: "Storage on a repossessed vehicle is billed to the contract as one storage charge when the customer asks to get the vehicle back … every other storage charge remains under the base storage rule".
  - Base: "[storage] is billed when the vehicle leaves the lot".
- Demonstrated consequence: take an involuntary repossession on its third business day, with no call or a call about personal property only. The notice is owed. The redemption quote it needs cannot be stated, because no storage charge can be billed: the customer has not asked for the vehicle and the vehicle has not left the lot. Reading A, mail the notice without a redemption quote, breaks the notice's own prerequisite sentence. Reading B, do not mail it, breaks "owed whether or not the customer calls" and the base deadline (`nois_mail_business_days`).
- Root cause: the waited-on state is produced only by an on_request policy.
- Affected: the trigger and opening sentence of `preowned_ext_release_storage_charge`, `preowned_ext_redemption_quote`, and `preowned_ext_sale_notice_schedule`.

**P-2 SOURCE-POLICY RED: a gate requires a charge the schedule prices at $0. Bears on: no task world; charter-wide.**
- Evidence:
  - Deficiency rule: "The deficiency figure is not stated until the account carries a transport charge dated on or after the repossession date of the most recent recovery". The same policy prices voluntary surrenders ("for a voluntary surrender no interest runs after the sale date", "for a voluntary surrender the share is the voluntary-surrender expense share"), and settlement_base_rule tier 2 prices "no reinstatement payment and the vehicle came back by voluntary surrender".
  - Transport rule: "a voluntary surrender is charged no leg … any voluntary surrender, carries no weekend surcharge". The charge is therefore (rate + surcharge) × 0 + 0 = 0.00.
  - `book_recovery_transport_6b5d55b7` docstring: "amount: … a positive number".
- Demonstrated consequence: in a voluntary-surrender world sold at auction, the deficiency figure can never be stated unless a $0.00 "transport charge" is booked for a tow that never happened, against the tool contract. As a result, three voluntary tiers can only be reached through an unreal $0 booking: deficiency post_sale_accrual_end tier 1, disposition_expense_share tier 1, and settlement_base_rule tier 2.
- A second member of the class is an observation: the storage-gated edges (redemption, reinstatement) need "a storage charge", which the release-storage schedule prices at $0.00 whenever billable days are 0 (stored days ≤ free days). The tool accepts 0, and in such worlds the value_input edge carries no weight.
- Affected: the deficiency prerequisite sentence and transport tow_leg_count tier 2.

**P-3 SOURCE-POLICY RED: when the transport charge is booked has two readings, and the two task worlds rely on opposite ones. Bears on: task 0 and task 1.**
- Evidence:
  - Transport rule: "booked from the repossession agency's invoice once the vehicle's movements for that recovery are complete … it is booked once per recovery … an involuntary recovery whose vehicle was later sold at auction is charged two legs, the recovery tow and the delivery to the auction".
  - Release-storage rule: "for an involuntary recovery with a transport charge posted after the repossession date, the vehicle reached the storage lot on the latest such transport date".
  - Sale-notice rule: "a vehicle held on the storage lot, shown by a transport charge posted after the repossession date of an involuntary recovery, adds the lot transfer days".
  - Redemption rule: "for a vehicle on the storage lot, shown by a transport charge posted after the repossession date".
- The 2-leg tier is reachable only if booking waits until the auction delivery (reading B). The three lot policies treat a transport charge as the marker of arrival on the lot, before any sale (reading A). Under reading A a once-per-recovery charge booked at arrival can never carry the second leg.
- Task 1's seed follows reading A: transport `21a06c2e-5…`, 2026-10-14, 190.00, one leg, booked the day after the 2026-10-13 repossession with the vehicle still on the lot.
- Task 0's seed follows reading B: no transport charge for the 2026-06-28 recovery until after the 2026-07-22 sale.
- The per-task consequence is demonstrated in 0.md and 1.md.
- Affected: the transport rule's booking-moment sentence; the lot-marker sentences of release storage, sale notice and redemption; seed rows in both tasks.

**P-4 SOURCE-POLICY RED: two policies disagree on whether returned-payment and extension fees can be collected during a state reinstatement period. Bears on: task 1.**
- Evidence:
  - Redemption rule: "Fees the state reinstatement period does not let the company collect are left out of the figure … while the quote date is within a recorded state reinstatement period longer than the company window, returned-payment fees and extension fees are left out; while it is within a recorded state reinstatement period that is not longer than the company window, returned-payment fees are left out".
  - Reinstatement rule, applying on the same dates in the same period: "The standard reinstatement amount is the past-due amount plus the fees due balance". The `fees_due` account holds "late charges, returned-payment fees, extension fees and repossession expenses", and the rule adds a separate "returned-payment reserve" on top.
- Same situation, different conclusions: on a statement date inside the state period, the redemption policy holds that the company may not collect a posted returned-payment fee, while the reinstatement policy collects it.
- Demonstration in 1.md.

**P-5 SOURCE-POLICY RED: the tool layer weakens inherited base posting provisions without a declaration. Bears on: task 1 (terminal state) and task 0 (settlement posting split).**
- Evidence:
  - Base `preowned_payment_posting`: "Each payment is applied in payment_allocation_order: first to simple interest accrued over preowned_msr_interest_accrual_days …, then to principal until preowned_msr_installments_due is satisfied, then to fees due, and any remainder to principal". The tier order is `[accrued_interest, principal, fees_due]`.
  - Base `preowned_reinstatement_and_redemption`: "for a reinstatement, the original schedule resumes with next_due_date set to the next installment".
  - `remit_reinstatement_funds_62601f54`: "the amount is applied first to fees due and then to principal". Its body writes `interest_applied=0.0`, `fees_applied=min(amt, fees)` and principal for the rest, and never updates `next_due_date` or `interest_paid_to_date`.
  - `remit_deficiency_settlement_2e6b8900` writes `interest_applied=0.0, principal_applied=amt`.
  - Both overwrites of the reinstatement and settlement policies name only the amount sentences.
  - The seeded reinstatement precedents follow base: task 0 `a16df589…` posts interest 585.58 / principal 1236.41 / fees 722.00; task 1 `504d5f4f…` posts interest 1088.05 / principal 1541.81 / fees 744.00.
- The demonstration against task 1's terminal state is in 1.md.

**F-1 SOURCE-FACTOR RED: on reachable variants, a tier selects the same value as its fall-through. Charter-wide; neither task world sits on a colliding variant.** Two members:
- (a) Reinstatement returned_payment_reserve: the "exactly one returned payment" tier is RND(installment × `extension_good_faith_pct`/100). That parameter is 0 in Tier 1 and Tier 1+, so the tier gives 0.00, the same as the "no returned payment adds nothing" fall-through.
- (b) Deficiency lease_relationship_rate: the short-relationship tier (9.99 %) equals the "contract rate" fall-through for every contract booked at 9.99 %. Examples: Tier 2, 61-72 band, `apr_rate_sheet` 9.99; Tier 2, 24-36 band, other make, 8.99 + `non_kestrel_make_apr_adder_pct` 1.0.

**F-2 SOURCE-FACTOR RED: the transport weekend_recovery factor is labelled `method`, but every tier selects a constant. Bears on: task 0.**
- The tiers are "the Sunday share times the transport fee for the tier", "a fixed flat amount" and "no weekend surcharge". `repo_transport_fee` is 135.00 in all six variants, so the three tiers select 67.50, 50.00 and 0.00 into the same slot (`+ weekend_surcharge`) in every world. That is a number substitution, not a change of algorithm.
- With this label struck, the transport computation has 0 honest `method` factors, below the floor of 1.

**F-3 SOURCE-FACTOR RED: cross-holding reads take the first match with no guard, and the tiers overlap when the customer holds two active holdings of the read category. Charter-wide; each task world holds exactly one active holding of the category it reads.** The full class has six bindings in four policies:
- deficiency quote `lease_days_past_due`, `lease_payments_made`
- settlement `lease_past_due_days`, `lease_payments_count`
- sale notice `retail_days_past_due`
- reinstatement `retail_past_due_days`

All read `CFIELD(cat, field, status='active')`, which returns `hs[0]`. Demonstration: active lease A (days past due 0, 22 payments) and active lease B (20 days past due). The settlement rule's tier 1 ("an active Kestrel lease with no days past due and at least … payments") and tier 2 ("an active Kestrel lease with any days past due") both describe this customer, giving −5 or +5 points depending on row order. The deficiency rate tiers and both retail ladders overlap the same way.

**F-4 SOURCE-FACTOR RED: deficiency disposition_expense_share restates the policy's scope inside a compound condition. Bears on: task 0 (structure only; the factor keeps its weight).**
- Tier 1 reads "came back by voluntary surrender **and was sold at auction**"; tier 2 reads "involuntary **and … sold at auction** for a gross sale price below the low-value sale limit".
- Every customer who reaches a deficiency quote has had the vehicle sold at auction. The rule's own scope is "a customer whose repossessed vehicle has been sold at auction", and the events section says `preowned_repo_sale` means "The repossessed vehicle is sold at auction". The conjunct, and its `COUNT(…preowned_repo_sale) >= 1`, divide no customers.

**F-5 SOURCE-FACTOR RED (realism): the reinstatement add-ons are charged on a reinstatement the recorded state period grants. Bears on: task 1.**
- The base charter treats a reinstatement the contract's `state_reinstatement_days` grants as the customer's right, not company discretion: "unless the contract records state_reinstatement_days greater than 0"; "a reinstatement the contract's recorded state_reinstatement_days grants is still offered". The redemption policy itself concedes that the state period limits what may be collected (P-4).
- US state reinstatement statutes fix the cure at past-due installments plus permitted charges and repossession and storage expenses. The 21-day Illinois right matches task 1's IL contract with `state_reinstatement_days` 21. A creditor does not publish pay-ahead installments, a reserve keyed to another account's delinquency, or a returned-payment reserve as conditions of that statutory cure.
- Yet second_reinstatement_pay_ahead tiers 1-2, retail_relationship_reserve tiers 1-2 and returned_payment_reserve tiers 1-2 apply whether or not the reinstatement is the state-granted one.
- In tiers with `reinstatement_max_per_contract` 1 (Tiers 2-5), a second reinstatement, which is the pay-ahead factor's own condition, is available only through the state right. So the pay-ahead tiers are reached essentially only by statutory reinstatements.

Charter-wide observations (not grounds for rework on their own):
- O-1: the deficiency 100 % fall-through credits expenses above the gross price, against the rule's "nothing is credited". Not realistically reachable.
- O-2: two depended-on rules restate their dependency (prerequisite_sentences above). This is the same text P-1 touches.
- O-3: "released on the storage lot's next business day" against base "once the funds post the vehicle is released" is an undeclared refinement. It decides the pick-up day the customer is told: today or the next business day.
- O-4: the relationship-reserve fall-through gives 0 at ≥ 30 days past due while 15-29 days gives a full installment. The base gate withholds only discretionary reinstatements at 30 or more, so a state-granted reinstatement with a retail account 45 days late pays less than one 20 days late.
- O-5: the redemption quote adds a reconditioning estimate the redeeming customer never causes. It also projects storage at the plain $18.00 tier fee while the release-storage schedule bills the same days at statutory rate plus oversize ($22.00 in task 1), and projects past its own 10-day good-through date to the end of the state period.
- O-6: deficiency "the days from the sale date through the notice mailing date are interest-free" can be counted inclusively (one more day). The paragraph's lead "Days after the sale on which…" and "taken off the post-sale days" support the exclusive count.
- O-7: the returned-payment reserve is priced from `extension_good_faith_pct`, a parameter of the extension program.
- O-8: booking a new transport charge on a deficiency account after the deficiency notice has been mailed changes the deficiency the notice explained. This is a compliance risk under real practice and is allowed here by the declared status overwrite.
- O-9: the settlement edge condition is broader than its sentence ("payoff quote" against "deficiency quote"), and the state_gate `gate` values are field paths rather than eligibility-gate ids.
- O-10: after a reinstatement, the release on the next business day falls under base "every other storage charge", which counts from the repossession date to the release date. That would re-bill days the release-storage charge already billed.
- O-11: the transport tool dates the charge "today", while the event's `txn_date` meaning is "service date". In late bookings (task 0) the transport date is not the service date, and the release-storage policy reads that date as the lot-arrival date.
- O-12: seeded own-category history follows base, not the extended schedules. Notices of intent to sell were mailed with no redemption quote (task 0 2026-06-30 and 2025-06-17; task 1 2025-06-09). Task 0's 2026 sale came 22 days after its notice, where the extended schedule would set 26.

## closing_checklist

Written after both reveals (2026-10-15T20:28:02Z). Everything above this heading was frozen at 2026-10-15T20:25:42Z, before any reveal, and was not changed.

- Per-task files 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json, and this file sits alongside them. This is round 1, so there are no older revisions.
- Scope: `charter_scope` of task 0 is {transport, deficiency_quote, deficiency_settlement}; task 1 is {release_storage, redemption_quote, sale_notice, reinstatement_funds}. That matches the blind partition in § policy_conflict_scan. The two are pairwise disjoint and jointly cover all 7 extended policies and 7 task tools.
- Trees: task 0 has 2 prerequisite problems with 2 value_input edges; task 1 has 3 prerequisite problems with 2 value_input edges. Both have the customer's own write at the root, and neither has a cycle. The whole-difficulty graph is a DAG.
- Unique solution: both tasks' blind derivations equal GT on every scored argument, owner and order. Every factor bears weight against an honest baseline, and every all-baseline figure is definite and differs from gold (figures in each task file).
- **Not closed.** Charter-wide REDs are open:
  - P-1, P-2, P-3, P-4, P-5 (SOURCE-POLICY)
  - F-1, F-2, F-3, F-4, F-5 (SOURCE-FACTOR)
  - Task-level T0-F6 (seed of the decoy lease).
- Bearing on the tasks:
  - Task 0 carries P-3, F-2 and T0-F6 at RED weight, F-4 structurally, and P-5 at observation weight.
  - Task 1 carries P-3, P-4, P-5 and F-5.
- Gate re-run on the final form: not applicable until rework. The round-1 snapshot (snapshot_r1.txt) is the gate state these verdicts rest on.

task0=SOURCE-POLICY+SOURCE-FACTOR RED task1=SOURCE-POLICY+SOURCE-FACTOR RED
charter=P-1,P-2,P-3,P-4,P-5,F-1,F-2,F-3,F-4,F-5

## revision_2

### charter_global_frozen (revision_2)

- Re-audit round 2. Auditor: same independent erl-task-policy-audit agent.
- Gating line: `tail -1 worklog.md` reads `REWORK round 2: gates 8/8 green`. Passed.
- Gate snapshot: `.audit_views/policy/preowned_repossession_recovery/snapshot_r2.txt` (2026-10-15T22:57:02Z), produced by running `/tmp/erl0066_coord/snapshot.sh preowned_repossession_recovery 2`.
  - check_extended, task_tools, replay --check, solvability, compute, grounding and cross_fire are all OK.
  - The only traceability miss is the unlock tool-name provenance, and validate reports `documents: 0`. Both are expected before render.
- Frozen hashes:
  - charter `preowned.extended.yaml` 3446bcbf4d6c49ff (round 1: 55fb44b63da012c4, changed)
  - `task_tools.py` 00e892251c847a86 (round 1: e9810ad98a9094ae, changed)
  - views 0.json 25fb1d0bed072a9b and 1.json edb5b222f5045f8d (both changed)
- Both shared inputs changed, so every charter-global section below is **re-derived in full**. Round-1 text above stays untouched.
- Base copy: every top-level key except `extended_policies` is still identical to `blueprint/products/preowned.yaml`.
- Read before this section was written: blueprint/, the charter, task_tools.py, `audits/render_source/XF_recipe.md`, the masked views, and the DSL evaluator.
- Not read before this section was written: the revision_2 task JSON GT fields, worklog.md (including its "REWORK round 2 closure" claims), and design_rationale. Round-1 GT was revealed in round 1 and is disclosed in each task file. Nothing below derives from round-2 GT.

### policy_conflict_scan (revision_2)

- Seven extended policies, each with the same target tool as round 1.
- Triggers changed for two policies: release storage is now `state_due` ("owed once such an amount is owed, whether or not the customer calls … booked even when it comes to 0.00"), and redemption is `state_due` ("owed whenever the company must state the redemption amount").
- Scopes from the masked views:
  - Task 0 (Tier 4, OH, deficiency): transport → deficiency quote → settlement.
  - Task 1 (Tier 1+, TX, repossessed, discretionary reinstatement): storage → redemption → notice → reinstatement.
  - The two are disjoint and together cover all seven policies.
- Conflicts found: see R2-X9 (base storage clause on the redemption path) and the realism ladders R2-F1 and R2-F2. Every round-1 conflict is closed (closure table below).

### rule_compute_equivalence (revision_2)

Mechanical sweep: all `compute_basis` quotes, `policy_source`, `replaced_by` and `baseline.rule` are verbatim in their own rules, and all `superseded_clause` are verbatim in the cited base rules. No misses.

Back-sweep of the changed parts:

**Transport.**
- Tow rate: the counting is stated as "(the assignment date not counted, the repossession date counted)", which equals DAYS.
- Repeat surcharge 60/30/0; weekend surcharge 70/50/0.
- Yard hold: nights = DAYS(repossession, lot intake), with a tie on the lot-intake date resolved to the first one listed. 1..7 nights × 25.00; more than 7 nights = 150.00; 0 otherwise.
- `result` returns 0.0 for a voluntary surrender. The rule says "none is booked". Equivalent.
- Gap: R2-X8(a).

**Deficiency quote.**
- Post-sale rate is the contract rate × 0.3 or × 0.6, otherwise the contract rate.
- The interest-free order is: no notice, then "most recent … more than grace", then 0. The days count "after the sale date up to and including the notice mailing date". This closes round-1 O-6.
- The disposition credit is now 0 at the 100 % share. This closes round-1 O-1.
- Gap: R2-X10, rounding inside the credit.

**Settlement.**
- Unchanged, except the posting sentence now restates the allocation order.
- Gap: R2-X6, a tie clause missing on the standard read.

**Release storage.**
- Lot-intake anchor is now the most recent condition report, with the tie rule stated.
- The rate tiers are statutory 12 / window 15 / tier fee, with "(not counted)/(counted)" conventions. Equivalent.

**Redemption.**
- Interest end and good-through: (state period still running) → state end; (no longer state period, window running) → window end; otherwise good-through. Equivalent. The good-through date becomes a tool argument (`good_through_days`).
- Projected storage uses the latest storage charge's daily amount (amount / MX(1, days), tie rule stated) for the projected days.
- Excluded fees: (within any recorded state period) returned-payment + extension fees; (within the window, no state period running) returned-payment fees. Equivalent.
- Gap: R2-X8(b).

**Sale notice.**
- Unchanged, except the lot marker is now the condition report and the first-listed retail tie rule is stated.

**Reinstatement.**
- `state_right_running` is a plain binding. When it holds, the amount is standard − 12-month returned-payment/extension fees + posting-day storage. Otherwise it is standard + pay-ahead + reserve + returned-payment reserve (share 0.25) + posting-day storage.
- Posting-day storage: Saturday adds 2 × the latest storage daily amount (0 if there is none); Sunday adds 1 × the tier fee; otherwise 0. Equivalent to the rule.
- Gaps: R2-X1(b), R2-X7, R2-X9(a).

### action_binding_and_uuids (revision_2)

- Same seven tools and uuid8 suffixes, all unique.
- New signatures: `book_recovery_transport_6b5d55b7(…, service_date)` and `quote_redemption_amount_aa560e9a(…, good_through_days)`.
- No body validates a prerequisite.
- Docstrings carry no example values, name no other tool, and use no ordering word that restates a dependency. The redemption docstring dropped "before the sale".
- Tool effects:
  - The settlement and reinstatement bodies now split payments as interest accrued to the posting date, then principal up to the past-due amount, then fees, then the remainder to principal. This matches base `payment_allocation_order` and the measure (`next_due_date` is in the past on these contracts, so the installments-due measure equals the past-due amount).
  - The reinstatement body also advances `next_due_date` and `payments_made_count` by covered installments. `add_months` clamps to day 28, which is unreachable because `due_day_latest` is 28 in every tier.
  - The reinstatement row is dated with the posting date (the Monday for a weekend wire), and the contract is set `active` at call time (O-r2-3).

### prerequisite_graph (revision_2)

- Edges are unchanged in shape: deficiency quote → transport (value_input), settlement → quote (value_input), redemption → storage (value_input), notice → redemption (state_gate), reinstatement → storage (value_input), and reinstatement → notice (state_gate).
- The graph is acyclic. Every `resolved_by` equals its target tool. The value_input gates name real bindings.
- The deficiency condition now carves out voluntary surrenders, matching its sentence "For an involuntary recovery, …".
- The settlement condition now says "a deficiency quote, a payoff quote issued to the customer". The round-1 O-9 first half is closed. The state_gate `gate` values are still field paths (observation carried).

### prerequisite_sentences (revision_2)

The four-point test passes on every edge:
- Deficiency: "For an involuntary recovery, the deficiency figure is not stated until the account carries the transport charge for that recovery, dated on or after its repossession date." Only the transport tool writes a transport-kind expense.
- The other five sentences are unchanged and pass as in round 1.

Depended-on rules:
- Storage: "whenever the company must state an amount the customer has to pay to get the vehicle back".
- Redemption: "owed whenever the company must state the redemption amount".
- These now state their own triggers, not the blocked side's order. Round-1 O-2 is closed.

No undeclared cross-problem order was found.

### override_declarations (revision_2)

Each overwrite re-checked sentence by sentence against the XF recipe point 9:

- **Transport.** The status overwrite restates "every other repossession expense can be charged only while … assigned … or repossessed". The transport-fee overwrite restates the involuntary/voluntary split.
- **Deficiency.** The payoff overwrite restates the base payoff formula for other quotes and names the redemption sibling. The net-proceeds overwrite restates "stay applied to principal as posted". The storage overwrite restates base storage for other charges and names the statement-storage and reinstatement-posting cases.
- **Release storage.** The storage overwrite names the posting-days case and the deficiency case and restates base for "every other storage charge" (but see R2-X9(b)).
- **Redemption.** Three overwrites (the payoff formula, the good-through sentence, and the redemption amount) share one replaced_by. It restates the base payoff, including "unless the requester asks for an earlier date".
- **Settlement.** The overwrite restates "pays the contract in full".
- **Reinstatement.** The amount overwrite restates the standard amount and the statutory/discretionary split.
  - **Missing:** the reinstatement collects storage for the days until the funds post, which retires part of the base storage clause. That retirement is declared only inside the siblings' replaced_by texts, never in this policy's own `overwrite` (R2-X9(a)).
  - Base "once the funds post the vehicle is released" now agrees with the extended rule (round-1 O-3 closed).

### factor_ladders (revision_2)

| policy | factors | parameter | method | cross_difficulty | multi-source |
|---|---|---|---|---|---|
| transport | 4 | 3 | 1 (agency_yard_hold) | — | none |
| deficiency quote | 5 | 4 | 1 | lease | disposition tier 2 (repossession type + sale row) |
| settlement | 5 | 4 | 1 | lease | settlement_base_rule |
| release storage | 4 | 3 | 1 | — | repeat_recovery_free_days |
| redemption | 4 | 3 | 1 | — | projected_lot_storage tier 1 (condition report + contract period + date) |
| sale notice | 5 | 4 | 1 | retail | established_customer_days |
| reinstatement | 4 | 3 | 1 (weekend_posting_storage) | retail | second_reinstatement_pay_ahead |

Structure:
- Every ladder has three disjoint tiers stated in the rule and implemented in `compute`.
- Every fall-through is the baseline. No factor reads another factor's binding (XF 3 sweep: none).
- Method honesty: yard hold (nights × rate against a flat amount) is honest, and so is posting storage (a record-derived daily amount against the tier fee). The transport weekend factor is now labelled parameter (round-1 F-2 closed).

Ladder realism:
- R2-F1: yard hold is not monotone.
- R2-F2: posting-day storage is priced by the call day.
- Pay-ahead, relationship reserve and returned-payment reserve now apply only to discretionary reinstatements (round-1 F-5 closed).
- The post-sale rate is a share of the contract rate, so it never equals the fall-through (round-1 F-1(b) closed).
- The returned-payment reserve share is the policy's own 0.25 (round-1 F-1(a) closed).
- The disposition tiers no longer restate the scope (round-1 F-4 closed).

### closure of round-1 charter REDs (verified against the artifacts on disk)

| id | status | evidence |
|---|---|---|
| P-1 | closed | Storage is now state_due: "owed once such an amount is owed, whether or not the customer calls … booked even when it comes to 0.00". The notice → redemption → storage chain no longer bottoms out in a customer request. |
| P-2 | closed | The deficiency gate is scoped "For an involuntary recovery". The transport rule: "a voluntary surrender carries no transport charge … and none is booked". The tool is now "for an involuntary recovery". |
| P-3 | closed | One transport charge per recovery, "dated the lot-intake date"; "delivery … to an auction is an auction sale expense"; the 2-leg tier is gone. All three lot markers now read the condition report. No second reading remains. Seed misuse in task 0 is handled per task. |
| P-4 | closed | The redemption exclusion is now a payoff concession ("fees it does not collect on a payoff made during a reinstatement period"). The statutory reinstatement leaves out the same fees. Both agree within a state period. |
| P-5 | closed | Both remit tools allocate per base and advance the schedule (see action_binding_and_uuids). |
| F-1 | closed | (a) The reserve share is a policy constant of 0.25. (b) The post-sale rate is a share of the contract rate. |
| F-2 | closed | weekend_recovery is now a parameter. The transport method factor is agency_yard_hold. |
| F-3 | closed | All six first-match reads now state "the first one the lease/retail lookup lists is the one read". |
| F-4 | closed | The scope conjunct was removed. |
| F-5 | closed | A state-granted reinstatement adds no reserve and no pay-ahead, and leaves out returned-payment and extension fees. Task 1 moved to a discretionary TX contract. |

Round-1 observations: O-1, O-2, O-3, O-5 (projection now at the billed daily amount, with good-through = projection end), O-6, O-10 (reinstatement case) and O-11 are closed. O-4 is closed because a discretionary reinstatement with ≥ 30 days past due is no longer offered. O-7 is closed because the reserve has its own share. O-8 and O-12 are superseded by the task-level seed findings. O-9 is half closed.

### findings (revision_2)

Charter-wide REDs, found by the XF recipe sweep and the realism review. Each lists every member found.

**R2-X1, SOURCE-POLICY RED (XF 1: assembly sentences name factor quantities).**
- (a) Settlement: "the settlement percentage is the age percentage plus every adjustment in percentage points, never below the minimum settlement percentage for the tier; that percentage is applied to the settlement base; any part of the balance carried outside the base is added in full". This names sale_age's quantity ("age percentage"), the settlement_base_rule quantities ("settlement base", "outside the base") and the other factors ("every adjustment").
- (b) Reinstatement: "…and no company reserve or installment paid ahead is added to it. Every other reinstatement is … and the reserves and installments below are added to it." This assembles the pay-ahead, relationship-reserve and returned-payment-reserve quantities by name. The gating actually lives in `result` (`0.0 if state_right_running else …`), not in any factor's tiers.

**R2-X6, SOURCE-POLICY RED (XF 6: tie on a latest read).**
- The settlement standard reads "the amount of the most recent deficiency quote on the account" (the `quote_amount` LATEST) with no tie clause.
- The tie clause ("the first one listed where two share a date") is attached only to the balance-size factor sentence.
- A rendered computation document carries the standard without the factor's sentence, so the settlement base's tie is unstated.

**R2-X7, SOURCE-POLICY RED (XF 7: twelve-month windows).**
- Members:
  - sale notice "no returned payment in the twelve calendar months before the mailing date"
  - redemption "fees posted in the twelve calendar months before the quote date" (both tiers)
  - reinstatement "posted in the twelve calendar months before the statement date" (statutory exclusion)
  - reinstatement "counted over the twelve calendar months before the statement date" (returned-payment reserve)
- The DSL window is 0 ≤ MONTHS(d, NOW) < 12. It includes rows dated the statement date itself, which "before" excludes, and drops the anniversary date. The base measure states its own convention ("ending on today's date, inclusive"); these rules do not.
- Demonstration: a returned payment posted on the statement date counts under compute (1 returned payment, reserve 0.25 × installment) and does not count under "before" (0, nothing). Neither task world sits on the boundary.

**R2-X8, SOURCE-POLICY RED (XF 8: unstated compute branches).**
- (a) Transport yard hold: when the most recent condition report predates the repossession date (a report from an earlier recovery, with the current one not yet taken), the compute gives `yard_nights` 0 and charge 0. The rule defines the lot-intake date as "the date of the most recent condition report" and covers only "taken to the lot on the day of the repossession, or with no condition report on record", so the negative-difference case is not stated.
- (b) Redemption `storage_daily_amount`: the compute's absent-record branch (`… if LATEST(…) != None else 0.0`) is not stated in the redemption rule. The reinstatement rule states its twin ("nothing where no storage charge is on record").

**R2-X9, SOURCE-POLICY RED (XF 9: base storage clause).**
- (a) The reinstatement rule collects storage "until the funds post" at the latest storage charge's daily amount or the tier fee. That retires part of the base clause "Storage is charged at storage_daily_fee … counting from repossession_date to the release or sale date, and is billed when the vehicle leaves the lot". Yet `preowned_ext_reinstatement_funds.overwrite` names only the amount sentence. The retirement appears only inside the release-storage and deficiency siblings' replaced_by texts.
- (b) The release-storage replaced_by keeps base for "every other storage charge … counting from the repossession date to the release or sale date, and billed when the vehicle leaves the lot". On the redemption path this second charge is not carved out.
  - Demonstration on a task-1-like world: the customer redeems; storage was already billed through the statement date (50.00, 2 days), and the redemption figure already collected the projected storage through the period end (450.00).
  - When the vehicle leaves the lot, the retained base text bills storage again from the repossession date to the release date, beyond the free days, at 18.00 a day. The same days are charged twice.

**R2-X10, SOURCE-POLICY RED (XF 10: rounding placement).**
- The deficiency compute rounds inside the credit: `disposition_credit = MX(0, sale_expense − RND(gross_sale × share / 100, 2))`.
- The rule says the credit is "computed as the expenses less the share times the gross sale price, never below zero" and "the figure is rounded to the cent once at the end".
- Demonstration: gross 5800.56 at 10 % gives 580.056. The compute uses 580.06; the rule keeps 580.056 to the end, so the figures can differ by a cent. Task 0's gross is 5800.00, so it is unaffected.

**R2-F1, SOURCE-FACTOR RED (unreal ladder: agency_yard_hold is not monotone).**
- "a hold of one night up to the yard cap nights is charged at the yard rate for each night, the charge growing with every night held; a hold of more than the yard cap nights is charged the flat weekly yard charge, whatever its length".
- With the parameters 25.00 per night, a 7-night cap and 150.00 weekly: 7 nights cost 175.00, 8 nights cost 150.00, and 30 nights cost 150.00.
- No agency or lender publishes a holding schedule where an extra night lowers the charge, or where a month costs one week's flat. Task 0 takes this ladder (2 nights, 50.00).

**R2-F2, SOURCE-FACTOR RED (unreal ladder: posting-day storage priced by the call day).**
- Saturday: "two days are added at the daily amount of the most recent storage charge". Sunday: "one day is added at the daily storage fee for the tier".
- The same posting-day storage, Monday, is priced at the latest charge's daily amount (25.00 in task 1: window rate 15.00 + oversize 10.00) when the customer calls on Saturday, but at the plain 18.00 tier fee when the customer calls on Sunday. The release-storage schedule itself bills that vehicle 25.00 a day.
- A business prices a storage day by the vehicle and the period, not by which weekend day the customer phoned.
- Task 1 takes the Saturday tier.
- This class was already present in round 1 as Friday/Saturday, and the round-1 audit missed it.

Charter observations (revision_2):
- O-r2-1: the twelve-month fee exclusions (redemption concession, statutory reinstatement) subtract fees *posted* in the window even if already paid, so they can take out more than `fees_due` holds.
- O-r2-2: the sale-notice schedule ignores weekdays. Task 1's schedule lands on Sunday 2026-11-22.
- O-r2-3: the reinstatement tool sets `status='active'` when the wire is sent but dates the payment row with the posting date (the next Monday for a weekend wire). The rule says "once the funds post the contract returns to active". The DB is therefore active two days before the funds post.
- O-r2-4: the transport charge is booked with a past `service_date` (the lot-intake date) months later in task 0, so the posting history carries a back-dated fee.
- O-r2-5: the redemption figure still adds an estimated reconditioning cost the redeeming customer never causes. It is now framed as a disposition expense ("an expense of disposition the redemption must cover"). Real redemption covers expenses *incurred* (UCC 9-623). This is a realism observation, carried from round-1 O-5.
- O-r2-6: the state_gate `gate` values are still field paths.

### reworker claims against the artifacts (revision_2, after reveal)

The "REWORK round 2 closure" claims were checked against the artifacts. Every round-1 item claim matches what is on disk (closure table above). The XF table claims "ok" in places where this audit finds members:

| XF point | claimed | found |
|---|---|---|
| 1 | X and R "ok" | R2-X1(a), R2-X1(b) |
| 6 | X "quote" | the tie is stated only in the balance-size sentence, not on the standard read (R2-X6) |
| 7 | R "12 calendar months" | "before the … date" against a DSL window that includes that date (R2-X7, four policies) |
| 8 | E and Q "no CR / storage" | the negative-difference yard branch and the redemption absent-storage branch are unstated (R2-X8) |
| 9 | R "amount clause" | the posting-day storage retirement is missing from R's own overwrite, and the redemption-path re-bill is kept (R2-X9) |
| 10 | Qd "ok" | the credit is rounded inside (R2-X10) |
| 12 | "regenerated" | stale or false proof sentences remain (T1-XF12; the T0-S1 and T1-S1 grounding checks) |

- Seed claim O-12, "seeded histories follow the extended schedules": the dates and good-through dates do, but the quote amounts are the base formula (T0-S1, T1-S1).
- The pairwise method table's R line (Saturday 50.00 against Sunday 18.00) is exactly the R2-F2 realism defect.

## closing_checklist (revision_2)

- Files: 0.md, 1.md and _difficulty.md each carry revision_2. Round-1 text is untouched.
- Scopes are disjoint and complete. Each tree's shape, edge kinds, unmet-at-opening status, customer write and acyclicity hold. Every factor bears weight against an honest baseline, and every all-baseline figure differs from gold.
- Both blind derivations equal GT on every argument.
- All ten round-1 charter REDs and both task-level round-1 REDs are closed, with no regression of a closed item.
- **Not closed.** New charter-wide REDs are R2-X1, R2-X6, R2-X7, R2-X8, R2-X9, R2-X10, R2-F1 and R2-F2. New task-level REDs are T0-S1, T1-S1 and T1-XF12.
- Gates: snapshot_r2 is green except the expected pre-render traceability and documents items.

task0=SOURCE-POLICY+SOURCE-FACTOR+SOURCE-TASK RED task1=SOURCE-POLICY+SOURCE-FACTOR+SOURCE-TASK RED
charter=R2-X1,R2-X6,R2-X7,R2-X8,R2-X9,R2-X10,R2-F1,R2-F2
VERDICT revision_2: task0=SOURCE-POLICY+SOURCE-FACTOR+SOURCE-TASK RED task1=SOURCE-POLICY+SOURCE-FACTOR+SOURCE-TASK RED charter=R2-X1,R2-X6,R2-X7,R2-X8,R2-X9,R2-X10,R2-F1,R2-F2

## revision_3

### charter_global_frozen (revision_3)

- Re-audit round 3, same independent auditor.
- Gating line: `REWORK round 3: gates 8/8 green`. Passed.
- Gate snapshot: `.audit_views/policy/preowned_repossession_recovery/snapshot_r3.txt` (2026-10-16T00:20:30Z). Every gate is OK; the only exceptions are the expected pre-render traceability (tool names) and `documents: 0` items.
- Frozen hashes:
  - charter e76db9fb5d92c608 (round 2: 3446bcbf4d6c49ff, changed, so every section below is re-derived)
  - task_tools.py 00e892251c847a86 (unchanged since round 2, so the round-2 tool conclusions in § action_binding_and_uuids (revision_2) carry forward on that hash)
  - views 0.json 45dd8e11fabac2af and 1.json 7ccf8fab85138904 (both changed)
- The base copy is still identical to the blueprint.
- Nothing below derives from round-3 GT, worklog.md, or the round-3 closure claims; none had been opened when this section was written.

### rule_compute_equivalence and XF sweep (revision_3)

Mechanical check: every compute_basis, policy_source, replaced_by and baseline.rule string is quoted verbatim in its own rule, and every superseded_clause is verbatim in the base. No misses.

XF recipe, every point against every policy, after the round-3 changes:

| point | result |
|---|---|
| 1 assembly sentences | Settlement is now generic: "a schedule that replaces a figure of the standard does so first, percentage points the schedules add are added to the percentage next, the percentage is never below the minimum …". The reinstatement scope sentence names no factor quantity, and each reinstatement ladder now carries "discretionary" in its own tiers. The other five policies are unchanged and generic. **No member.** |
| 2 non-commuting order | Sale notice: "the anchors are compared before any days are added, and the move off a weekend comes last". The compute moves `scheduled_offset_days` off the weekend after the sum. Settlement order is stated. The rest is unchanged. **No member.** |
| 3 factor independence | Reinstatement factors read the plain `state_right_running` and `installment`. `posting_storage` and `projected_storage` are plain bindings consuming one factor output times a plain daily amount. Sale-notice `result` reads the plain `scheduled_offset_days`. **No member.** |
| 4 ownership | The daily storage amount is defined inside the projected-storage (redemption) and posting-days (reinstatement) sentences. **No member.** |
| 5 compute_basis | Verbatim (script). **No member.** |
| 6 ties | Settlement standard: "(the first one listed where two share a date, and nothing where none stands)". The reinstatement and redemption daily amount, lot intake, and the first-listed lease/retail reads are all stated. **No member.** |
| 7 counting | Every twelve-month window now reads "after the same calendar day twelve months before the … date, up to and including the … date". That equals the DSL's `0 <= MONTHS(d, NOW) < 12`. Spot-checked: the anniversary is excluded, the day after it is included, and NOW is included. Posting days are "two days later / one day later". The sale-notice weekend move matches `DAYS('2024-01-07', ·) % 7`. **No member.** |
| 8 branches | Transport: "a contract whose most recent condition report is dated on or before the repossession date … carries no holding charge". Redemption and reinstatement: "or at the daily storage fee for the tier where that charge covers no billable day or no storage charge is on record". Settlement: "nothing where none stands", which is a quote amount of 0. The fee exclusions are "never more than the fees due balance", matching `MN(fees_due, …)`. **No member.** |
| 9 base clauses | Every policy that retires the base storage sentence (deficiency, release storage, redemption, reinstatement) now declares it in its own `overwrite`, names its scope, and restates "Storage is billed for each day of a repossession only once … any other day … counting from the repossession date". **New member: R3-X9.** |
| 10 rounding | The deficiency credit is no longer rounded inside. Reinstatement: the half installment and reserve share are rounded as stated; the daily amounts are not rounded, as the rule implies; one RND at the end. **No member.** |
| 11 tools | Tools unchanged since round 2. **No member.** |
| 12 proof text | Checked after the reveal (task files). |

### closure of revision_2 charter REDs (verified on disk)

| id | status | evidence |
|---|---|---|
| R2-X1 | closed | XF 1 row above |
| R2-X6 | closed | XF 6 row above |
| R2-X7 | closed | All four windows restated; compute unchanged and now equal to the stated window |
| R2-X8 | closed | Both branches stated |
| R2-X9 | closed for (a) and (b) | The reinstatement declares its own storage overwrite. The "billed only once" sentence excludes days billed through a statement date and days collected in a redemption or reinstatement. A remaining class member is R3-X9 below. |
| R2-X10 | closed | `MX(0, sale_expense - gross_sale * expense_share_pct / 100)` has no inner RND |
| R2-F1 | closed | The yard hold is now tiered at 25.00 a night up to 7, then 15.00 a night: 7 nights 175.00, 8 nights 190.00, 30 nights 520.00. It is monotone, and "proportional vs two-rate tiered" is still an honest method pair. |
| R2-F2 | closed | Posting days are now a parameter factor (2/1/0). Each day is priced at the same daily amount whatever the call day. |

Round-2 observations:
- Closed: O-r2-1 (exclusions capped at fees due), O-r2-2 (sale moved off weekends), O-r2-3 (the rule now says the reinstatement is "recorded when the funds are sent and take effect on the posting date").
- Remaining: O-r2-4 (back-dated transport in task 0, inherent in a late booking), O-r2-5 (reconditioning estimate on a redemption), O-r2-6 (state_gate gates are field paths).

### factor_ladders (revision_3)

- Factor counts are unchanged: transport 4 (3P/1M), deficiency 5 (4/1), settlement 5 (4/1), storage 4 (3/1), redemption 4 (3/1), sale notice 5 (4/1), reinstatement 4 (3/1).
- Reinstatement changes:
  - The method is now retail_relationship_reserve: "read from the other account: that retail contract's own past-due amount" against "half of this contract's monthly installment". These are different sources and algorithms, so the method is honest.
  - weekend_posting_days is now a parameter.
- Cross-difficulty factors: lease (deficiency, settlement) and retail (sale notice, reinstatement).
- Multi-source factors: settlement_base_rule (task 0); pay-ahead, free days and established customer (task 1).
- Ladders stated in the rule = compute; fall-through = baseline.
- Realism observation O-r3-1: the reserve's 15–29-day tier (the other contract's own arrears) can fall below its under-15-day tier (half of this installment) when the retail installment is small. Example: retail past due 300.00 against 415.72. This depends on the amounts, not the structure. Task 1 is not inverted (512.87 > 415.72).

### findings (revision_3)

**R3-X9, SOURCE-POLICY RED (XF 9 / check 1, remaining member of the storage-day class): the retained base storage text counts agency-yard nights as lot storage days, but the transport charge has already billed those nights.**
- The retained text appears identically in the replaced_by of four policies: deficiency (storage overwrite), release storage, redemption (storage overwrite) and reinstatement (storage overwrite). It reads: "Storage is billed for each day of a repossession only once: days billed through a statement date, days collected in a redemption figure or a reinstatement amount, and days counted into a deficiency quote are not billed again, and any other day the vehicle is stored beyond the free days is charged at the daily storage fee, counting from the repossession date to the release or sale date".
- The exclusion list omits the nights before lot intake that the transport charge bills. The transport rule says "the agency's holding of the vehicle before lot intake is charged by the nights it held the vehicle … at the yard rate".
- The release-storage rule itself treats those nights as not storage: "the agency held the vehicle until then and billed that holding on its transport charge, so the stored days are counted from the day after the lot-intake date".
- Same situation, two counts, shown on task 0's world:
  - Repossession 2026-06-28, lot intake 2026-06-30, sale 2026-07-28.
  - The retained base text counts the sale-time storage from the repossession date: 30 − 3 free = 27 days, 486.00. That is the seeded row `df52a923…`.
  - The charter's own yard/lot split counts it from the day after lot intake: 28 − 3 = 25 days, 450.00.
  - The difference is the 2 yard nights. The gold transport charge bills those nights at 50.00, and the seeded storage bills them again at 36.00.
- Consequence for task 0 is demonstrated in 0.md: the deficiency figure is unchanged (3349.01), but the settlement is 2653.21 against 2640.61.

task0 / task1 verdicts: see the task files' revision_3 sections.

### reworker claims against the artifacts (revision_3, after reveal)

- Every round-3 closure claim for R2-X1, X6, X7, X8, X9(a), X10, F1, F2, T0-S1, T1-S1 and T1-XF12 matches the artifacts.
- The R2-X9(b) claim, "only other days fall to the base charge", holds for the listed sibling cases. It leaves R3-X9: the agency-yard nights, and whether 0-day statement coverage counts as "billed through a statement date".
- The T0 seed claim "Grounding sentences rewritten" leaves the false `df52a923…` grounding sentence (T0-XF12).

## closing_checklist (revision_3)

- Revision_3 is appended to 0.md, 1.md and _difficulty.md. Earlier revisions are untouched.
- Scopes are disjoint and complete. Both trees hold, both blind derivations equal GT, and every factor bears weight against an honest baseline.
- **Not closed.**
  - Charter-wide R3-X9 (SOURCE-POLICY) is open.
  - Task 0 carries its consequence (settlement 2653.21 against 2640.61) and the proof-text red T0-XF12.
  - Task 1 passes.
- Gates: snapshot_r3 is green, apart from the expected pre-render items.

task0=SOURCE-POLICY+SOURCE-TASK RED task1=PASS
charter=R3-X9
VERDICT revision_3: task0=SOURCE-POLICY+SOURCE-TASK RED task1=PASS charter=R3-X9

## revision_4

### charter_global_frozen (revision_4)

- Re-audit round 4, same independent auditor.
- Gating line: `REWORK round 4: gates 8/8 green`. Passed.
- Gate snapshot: `.audit_views/policy/preowned_repossession_recovery/snapshot_r4.txt` (2026-10-16T01:11:02Z). Every gate is OK; the traceability tool-name item is expected. validate_scenario now counts 169 documents (other products rendered); its preowned "required document not found" errors are expected before render.
- Frozen hashes:
  - charter 67f02aa954dca02d (round 3: e76db9fb5d92c608, changed, so re-derived below)
  - task_tools.py 00e892251c847a86 (unchanged since round 2; tool conclusions carry forward on that hash)
  - views 0.json 6341668d8e16af5b and 1.json 62f12c911fade72b
- The base copy is still identical to the blueprint.
- Nothing below derives from round-4 GT, worklog.md, or its claims; none had been opened when this section was written.
- Mechanical sweep: every compute_basis, policy_source, replaced_by and baseline.rule string is quoted verbatim in its own rule, and every superseded_clause is verbatim in the base. No misses.

### closure of revision_3 charter RED (verified on disk)

| id | status | evidence |
|---|---|---|
| R3-X9 | closed | One common storage tail now sits identically in the rule and storage overwrite of deficiency, release storage, redemption and reinstatement (8 copies). It reads: "Storage is billed only for days the vehicle is on the storage lot, and each such day only once. The lot days of an involuntary recovery whose most recent condition report is dated after the repossession date run from the day after that lot-intake date, the nights before it being the agency's holding, billed on its transport charge and never as storage … A lot day up to and including the latest statement date on which a storage charge was billed is billed by that charge, whatever the charge came to … Every other lot day through the release or sale date is charged at the daily storage fee once the free days for the tier, less any free days an earlier storage charge for the same repossession already set against its stored days, are used up". Both facets are decided: yard nights are never storage, and a 0.00 statement charge still covers its days. Task 0's seeded sale storage is now 25 days / 450.00, which is 07-01..07-28 = 28 lot days less 3 free days. |

### XF sweep (revision_4, every point × every policy)

The changed text is the storage tail (all four storage policies) and the reinstatement relationship reserve. The other text and the computes match revision_3, whose XF table stands. Results on the changed text:

| point | result |
|---|---|
| 1 | The tail names no factor quantity. The reserve sentence is the factor's own. No member. |
| 2 | The tail is not additive. In the reserve, "whichever is larger" sits inside one tier. No member. |
| 3 | The reserve reads its own retail bindings plus the plain `installment`. No member. |
| 4–6 | No new read, so no tie is needed. No member. |
| 7 | Lot days "from the day after that lot-intake date … through the release or sale date" is a stated convention. No member. |
| 8 | The tail governs base billing at release or sale, outside these tools, and says so ("billed when the vehicle leaves the lot"). No member. |
| 9 | The tail is restated in each retiring policy's own overwrite. No member. |
| 10 | The reserve: "rounded to the cent, whichever is larger" equals `MX(retail_past_due_amount, RND(installment / 2, 2))`. No member. |
| 11 | Tools unchanged. No member. |
| 12 | Checked per task after the reveal. |

### findings (revision_4)

**R4-F1, SOURCE-FACTOR RED (a ladder tier coincides with the next tier on a reachable domain).** Reinstatement `retail_relationship_reserve`:
- Tier 1 (retail 15–29 days past due): "that retail contract's own past-due amount or half of one monthly installment of this contract, rounded to the cent, whichever is larger". Compute: `MX(retail_past_due_amount, RND(installment / 2, 2))`.
- Tier 2 (fewer than 15 days): "half of one monthly installment of this contract, rounded to the cent".
- Whenever the retail arrears are no larger than half this contract's installment, tier 1 selects exactly tier 2's value. Demonstration: a 20-days-past-due retail contract with a 300.00 past-due amount, against a 831.44 pre-owned installment, gives 415.72 under both tiers.
- That is a common case: one retail installment at 15–29 days against a larger used-truck installment. On that domain the 15-day line divides no customers.
- This is the ladder-distinctness defect class (two tiers selecting the same value), introduced by the round-4 change that cured the inversion in observation O-r3-1. It is the only member: no other ladder of the charter has a tier built from another tier's value.
- Bears on: the charter. Task 1 sits on tier 2 (14 days), so its scored value does not move.

### reworker claims against the artifacts (revision_4, after reveal)

- R3-X9 claim: matches. The storage tail is one string carried in 8 places, and task 0's seed and fees due were re-derived.
- T0-XF12 claim: matches.
- O-r3-1 claim: the reserve is now "monotone in the retail days past due", as claimed. But the "whichever is larger" floor makes the 15–29-day tier equal the <15-day tier wherever the retail arrears are no larger than half this installment (R4-F1). The claim's pairwise-method line ("larger of retail past-due and half installment / half installment") states the coincidence itself.
- Retail 14/15 boundary claim: matches. Retail is now 10 days past due with consistent dates, and the persona was updated.
- O-r2-4, O-r2-5 and O-r2-6 are carried as observations.

## closing_checklist (revision_4)

- Revision_4 is appended to all three files.
- Both tasks: blind derivations equal GT, trees hold, every factor bears weight, seeds and proof text are consistent. **Both tasks PASS.**
- Charter is not CLEAN. One open charter-wide RED, R4-F1 (SOURCE-FACTOR, reinstatement reserve tiers coincide on a reachable domain). No other XF member was found on any policy.
- Gates: snapshot_r4 is green apart from the expected pre-render items.

task0=PASS task1=PASS
charter=R4-F1
VERDICT revision_4: task0=PASS task1=PASS charter=R4-F1

## revision_5

### charter_global_frozen (revision_5)

- Re-audit round 5, same auditor.
- Gating line: `REWORK round 5: gates 8/8 green`. Passed.
- Gate snapshot: `snapshot_r5.txt` (2026-10-16T04:16:16Z). All gates are OK; the remaining items are the expected tool-name traceability miss and preowned documents not yet rendered.
- Frozen hashes:
  - charter 1b298723434e4c95 (round 4: 67f02aa954dca02d, changed)
  - tools 00e892251c847a86 (unchanged)
  - views: 0.json e5caacd725c39ed3 (changed), 1.json 62f12c911fade72b (unchanged since revision_4)
- The base copy is identical to the blueprint.
- Mechanical sweep: every compute_basis, policy_source, replaced_by and baseline.rule string is quoted verbatim in its own rule, and every superseded_clause is verbatim in the base. 0 misses.
- Written before the round-5 worklog claims and GT were opened.

### closure and changed text (revision_5)

**R4-F1: closed.**
- The 15–29-day reserve tier is now "half of one monthly installment of this contract, rounded to the cent, plus that retail contract's own past-due amount". Compute: `RND(installment / 2, 2) + retail_past_due_amount`.
- A retail contract 15–29 days past due always has a positive past-due amount, so tier 1 is always above tier 2 (half installment) and above the fall-through (0).
- The tiers are distinct on the whole reachable domain and monotone in the retail days past due. The method label is still honest: tier 1 reads the other account; tier 2 derives from this contract only.

**Free-days disagreement the reworker found: aligned.**
- The shared storage tail is one string across 8 copies (rule and storage overwrite of deficiency, release storage, redemption and reinstatement). It now reads "the free days follow the recovery history exactly as for a storage charge through a statement date (none for an involuntary recovery of a contract that shows an earlier reinstatement payment, the surrender free days for a voluntary surrender of a contract that shows no reinstatement payment, the free days for the tier for any other recovery), less any free days an earlier storage charge for the same repossession already set against its stored days".
- Statement-time and sale-time storage no longer give the same vehicle different free days.
- Task 0's seed follows the alignment. Sale storage `df52a923…` is now 28 lot days (07-01..07-28) × 18.00 = 504.00, with 0 free days for this repeat involuntary recovery. Fees due are 1044.00 = 75 + 400 + 65 + 504.

### XF sweep (revision_5, every point × every policy)

Unchanged text keeps its revision_3 / revision_4 results. On the changed text:

| point | result |
|---|---|
| 1, 2, 3 | The reserve sentence is the factor's own and sits inside one tier. No member. |
| 5–8, 10, 11 | The reserve's RND sits on the half installment, as stated ("rounded to the cent, plus …"). No new read. No member. |
| 9 | The tail is restated in each retiring policy's own overwrite. No member. |
| **4 ownership** | **Member: R5-X4.** |

### findings (revision_5)

**R5-X4, SOURCE-POLICY RED (XF 4: a rule phrase defines a quantity as another policy figures it, and a factor's ladder is carried outside its own policy).**
- The tail says sale-time free days "follow the recovery history exactly as for a storage charge through a statement date", then restates that schedule's three free-day tiers. Those tiers are the ladder of `preowned_ext_release_storage_charge.factors[repeat_recovery_free_days]`.
- XF 4: "No rule phrase defines a quantity 'as another policy figures it'". In the release-storage policy itself the reference is to its own schedule. In three other policies, the phrase both defines the quantity by another policy's figure and copies a declared factor's full ladder into their rules, where the render must carry it in their hubs.
- Every member:
  - `preowned_ext_deficiency_quote`: rule, and storage overwrite replaced_by
  - `preowned_ext_redemption_quote`: rule, and storage overwrite replaced_by
  - `preowned_ext_reinstatement_funds`: rule, and storage overwrite replaced_by
- Consequence: the three policies' published text carries another policy's factor ladder, so it is no longer "carried in full in its own document … referenced by nothing". A future change to that factor's tiers would have to be mirrored in six other places, or the KB would state two free-day ladders for the same storage.
- No scored figure moves in either task.

### reworker claims against the artifacts (revision_5, after reveal)

- R4-F1 claim: matches. The tiers are distinct and monotone, and the method is honest.
- Free-days claim: matches. Statement-time and sale-time free days now agree, and task 0's seed (504.00 / 28 days, fees due 1044.00) and every proof figure follow.
- The claim lists XF 4 as fine for every policy. The aligning sentence itself introduces R5-X4: it defines the sale-time free days "exactly as for a storage charge through a statement date" and copies the `repeat_recovery_free_days` ladder into the deficiency, redemption and reinstatement rules and their overwrites.

## closing_checklist (revision_5)

- Revision_5 is appended to all three files.
- Both tasks PASS: blind derivation equals GT, trees hold, every factor bears weight, and seeds and proof text are consistent.
- The charter is not CLEAN. R5-X4 (SOURCE-POLICY, XF 4) is open with 3 policies (6 copies) as members. No other XF member was found.
- Gates: snapshot_r5 is green apart from the expected pre-render items.

task0=PASS task1=PASS
charter=R5-X4
VERDICT revision_5: task0=PASS task1=PASS charter=R5-X4

## revision_6

### charter_global_frozen (revision_6)

- Re-audit round 6, same auditor.
- Gating line: `REWORK round 6: gates 8/8 green`. Passed.
- Gate snapshot: `snapshot_r6.txt` (2026-10-16T05:14:27Z). All gates are OK; the remaining items are the expected tool-name traceability miss and preowned documents not yet rendered.
- Frozen hashes:
  - charter 648fcef1e0e01976 (round 5: 1b298723434e4c95, changed)
  - tools 00e892251c847a86 (unchanged)
  - views 0.json e5caacd725c39ed3 and 1.json 62f12c911fade72b (both unchanged since revision_5)
- The base copy is identical to the blueprint.
- Mechanical sweep: 0 verbatim misses across compute_basis, policy_source, replaced_by, superseded_clause and baseline.rule.
- Written before the round-6 worklog claims and GT were opened.

### closure of R5-X4 (verified on disk)

- The shared storage text still sits in the rule and storage overwrite of all four storage policies.
- The phrase "exactly as for a storage charge through a statement date" is gone. The sale-time free days are now stated on their own: "The free days for that charge follow the recovery history: an involuntary recovery of a contract that shows an earlier reinstatement payment has none, a voluntary surrender of a contract that shows no reinstatement payment has the surrender free days, and any other recovery has the free days for the tier, in each case less any free days an earlier storage charge for the same repossession already set against its stored days."
- No rule phrase now defines a quantity as another policy figures it.
- The sale-time charge's free days are a quantity of the retained base charge, which falls outside every tool, and no factor uses it. It is the still-in-force part of the retired base clause, and XF 9 requires each retiring policy to restate it.
- **R5-X4 is closed.**

Observation O-r6-1, for the renderer and KB auditor:
- The base charge's three free-day tiers have the same values as the release-storage factor `repeat_recovery_free_days`, and the shared text sits in every storage hub, including release storage's own.
- The render must keep that text scoped to "that charge" (the release/sale charge). A statement-storage reader must still get its free days only from the factor document.
- This affects placement only; it is not a policy defect.

### XF sweep (revision_6)

- The only changed text is the free-days sentence above.
- All twelve points re-run on it: no member found.
  - It names no factor quantity (1).
  - Its order is stated (2): "in each case less …".
  - It reads no factor (3).
  - It refers to no other policy (4).
  - No tie, count or round is involved (6, 7, 10).
  - It is restated in each retiring policy's own overwrite (9).
- Every other policy text and compute is unchanged; the recomputed figures, sensitivities and all-baselines equal revision_5 exactly. The revision_5 results stand for all other points.

### reworker claims against the artifacts (revision_6, after reveal)

- R5-X4 claim: matches.
  - The phrase is gone from the 8 copies.
  - The deficiency quote, redemption and reinstatement each declare `surrender_free_days: 7`, so the surrender free days named in their own text are their own parameter. It has the same value as release storage's, and no compute reads it.
  - The two remaining sibling references ("a redemption quote is figured under the redemption-quote schedule" / "a deficiency quote … under the deficiency-quote schedule") are XF 9 scope exclusions for a quote the other policy owns. They do not define a quantity the citing policy uses. Accepted.
- No figure moved. GT equals revision_5 and this re-derivation.

## closing_checklist (revision_6)

- Revision_6 is appended to all three files.
- Every red light from revision_1 through revision_5 is closed, with no regression found.
- Both tasks PASS: blind derivation equals GT, trees hold, every factor bears weight against an honest baseline, and seeds and proof text are consistent.
- Every XF recipe point on every extended policy has no member.
- Gates: snapshot_r6 is green apart from the expected pre-render items (traceability of unlock tool names; preowned documents not yet rendered).
- Observations carried for downstream work only (not grounds for rework):
  - O-r2-4: back-dated transport by design.
  - O-r2-5: reconditioning estimate on a redemption.
  - O-r2-6: state_gate gates as table.field.
  - O-r6-1: render scoping of the sale-time free-days sentence.

task0=PASS task1=PASS
charter=CLEAN
VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN

## revision_7

### charter_global_frozen (revision_7)

- Re-audit round 7, same auditor.
- Gating line: `REWORK round 7: gates 8/8 green`. Passed.
- Gate snapshot: `snapshot_r7.txt` (2026-10-16T09:55:52Z). All gates are OK; the remaining items are the expected tool-name traceability miss and preowned documents not yet rendered.
- Frozen hashes:
  - charter e41acbe37a6d82a5 (changed)
  - task_tools.py 375d8b7d5ca18f34 (changed for the first time since round 2, so the tool conclusions are re-derived below)
  - views 0.json e5caacd725c39ed3 and 1.json 62f12c911fade72b (both unchanged)
- This round's input is the renderer's stop report `audits/render_source/preowned_repossession_recovery/render_r1.md`, read in full: 4 mismatches and 4 observations.
- Auditor's note: my revision_6 PASS/CLEAN missed all four mismatches. Each is an XF 8 member (an unstated branch, or a format the tool rules out) that I should have caught.
- Mechanical sweep: 0 verbatim misses. The base copy is identical to the blueprint.
- Written before the round-7 worklog claims and GT were opened.

### renderer items against the source (verified on disk)

| item | status | evidence |
|---|---|---|
| M1: repeat_recovery zero-fee case | closed | The rule now reads "a single agency fee, or none posted, carries none". This matches the compute's `else 0.0`. |
| M2: transport date with no report for this recovery | closed | The charge is now "dated the lot-intake date, that is the date of the condition report taken when the vehicle reached the storage lot for this recovery, the most recent condition report, dated on or after the repossession date … no transport charge is owed while no condition report dated on or after the repossession date is on record". The case is now outside the tool's scope, so no `service_date` can predate the repossession. This agrees with the deficiency gate "dated on or after its repossession date". |
| M3: report dated on the repossession date | closed | The lot test is now "on or after" in all three readers: sale notice (`lot_intake_date >= F('repossession_date')`, with the agency-yard case worded "with no condition report dated on or after the repossession date"), redemption projected storage (`>=`, "dated on or after"), and transport ("taken to the lot on the day of the repossession" carries no holding charge). Release storage keeps `>` for its lot-intake anchor. That is equivalent on the equal date: the day after intake = the day after repossession. |
| M4: good_through_days of 0 | closed | The tool now accepts "`good_through_days` … a non-negative integer", and the body does `add_days(today, 0)`. The last day of the period (quoted and good through the same day) is now in-format. |
| Obs: which sale date | closed | The deficiency rule says "The sale date is the sale date recorded on the contract". The settlement says "from the sale date recorded on the contract". |
| Obs: settlement posting vs base | closed, but see R7-X9 | The settlement now declares an overwrite of the base cutoff sentence: it is paid by wire from the customer's own account, "a certified-funds channel that is accepted while the contract takes certified funds only", credited when received, and a weekend wire posts on the Monday. The tool matches: channel "wire", posting date `_Cal.posting_date`, interest through the posting date. |
| Obs: reinstatement baseline | closed | `baseline.rule` now includes "less the fees a reinstatement the state period grants leaves out of its amount". It is verbatim in the rule and matches the plain `statutory_fee_exclusion` in `result`. |
| Obs: placement | renderer's own concern | No source change is needed, and none found. |

Tools (re-derived on 375d8b7d…):
- uuid8 values are unchanged.
- No body judges a prerequisite.
- Docstrings carry no example values and no ordering words.
- The settlement docstring ("dated with the posting date … the Monday when it is sent on a Saturday or Sunday … paid in full as of the posting date") matches the body.

### findings (revision_7)

**R7-X9, SOURCE-POLICY RED (XF 9: two sibling overwrites retire the same base clause, and each restates it for "every other payment" without naming the other's case).**
- Base `preowned_payment_posting`: "A payment received before payment_cutoff_time_ct Central Time on a business day posts that day; a payment received later, or on a weekend or US federal holiday, posts the next business day."
- `preowned_ext_deficiency_settlement` replaced_by: "For a settlement payment this policy takes, and only for such a payment, … the wire is credited when it is received, whatever the hour … **Every other payment received before the payment cutoff time Central Time on a business day posts that day, and one received later, or on a weekend or US federal holiday, posts the next business day.**"
- `preowned_ext_reinstatement_funds` replaced_by: "For reinstatement funds this policy takes, and only for such funds, the funds are credited when they are received, whatever the hour … **Every other payment received before the payment cutoff time … posts the next business day.**"
- The settlement text's "every other payment" covers reinstatement funds, and the reinstatement text's covers settlements. Neither names the sibling's case, which XF 9 requires ("names its own scope (and any sibling policy's case retiring the same clause)").
- Same situation, two conclusions: a reinstatement wire received Tuesday after the cutoff. The reinstatement rule says it posts that Tuesday. The settlement policy's restated base says it posts Wednesday. The mirror case holds for a settlement wire under the reinstatement policy's text.
- Members (the whole class):
  - the settlement overwrite (and its rule copy)
  - the reinstatement overwrite (and its rule copy)
- No task world sits on it: task 0 pays on a Wednesday morning, and task 1 wires on a Saturday, which both texts post on the Monday.
- Realism observation O-r7-1: "credited when it is received, whatever the hour" ignores bank wire-network cutoffs. A wire sent after the network closes is received the next business day, so the effect is the company crediting at receipt, which is plausible.

### reworker claims against the artifacts (revision_7, after reveal)

- M1–M4, the sale date and the reinstatement baseline: claims match the disk (table above).
- O-placement claim: matches. Every single-factor binding has moved into its factor's binding set: deficiency (`gross_sale`, `sale_expense`, `disposition_credit`; `storage_billed_days`, `storage_credit`; `post_sale_per_diem`), redemption (`storage_daily_amount`, `projected_storage`), reinstatement (`storage_daily_amount`, `posting_storage`), settlement (`fees_due`). A mechanical check finds every binding owned by exactly one factor and no factor binding reading another factor's binding.
- O-settlement-posting claim ("every other payment keeps the base cutoff / next business day rule (restated)"): accurate, and that restatement is the defect. Each sibling's "every other payment" sentence covers the other sibling's funds (R7-X9).
- Proof text: updated, with no stale figure.

## closing_checklist (revision_7)

- Revision_7 is appended to all three files.
- All 4 renderer mismatches are closed in the source, and the renderer's observations are resolved.
- Both tasks PASS: derivations equal GT, trees hold, factors bear weight, seeds and proof text are consistent.
- The charter is not CLEAN. R7-X9 (SOURCE-POLICY, XF 9) is open, with exactly 2 members: the settlement and reinstatement posting overwrites (each with its rule copy).
- Gates: snapshot_r7 is green apart from the expected pre-render items.

task0=PASS task1=PASS
charter=R7-X9
VERDICT revision_7: task0=PASS task1=PASS charter=R7-X9

## revision_8

### charter_global_frozen (revision_8)

- Re-audit round 8, same auditor.
- Gating line: `REWORK round 8: gates 8/8 green`. Passed.
- Gate snapshot: `snapshot_r8.txt` (2026-10-16T09:59:58Z). All gates are OK; the remaining items are the expected tool-name traceability miss and preowned documents not yet rendered.
- Frozen hashes:
  - charter 45f5b4c54d68e214 (changed)
  - tools 375d8b7d5ca18f34 (unchanged from revision_7)
  - views unchanged: 0.json e5caacd725c39ed3, 1.json 62f12c911fade72b
- The base copy is identical to the blueprint.
- Mechanical sweep: 0 verbatim misses.
- Written before the round-8 claims and GT were opened.

### R7-X9 and every multi-retirement clause (verified on disk)

All overwrites were grouped by the base sentence they retire.

| base clause | retired by | sibling cases named in each replaced_by? |
|---|---|---|
| payment_posting cutoff sentence | settlement, reinstatement | **yes, both.** Each now reads "Every payment other than a deficiency settlement wire or reinstatement funds, both of which post on the day they are received or on the Monday after a weekend as the settlement and reinstatement terms state, keeps the standard posting …". **R7-X9 closed.** |
| payoff per-diem/payoff sentence | deficiency quote, redemption quote | yes. "a redemption quote is figured under the redemption-quote schedule" and "a deficiency quote is figured under the deficiency-quote schedule". |
| repossession_charges storage sentence | deficiency, release storage, redemption, reinstatement | yes. One shared text in all four: "days billed through a statement date … collected in a redemption figure or a reinstatement amount or counted into a deficiency quote are not billed again". |
| every other retired clause (transport status, transport fee, net proceeds, settlement minimum, good-through, redemption amount, reinstatement amount) | one policy each | n/a. Each restates its out-of-scope part. |

Observation O-r8-1 (latent, not a policy conflict):
- The base good-through sentence ("… unless the requester asks for an earlier date") stays in force for deficiency quotes; only the redemption policy retires it.
- `quote_deficiency_balance_4c162eac` always writes today + 10 days.
- An earlier good-through date that a customer asks for on a deficiency quote could therefore not be recorded. No task asks for one.

### renderer stop report render_r1.md (re-checked)

All items remain closed on disk:
- M1: "a single agency fee, or none posted, carries none".
- M2: "no transport charge is owed while no condition report dated on or after the repossession date is on record".
- M3: lot test "on or after" in the sale notice and redemption (compute `>=`).
- M4: tool `good_through_days` "a non-negative integer".
- The sale date is defined in both the deficiency quote and the settlement.
- The reinstatement baseline includes the state-period exclusion.
- Factor-owned bindings: the mechanical check finds every binding owned once and no cross-factor read.

### XF sweep (revision_8)

- The changed text is the two posting replaced_bys (and their rule copies). All 12 points were re-run on them: no member. The sentence names no factor quantity, has no order, read, tie, count or round in play, and is restated with sibling naming (9).
- All other text, the computes and the tools are unchanged.
- The figures, sensitivities and all-baselines recomputed exactly as in revision_7.

### reworker claims against the artifacts (revision_8, after reveal)

- R7-X9 claim and class sweep: match. The posting tail now names both cases in all 4 copies, and the other two multi-retirement clauses already name their siblings.
- O-r7-1: kept as an observation.

## closing_checklist (revision_8)

- Revision_8 is appended to all three files.
- Every red light from revision_1 through revision_7 is closed. The renderer stop report's items stay closed. Every base clause retired by more than one policy names its sibling cases.
- Every XF recipe point on every extended policy has no member.
- Both tasks PASS: blind derivation equals GT, trees hold, every factor bears weight against an honest baseline, and seeds and proof text are consistent.
- Gates: snapshot_r8 is green apart from the expected pre-render items.
- Observations carried, not grounds for rework: O-r2-4, O-r2-5, O-r2-6, O-r6-1, O-r7-1, O-r8-1.

task0=PASS task1=PASS
charter=CLEAN
VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN
