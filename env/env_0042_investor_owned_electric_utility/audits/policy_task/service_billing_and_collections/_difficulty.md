# Policy-task audit — service_billing_and_collections / charter-global

## charter_global_frozen

- Auditor: independent policy-task auditor (did not author these artifacts); revision 1.
- Freeze time: 2026-10-07T21:27Z (written before any task's GT was revealed).
- Freeze hashes (verified with `sha256sum` against the coordinator's MANIFEST.txt, all equal):
  - `tasks/service_billing_and_collections/service.extended.yaml` = `1c0b8977d02d07acee13c40a1ca2587b061fdfcb3fd3e1bb7db76fffb88b66c3`
  - `tasks/service_billing_and_collections/task_tools.py` = `29d175fba2e559d470a61f75af6cb4a753870ce26089caa5f1b82bc3cb3b3498`
- Fields permitted: blueprint (`blueprint.yaml`, `db_schema.json`, `share_tools.py`, `products/*.yaml` of this scenario), the full extended charter, the full tool module, and the masked views `audits/views/policy_task/service_billing_and_collections/task_{0,1}.view.json` (frozen_time, user_scenario, initial_state).
- Fields masked and not read for this section: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`. No recursive search was run over the scenario or `tasks/`; no `/tmp` file was read.
- Entry conditions (Step 0): the coordinator supplied the gate snapshot (check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK with "suite depth: history_rows_max=88(>= 8) branches_max=60(>= 5)"; check_grounding GROUNDING OK; check_cache_diff INFO; check_cross_fire SCOPE OK; check_traceability deferred because the KB is not yet published), the masked views and their hashes. Inputs complete except the deferred traceability gate, recorded here as noted rather than as a problem of this audit.
- Base copy: lines 1-1723 of the extended file are byte-identical to `blueprint/products/service.yaml` (`diff` shows only the appended `extended_policies` banner), and every top-level key of the base section parses equal to the blueprint product.

Policies in the charter (7 extended): `service_ext_late_charge_assessment` (LC), `service_ext_auto_sustained_outage_credit` (SOC), `service_ext_reconnection_card_payment` (CP), `service_ext_reconnection_order_charge` (RO), `service_ext_prior_balance_transfer_settlement` (PBT), `service_ext_auto_chronic_outage_credit` (COC), `service_ext_notice_avoidance_bank_draft` (BD).

### policy_conflict_scan

Prerequisite graph read from the charter: RO -> CP (state_gate); CP -> LC (value_input), CP -> SOC (value_input); BD -> PBT (value_input), BD -> COC (value_input). Two disconnected trees: {RO, CP, LC, SOC} and {BD, PBT, COC}. The coordinator-claimed scope (11 service event types) is covered: LC (late payment charge), SOC/COC (outage credit), CP/BD (service_payment), RO (reconnection + reconnection charge), PBT (program debit/credit). Scope exclusivity across M=2 can only be confirmed against `charter_scope` after the reveal; from the masked views, task 0's world (disconnected RS agreement, outage at the address) instantiates the first tree and task 1's world (open GS agreement + closed GS agreement + outage history) the second, so the 7 policies split 4 + 3 with no overlap.

Overlaps examined (subject, trigger, eligibility, time anchor, parameters, terminal state, cross-category reads):
- LC vs base `service_late_payment_charge_rule`: same subject; LC narrows the object to "the most recent bill" (base charges any bill past grace). Not declared, but no world in this difficulty has an uncharged older past-grace bill (task-level check), so recorded as observation O-1.
- SOC vs base `service_outage_credit_rule`: request -> automatic posting declared; base claim window sentence ("The credit must be requested no later than the claim window ...") is inherited unchanged and stays meaningful as a posting limit. SOC narrows to "the most recent outage record" (base: any qualifying record in the claim window) — undeclared narrowing, observation O-2.
- COC vs base `service_chronic_outage_credit`: threshold / attachment / on-request sentences declared; "at most one per account in any 12 months" inherited.
- CP and RO vs base `service_reconnection_rule` — **conflict F-1** below (alternatives and non-card payments).
- BD vs base `service_payments_and_returns` returned-payment restriction — **conflict F-2** below.
- BD vs base `service_agg_prior_balance_transfer` "past due only after that bill's due date" — declared overwrite; unique after replacement.
- PBT vs base `service_agg_prior_balance_transfer` two-entry and amount sentences — declared; timing eligibility `final_bill_aged` inherited (relevant to F-4).
- Cross-category reads: SOC reads meter interval length (meter variant parameter), RO reads meter remote-switch capability, `meter_field_orders` and the Residential Reestablishment Deposit, COC reads the in-service meter type. All are readable through share finders (`find_meter_installations`, `find_meter_field_orders`, `find_deposit_accounts`, `find_deposit_transactions`) plus the meter product parameters; no write crosses a category boundary.

### rule_compute_equivalence

Checked per binding against `compute_basis` and back against every rule sentence.

- LC: every binding quotes a rule sentence verbatim; the window convention ("Every count or sum over the 12, 24 or 1 calendar months before a posting takes the records dated less than that many whole calendar months before the posting date") backs `within_months`; rounding points (rated, autopay, hardship each to the cent; minimum after hardship; surcharge last) match `rated_charge`/`courtesy_charge`/`shared_charge`/`floored_charge`/`result`. Grace-ended and no-prior-charge conditions are carried by the inherited base eligibility (`grace_period_passed`, `one_charge_per_bill`), not by compute — acceptable. The `inputs.history` metadata omits the energy-assistance count and the `event_type` filter on the autopay count (metadata only, observation O-3).
- SOC: meter rounding (ceil to hour / quarter hour / as recorded), min duration, increment hours, base by cause, increment amount, tenure cap, floor division for full increments, final-only rounding — all match. Equivalent.
- CP: balance, basis by reconnections in 24 months (whole / less late charges 12+ months old / less all late charges), hardship and tenure shares, floor at zero before the shares, good-faith and returned-payment add-ons — all match. Equivalent.
- RO: restoration charge (remote / after-hours field / field standard), repeat multiplier, door-hanger visit recovery, hardship, tenure, deposit share, final-only rounding, method/timing recording — match. Two drafting gaps, observations only: `tamper_findings_24` subtracts rows with `finding='no_tampering'` of any event type from rows of `event_type='meter_tampering_finding'`, so a tampering-investigation row whose finding is `no_access` (an enum value in `db_schema.json` `meter_field_orders.finding`) would be counted as a confirmed finding although the rule counts only confirmed findings (O-4); the deposit tier says "in the calendar month before the order" while compute uses the 1-month window convention (O-5). Neither bites in task 0 (only a `no_tampering` row; deposit already `held`).
- PBT: closed balance, final unpaid, carried rate by days since final due, return multiplier, tenure forgiveness, notice collection recovery, result — match.
- COC: threshold cut by controllable causes, excess-amount tiers, load factor (AND / XOR / neither), planned-maintenance multiplier, tenure add-on, assembly order — match.
- BD: past-due balance (excludes the latest bill only when its due date is after today; transferred balance removed then re-added at its counted share), returned-payment allowance, tenure increase with cap, load margin, result — match. Boundary note: `current_not_due` treats a bill due today as past due while the rule says "whose due date has passed" (O-6; no world here sits on that boundary).

No `compute` invents a basis absent from the rule, and no rule tier is missing from compute. Every factor ladder tier is a rule sentence and a branch of its `decides` binding.

### action_binding_and_uuids

- `(target_tool, computes)`: LC (`post_late_payment_charge_a575fa01`, amount), SOC (`grant_sustained_outage_credit_20084a33`, amount), CP (`take_card_payment_dce85fc7`, amount), RO (`issue_reconnection_order_52263bc7`, reconnection_charge), PBT (`transfer_prior_balance_e8000638`, amount), COC (`grant_chronic_outage_credit_becf7e74`, amount), BD (`authorize_bank_draft_payment_056776f4`, amount). Each pair is claimed by exactly one policy.
- Owners: CP and BD `owner="user"`; the other five `owner="agent"`.
- uuid8 tails `a575fa01, 20084a33, dce85fc7, 52263bc7, becf7e74, e8000638, 056776f4`: pairwise distinct, no shared prefix, no sequence pattern — consistent with independent generation.
- Docstrings: none names another tool, none states a position in a sequence; "after_hours" appears only as an enum value. No confirmation, review or wait is added beyond the policy.
- Function bodies: no tool reads any other record to validate status, eligibility, prerequisite or amount (the module docstring says so and every body confirms: they `find` only the account(s) to update balances, then `create`/`update`). Tools never judge prerequisites.

### prerequisite_graph

| Blocked policy | problem | kind | gate | form | gate exists | resolved_by = target_tool of problem |
| --- | --- | --- | --- | --- | --- | --- |
| CP | LC | value_input | `charges_total` | state | yes (CP compute) | yes |
| CP | SOC | value_input | `credits_total` | state | yes (CP compute) | yes |
| RO | CP | state_gate | `service_reconnection_rule.reconnection_requirement_met` | state | yes (base eligibility) | yes |
| BD | PBT | value_input | `transfers_in` | state | yes (BD compute) | yes |
| BD | COC | value_input | `credits_total` | state | yes (BD compute) | yes |

- `prerequisite` is filled for all 7 (`[]` for LC, SOC, PBT, COC). Every `problem` is an extended policy id of this file, none is a base policy or itself; the graph is acyclic.
- Every `policy_source` is a verbatim substring of its own blocked policy's `rule` (verified by string search on the parsed YAML).
- All edges `form: state`; no `fallback_reason` present on any edge (correct, since none is action-form).
- `condition` restates each sentence at the same scope. `effect` on BD<-PBT ("half of it counts toward the past-due balance for an agreement with one late payment charge in 24 months") describes only one tier of the counting ladder — tailored phrasing, not authoring-viewpoint words; observation O-7.

### prerequisite_sentences

Four-point test per edge:

1. CP<-LC: "The reconnection payment amount is fixed only after the agreement carries a late payment charge for each of its bills whose grace period has ended with part of the bill unpaid." Connective "only after"; state = a late-charge row per past-grace partly-unpaid bill (record-visible: `service_charges` with `bill_id`); no tool/id/snake_case; scope equals `condition`. The only write producing a `service_late_payment_charge` row is LC's tool. Derivation: sentence -> find bills past grace with part unpaid and no charge -> LC's rule ("A late payment charge is posted on the most recent bill ... once that bill's grace period has ended with part of the bill unpaid ...") -> `post_late_payment_charge`. Scope note: the sentence covers "each of its bills", LC posts only on "the most recent bill"; an older uncharged past-grace bill would make the sentence unresolvable (observation O-1, no world consequence here).
2. CP<-SOC: "The reconnection payment amount is not fixed until the agreement carries the sustained-outage credit owed for the most recent qualifying outage record at its service address." Connective "not until"; state = sustained-outage credit row; unique writer SOC. Scope note: "most recent qualifying" vs SOC's "most recent outage record ... once that record qualifies" — if the most recent record does not qualify but an earlier one does, the sentence asks for a credit SOC never posts (O-2).
3. RO<-CP: "A reconnection order is issued only after the card payments posted to the agreement since its disconnection date add up to at least the reconnection payment amount." Connective "only after"; state = card-channel payments since `last_status_date`; unique writer CP (BD writes channel `online_bank_transfer`, not card). Single reading.
4. BD<-PBT: "The notice-avoidance amount is fixed only after every closed agreement of the customer whose final bill has stayed unpaid for the prior balance transfer period carries a balance transfer credit." Connective "only after"; state = `prior_balance_transfer` credit on each aged closed agreement; unique writer PBT. Single reading.
5. BD<-COC: "The notice-avoidance amount is not fixed until the agreement carries the chronic-outage credit owed once its outage records reach the chronic threshold." Connective "not until"; state = `chronic_outage` credit; unique writer COC. Single reading.

No rule restates a depended-on edge, no rule names a tool or another policy id, the depended-on rules (LC, SOC, CP, PBT, COC) do not restate their dependents' sentences. Base cross-problem order sentence `service_reconnection_rule` "Reconnection is ordered only after the reconnection payment requirement is met ..." is superseded in practice by RO's own sentence, which grounds the edge; no tree rests on a base sentence alone. No undeclared cross-problem order found in any extended rule.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (findings only; consequences are demonstrated in the task files):

- LC vs `service_late_payment_charge_rule`: sentences 1-3 (charged once; after grace; counting) followed; sentence 4 (amount and unpaid-portion measure) superseded and declared; sentence 5 (one per bill; fees never attract) followed; income-qualification and pending-meter-test exemptions inherited and not contradicted; open-status sentence followed. Object narrowed to the most recent bill (O-1). Disguised forms: none (the new multipliers act on the declared-replaced amount).
- SOC vs `service_outage_credit_rule`: request/min-duration sentence and formula sentence superseded and declared; exclusions, claim window, one-per-code, schedule-on-start-date, stacking followed/inherited. Vs `service_chronic_outage_credit`: no sentence touched.
- CP vs `service_payments_and_returns`: confirmation sentence superseded (the replacement is a narrower restatement, harmless); oldest-first application, restriction list (card stays accepted), assistance posting followed. Vs `service_reconnection_rule`: payment-requirement basis sentence superseded and declared (including "measured at disconnection").
- RO vs `service_reconnection_rule`: fee sentence superseded and declared. **Undeclared**: RO's "A reconnection order is issued only after the card payments posted to the agreement since its disconnection date add up to at least the reconnection payment amount" removes the base alternatives ("an active payment arrangement ... whose down payment has been received, or an active medical certification ... whose kind requires disconnected service to be restored") and the base counting of any-channel payments ("payments posted since the disconnection date") — no `overwrite` entry names either sentence (F-1).
- PBT vs `service_agg_prior_balance_transfer`: two-entry sentence and amount sentence superseded and declared; timing, period, receiving-agreement, credit-balance and refund sentences followed. Vs `service_program_postings`: no sentence superseded; program postings govern other programs' amounts, so no conflict.
- COC vs `service_chronic_outage_credit` / `service_outage_credit_rule`: threshold and attachment/on-request sentences declared; once-per-12-months inherited.
- BD vs `service_payments_and_returns`: confirmation sentence superseded. **Undeclared**: base "When service_msr_returned_payments_lookback reaches the schedule's returned_payment_restriction_count, payments through mail_check, online_bank_transfer and autopay are not accepted for returned_payment_restriction_months after the latest return" is not named, yet BD unconditionally takes an online-bank-transfer draft and prices exactly that population in its allowance ladder (F-2). Vs `service_disconnection_notice_rule`: no sentence superseded; BD's own past-due definition differs from `service_msr_past_due_balance` only in the transferred-balance treatment, which is declared via the `service_agg_prior_balance_transfer` overwrite. Vs `service_agg_prior_balance_transfer`: past-due-after-billing sentence declared.

### factor_ladders

Per policy (P = parameter, M = method; "honest" = label matches what the tiers do; MS = every non-fall-through tier is a conjunction/disjunction over distinct records; XD = cross_difficulty):

| Policy | Factor | Label | Honest? | Tiers | MS | XD |
| --- | --- | --- | --- | --- | --- | --- |
| LC | repeat_lateness_rate | P | yes | 3 | no | - |
| LC | autopay_courtesy_reduction | M | **no**: x0.8 / x0.9 / x1 on the same rated charge = a number substituted | 3 | no | - |
| LC | assistance_hardship_share | P | yes | 3 | no | - |
| LC | written_notice_surcharge | P | yes | 3 | no | - |
| SOC | qualifying_duration_measure | M | yes (ceil hour / ceil quarter / as recorded) | 3 | no | meter |
| SOC | assisted_household_minimum_duration | P | yes | 3 | no | - |
| SOC | outage_frequency_increment_hours | P | yes | 3 | no | - |
| SOC | outage_cause_base_amount | P | yes | 3 | no (single record field, disjunction of values) | - |
| SOC | repeat_equipment_failure_increment | P | yes | 3 | no | - |
| SOC | tenure_outage_credit_cap | P | yes | 3 | no | - |
| CP | reconnection_history_basis | M | yes (changes which late charges leave the basis) | 3 | no | - |
| CP | assistance_payment_share | P | yes | 3 | no | - |
| CP | tenure_payment_share | P | yes | 3 | no | - |
| CP | notice_goodfaith_addon | P | yes | 3 | no | - |
| CP | returned_payment_addon | P | yes | 3 | no | - |
| RO | restoration_path_charge | P | yes | 3 | **yes** (meter capability AND field-order finding; finding AND meter in service) | meter |
| RO | repeat_reconnection_adjustment | M | **no**: x2 / x1.5 / x1 on the restoration charge | 3 | no | - |
| RO | door_hanger_visit_recovery | P | yes | 3 | no | - |
| RO | assistance_charge_share | P | yes | 3 | no | - |
| RO | tenure_charge_share | P | yes | 3 | no | - |
| RO | reestablishment_deposit_share | P | yes | 3 | no (tier 1 single condition) | deposit |
| PBT | final_bill_carried_rate | P | yes | 3 declared, **2 reachable** (F-4) | no | - |
| PBT | returned_payment_carried_transform | M | **no**: x2 / x1.5 / x1 before rounding | 3 | no | - |
| PBT | closed_tenure_forgiveness | P | yes | 3 | no | - |
| PBT | closed_notice_collection_recovery | P | yes | 3 | no | - |
| COC | controllable_cause_threshold | P | yes | 3 | no | - |
| COC | chronic_excess_amount | P | yes | 3 | no | - |
| COC | three_phase_load_factor | P | yes | 3 | **yes** (bill demand AND/XOR meter type) | meter |
| COC | planned_maintenance_adjustment | M | **no**: x2 / x1.5 / x1 after the load factor | 3 | no | - |
| COC | tenure_chronic_addon | P | yes | 3 | no | - |
| BD | late_history_transfer_count | M | **no**: coefficient 1 / 0.5 / 0 on the transferred balance | 3 | no | - |
| BD | returned_payment_allowance | P | yes | 3 | no | - |
| BD | tenure_allowance_increase | M | **no**: x1.2 / x1.1 / x1 on the allowance (the cap binds in no tier more than in the fall-through, since every allowance is already at most one cent under the minimum) | 3 | no | - |
| BD | peak_demand_load_margin | P | yes | 3 | no | - |

Counts (declared / honest): LC 4 factors, 3 P, 1 M declared / **0 honest M**; SOC 6, 5 P, 1 M / 1 honest M; CP 5, 4 P, 1 M / 1 honest M; RO 6, 5 P, 1 M / **0 honest M**; PBT 4, 3 P, 1 M / **0 honest M**; COC 5, 4 P, 1 M / **0 honest M**; BD 4, 2 P, 2 M / **0 honest M**. All counts are within 4-6; every computation has at least 2 honest P.

Distinct outcomes per ladder: no two tiers of any ladder select the same value or method. Every tier (condition and value/method) is stated in the owning `rule` and implemented in `compute`. Every `decides` names an input, never `result`; binding sets within each policy are disjoint. Every factor's `baseline` equals its fall-through tier and the policy `baseline.rule` (checked factor by factor; e.g. PBT `carried_rate: '0'` agrees with baseline.rule "The transfer amount is that balance, rounded to the cent", which carries no carried charge). Every `baseline.rule` sentence occurs verbatim in its `rule`, and every `baseline.params` key is a schedule parameter.

Conditions that hold of every customer reaching the write: PBT `final_bill_carried_rate` (F-4). CP `notice_goodfaith_addon` and RO `door_hanger_visit_recovery` were checked for the same defect: every reconnection follows a written notice and a final notice, but their fall-through tiers ("one or none") stay reachable at "one", so their ladders stay three-tier.

Per-tree MS/XD availability: tree {RO, CP, LC, SOC} has MS via RO `restoration_path_charge` and XD via SOC (meter), RO (meter, deposit). Tree {BD, PBT, COC} has MS and XD via COC `three_phase_load_factor` (meter).

### findings

**F-1 — SOURCE-POLICY RED (charter-global; bears on task 0 — demonstration in task_0.md).** Symptom: RO's gate removes base alternatives and non-card payments without declaration. Root cause: RO `overwrite` names only the fee sentence of `service_reconnection_rule`. Evidence: base rule "A disconnected agreement is reconnected when one of the following holds. Reconnection is ordered only after the reconnection payment requirement is met or an alternative listed below applies. The payment requirement is met when payments posted since the disconnection date ... The alternatives are an active payment arrangement on the agreement whose down payment has been received, or an active medical certification for the agreement whose kind requires disconnected service to be restored." vs RO rule "A reconnection order is issued only after the card payments posted to the agreement since its disconnection date add up to at least the reconnection payment amount." Demonstrated consequence (same situation, two conclusions): a disconnected RS agreement with an active payment arrangement whose down payment was received and no card payment since disconnection — base: reconnect now; RO: no order until card payments reach the amount. Likewise, a customer whose energy-assistance-agency payment since disconnection covers the amount — base counts it, RO does not. Affected: `service.extended.yaml` `service_ext_reconnection_order_charge.rule`/`overwrite`.

**F-2 — SOURCE-POLICY RED (charter-global; bears on task 1 — demonstration in task_1.md).** Symptom: BD takes an online-bank-transfer draft unconditionally where base refuses that channel. Root cause: BD's `overwrite` names only the confirmation sentence of `service_payments_and_returns`. Evidence: base "When service_msr_returned_payments_lookback reaches the schedule's returned_payment_restriction_count, payments through mail_check, online_bank_transfer and autopay are not accepted for returned_payment_restriction_months after the latest return" vs BD "the customer authorizes a one-time bank draft for the notice-avoidance amount ... and the draft is posted that day", plus BD's ladder tier "The allowance under the notice minimum is nothing when two or more payments on the agreement were reversed as returned unpaid in the 24 calendar months before the payment" (the tool posts channel `online_bank_transfer`). Demonstrated consequence: a GS agreement with two returned payments in the last 12 months — base: the draft is not accepted; BD: the draft is posted at allowance 0. Affected: `service_ext_notice_avoidance_bank_draft.rule`/`overwrite`.

**F-3 — SOURCE-FACTOR RED (charter-global structure; LC and RO bear on task 0, PBT, COC and BD bear on task 1).** Symptom: five computations declare their only `method` factor(s) over tiers that only substitute a multiplier into an unchanged formula. Root cause: `effect: method` assigned to multiplier ladders. Evidence: LC `autopay_courtesy_reduction` ("reduced by one fifth ... one tenth ... taken as computed" = x0.8/x0.9/x1); RO `repeat_reconnection_adjustment` ("doubled ... multiplied by one and a half ... taken as it is"); PBT `returned_payment_carried_transform` ("doubled before rounding ... multiplied by one and a half before rounding ... taken as it is"); COC `planned_maintenance_adjustment` ("doubled ... one and a half ... taken as it is"); BD `late_history_transfer_count` ("counts in full ... half ... not at all" = 1/0.5/0) and `tenure_allowance_increase` ("increased by one fifth ... one tenth ... taken as it is", cap never binding beyond the fall-through). Consequence: counted honestly, LC, RO, PBT, COC and BD each have 0 `method` factors, under the minimum of 1 per computation.

**F-4 — SOURCE-FACTOR RED (charter-global; PBT, bears on task 1).** Symptom: the fall-through tier of `final_bill_carried_rate` can never be reached at the transfer write. Root cause: the ladder's lower boundary equals the inherited transfer eligibility. Evidence: PBT rule "half of that rate when at least the prior balance transfer period but fewer than 60 days have passed, and no carried rate when fewer days have passed" vs inherited base eligibility `final_bill_aged`: "The transfer is made only when the final bill of the closed agreement has remained unpaid for at least the prior balance transfer period after its due date ... the transfer may be made on the day the count reaches the period, not before." Consequence: the condition "at least the prior balance transfer period" holds of every customer who reaches this write, and the fall-through ("fewer days" -> carried rate 0, which is also the factor's `baseline`) holds of none. The ladder has 2 live tiers (< 3), and its baseline is a value no customer at this write ever receives.

Observations (no demonstrated consequence; not grounds for rework): O-1 LC object narrowed to the most recent bill while CP's sentence covers "each of its bills"; O-2 SOC object narrowed to the most recent record while CP's sentence says "most recent qualifying"; O-3 LC `inputs` metadata incomplete; O-4 RO `tamper_findings_24` would count `no_access` findings; O-5 RO deposit-payment window wording ("the calendar month before") vs the 1-month convention; O-6 BD "due date has passed" vs `current_not_due` on the due date itself; O-7 BD<-PBT `effect` describes one tier only. Also: RO's rule and CP's rule each carry a baseline sentence ("The reconnection charge is the schedule's field reconnection charge for standard hours, rounded to the cent."; "The reconnection payment amount is that balance less every late payment charge ever posted ...") next to the factor sentences that redefine the same quantity. This is the charter's required baseline-in-rule layout and is recorded only so the KB audit can watch how it is rendered.

## closing_checklist

Written 2026-10-07T21:3xZ, after both tasks' derivations were frozen and compared. This section is post-reveal, and nothing above it was edited after the reveal.

**Status: NOT CLOSED.** Not every task passes all four relationships.

- Per-task files: `0.md`, `1.md` match tasks 0 and 1 one-to-one, with `_difficulty.md` alongside. This is revision 1, so there is no older revision. Each comparison section carries a verdict, and neither is all-PASS.
- Coverage and exclusivity: `charter_scope` of task 0 = {LC, SOC, CP, RO} with tools {a575fa01, 20084a33, dce85fc7, 52263bc7}; task 1 = {PBT, COC, BD} with tools {e8000638, becf7e74, 056776f4}. The two scopes are disjoint and together cover all 7 extended policies and all 7 task tools. Each scope spans its whole tree. Each uuid8 is independent (§action_binding_and_uuids).
- Trees:
  - Task 0: 3 prerequisite problems, 2 value_input edges, owner=user CP.
  - Task 1: 2 prerequisite problems, 2 value_input edges, owner=user BD.
  - Both acyclic, and the union graph is still a DAG (two disjoint trees).
  - The trees hold, but task 0's closure carries a false evidence assertion (`0.md` finding 5).
- Factors:
  - Every factor bears weight against an honest baseline on its task's world.
  - Every whole baseline gives a definite number different from gold (2.53, 35.00, 344.73, 65.00, 476.46, 50.00, 599.06).
  - Multi-source and cross-difficulty factors are present per task.
  - **Failing:** F-3 (LC, RO, PBT, COC and BD have 0 honest `method` factors), F-4 (PBT carried-rate ladder has 2 live tiers), plus task 0's false factor_trace figures.
- Policy self-consistency: F-1 and F-2 are charter-global SOURCE-POLICY RED. Neither has a consequence in this difficulty's two worlds.
- Unique solution: the independent derivation equals GT on every scored argument in both tasks.
- Gates: this audit does not re-run the instantiation-stage gates (the coordinator's snapshot is cited in §charter_global_frozen). They will need to be re-run once on any reworked form.

## revision_2

### charter_global_frozen (revision 2)

- Freeze time 2026-10-07T22:31Z. Written before either task's round-2 GT was revealed; built only from the charter, the schema, the tools and the masked views. Revision 1 text above is untouched.
- Hashes:
  - `service.extended.yaml` = `976406a4f8841ac989d497ad5559661ae2456472e60746a07a577f2de85bcda4`, **changed** from round 1, so every charter-global section is re-derived in full below.
  - `task_tools.py` = `29d175fb…cb3b3498`, unchanged, so §action_binding_and_uuids is carried forward by reference.
  - Views `task_0.view.json` `d6e0e1a3…` and `task_1.view.json` `0cc89c49…` are unchanged, so both worlds are the same as round 1.
- Base section: lines 1-1723 still byte-identical to `blueprint/products/service.yaml`.
- Gate snapshot (coordinator, after rework): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK ("history_rows_max=89, branches_max=61"); GROUNDING OK; CACHE-DIFF INFO; SCOPE OK; traceability deferred.
- Mechanical checks re-run on the new charter:
  - every `policy_source` is verbatim in its own rule;
  - every `compute_basis` sentence is verbatim in its rule;
  - every `baseline.rule` sentence is in its rule;
  - every `replaced_by` is in its rule;
  - `compute_basis` keys equal `compute` bindings;
  - no edge carries `fallback_reason`; all edges are `form: state`.

### policy_conflict_scan (revision 2)

The graph is unchanged: RO -> CP (state_gate); CP -> LC and CP -> SOC (value_input); BD -> PBT and BD -> COC (value_input).

Changes since round 1 and what they do to overlaps:
- RO now supersedes the base payment-requirement sentence. It restores the base alternatives in its rule: "A reconnection order that rests on an active payment arrangement ... or on an active medical certification ... needs no payment, as the base reconnection rule provides". It counts card, authorized-pay-station-cash and energy-assistance payments and excludes mail check, online bank transfer and autopay.
- CP supersedes the same base sentence for the basis. The two replacements govern different halves of the sentence: RO decides which payments count, CP decides the threshold amount. Merged, the requirement is "eligible payments since disconnection ≥ CP's reconnection payment amount", which is unique.
- BD now carries "A bank draft is taken only while the payments on the agreement reversed as returned unpaid in the schedule's returned-payment restriction look-back stay below the schedule's returned-payment restriction count, as the base payment rule provides; at or above that count no bank draft is taken." This agrees with base.
- No new overlap found between policies.

### rule_compute_equivalence (revision 2)

All bindings re-checked.
- LC: the autopay count now selects the repeat-lateness window (1 / 3 / 12 months), and compute `count_window_months` / `late_charges_counted` match. The autopay multiplier is gone, and `overwrite.replaced_by` was updated to match.
- RO: the assistance window is MONTHS(latest reconnection charge, NOW) / 6 / 12, matching "the number of whole calendar months that have passed since the most recent such charge". `tamper_findings_24` now subtracts both `no_tampering` and `no_access` within `event_type='meter_tampering_finding'`, which closes O-4. The deposit wording is now "less than one whole calendar month before the order", which closes O-5. The repeat-reconnection multiplier was removed from both rule and compute.
- PBT: the carried rate is now ≥60 / 40-59 / <40 days from an anchor date, with the anchor = final bill date / stop date / final due date, matching `anchor_date` and `days_since_anchor`. The return multiplier was removed.
- COC: look-back 24 / 18 / 12 months by planned-maintenance count, matching `lookback_months` / `outage_records_counted`. The controllable count and planned count stay on 12 months, as the rule says. Assembly order matches.
- BD: `allowance_final` = MN(min−0.01, MX(returned allowance, RND(share × most recent bill))) for 96+ / 48-95 months, otherwise the returned allowance, matching the rule. `current_not_due` now uses `>= 0`, so a bill due today is not past due, which closes O-6.
- No `compute` invents a basis, and no rule tier is absent from compute.

### action_binding_and_uuids (revision 2)

Carried forward by reference: `task_tools.py` hash unchanged, and every `(target_tool, computes)` pair is unchanged and claimed once.

### prerequisite_graph (revision 2)

| Blocked | problem | kind | gate | gate exists | resolved_by ok |
| --- | --- | --- | --- | --- | --- |
| CP | LC | value_input | charges_total | yes | yes |
| CP | SOC | value_input | credits_total | yes | yes |
| RO | CP | state_gate | service_reconnection_rule.reconnection_requirement_met | yes | yes |
| BD | PBT | value_input | transfers_in | yes | yes |
| BD | COC | value_input | credits_total | yes | yes |

- The graph is acyclic.
- The `condition` fields of CP<-LC, CP<-SOC and RO<-CP were updated with their sentences and match them.
- BD<-PBT `effect` now covers all three counting tiers, which closes O-7.
- **New defect R2-F5:** BD<-COC `condition` still reads "Once the outage records at the address **in the 12 months before the payment** reach the chronic threshold". The COC rule now counts over "the chronic look-back", which "is the 24 calendar months before the posting when two or more outage records recorded as planned maintenance began in the 12 calendar months before the posting, the 18 calendar months before the posting when exactly one did, and the 12 calendar months before the posting when none did". Detail in §findings (revision 2).

### prerequisite_sentences (revision 2)

1. CP<-LC: "The reconnection payment amount is fixed only after the agreement carries a late payment charge on its most recent bill once that bill's grace period has ended with part of it unpaid." The scope now equals LC's object, which closes O-1. Connective "only after"; state form; one writer (LC).
2. CP<-SOC: "The reconnection payment amount is not fixed until the agreement carries the sustained-outage credit owed for the most recent outage record at its service address when that record qualifies." The scope now equals SOC's object, which closes O-2. One writer (SOC).
3. RO<-CP: "A reconnection order that rests on payment is issued only after the card, authorized pay station cash and energy assistance agency payments posted to the agreement since its disconnection date add up to at least the reconnection payment amount." Of this difficulty's writes, only CP posts a payment in those channels (BD posts `online_bank_transfer`, which the rule excludes), so there is a single writer and a single reading.
4. BD<-PBT and 5. BD<-COC: sentences unchanged; same conclusions as round 1.

No tool names, policy ids or restated edges appear in any rule. No undeclared cross-problem order.

### override_declarations (revision 2)

- F-1 re-check: the base payment-requirement sentence is now named in RO's `overwrite`, and the base alternatives are restated in RO's rule. In the round-1 demonstration situation (an active arrangement whose down payment has been received, no card payment), base says reconnect and RO says "needs no payment", so the two now agree. A disconnected customer who paid through an energy assistance agency: base counted it, RO counts it. A customer who paid by mail check: base counted it, RO does not, and that difference is now declared in `overwrite`. **F-1 closed.**
- F-2 re-check: in the situation "two returns in the last 12 months", base refuses online_bank_transfer and BD now says "at or above that count no bank draft is taken". Same conclusion. BD's allowance tier "two or more ... in the 24 calendar months" remains reachable: two returns in 24 months but fewer than two in the last 12. **F-2 closed.**
- Every other sentence-level conclusion from round 1 is unchanged.
- LC's `overwrite.replaced_by` now matches its new operation order.
- COC's `overwrite.replaced_by` now speaks of "the chronic look-back". This is declared, since the base sentence naming `service_msr_outages_12m` is the superseded clause.

### factor_ladders (revision 2)

Changed factors:

| Policy | Factor | Label | Honest? | Live tiers |
| --- | --- | --- | --- | --- |
| LC | autopay_lateness_window (replaces autopay_courtesy_reduction) | M | yes: selects the window over which late charges are counted (1 / 3 / 12 months), i.e. which records enter the count, not a multiplier | 3 |
| RO | collection_cycle_assistance_window (replaces repeat_reconnection_adjustment) | M | yes: selects the window over which assistance payments are counted (months since the last reconnection / 6 / 12) | 3 |
| PBT | final_bill_carried_rate | P | yes | 3 (see F-4 re-check) |
| PBT | carried_charge_anchor (replaces returned_payment_carried_transform) | M | yes: selects the date from which elapsed days are counted | 3 |
| COC | planned_maintenance_lookback (replaces planned_maintenance_adjustment) | M | yes: selects the outage-count look-back (24 / 18 / 12 months) | 3 |
| BD | late_history_transfer_count | relabelled P | yes (coefficient 1 / 0.5 / 0) | 3 |
| BD | tenure_allowance_selection (replaces tenure_allowance_increase) | M | yes: the 96+ and 48-95 tiers introduce a new term (a share of the most recent bill) under a max; the fall-through does not | 3 |

Unchanged factors keep their round-1 conclusions.

- Counts (honest): LC 3 P + 1 M; SOC 5 P + 1 M; CP 4 P + 1 M; RO 5 P + 1 M; PBT 3 P + 1 M; COC 4 P + 1 M; BD 3 P + 1 M. All are within 4-6 with ≥ 2 P and ≥ 1 M. **F-3 closed.**
- Consistency note: three of the new methods select a counting window and one selects an anchor date. I class window/anchor selection as method, the same way I classed CP `reconnection_history_basis` (which late charges leave the basis) in round 1. Multipliers are classed as parameters.
- F-4 re-check: the carried-rate ladder now reads 60+ / 40-59 / under 40 days from the anchor. Base `final_bill_aged` guarantees only ≥ 30 days after the final due date. With the due-date anchor (no return, final bill issued < 6 days after stop), 30-39 days therefore reaches the "no carried rate" fall-through. No tier condition now holds for every customer at the write. **F-4 closed.**
- Business realism of the new tiers:
  - LC's autopay window: judging automatic payers on recent conduct is credible.
  - RO's collection-cycle window and COC's planned-maintenance look-back: plausible.
  - BD's bill-share allowance for long tenure: plausible.
  - PBT anchor tier 1 (a returned payment means counting from the final bill date) works like losing a grace period, which lenders do.
  - PBT anchor tier 2 ("the agreement's stop date when no payment was returned but the final bill was issued six or more days after the stop date") counts late-charge days from before the final bill even existed, because the company billed late. I doubt a utility would publish that treatment, but the "interest from the service date" analogy keeps it short of a demonstrable defect, so it is recorded as observation R2-O1. No task world takes this tier.
- All ladders: tiers are distinct in outcome; every tier is stated in the rule and implemented in compute; each factor's `baseline` equals its fall-through and `baseline.rule`. COC `baseline.rule` now includes "The chronic look-back is the 12 calendar months before the posting.", which is in the rule.

### findings (revision 2)

- F-1 **closed**, F-2 **closed**, F-3 **closed**, F-4 **closed** (re-check evidence above).
- O-1, O-2, O-4, O-5, O-6, O-7 addressed in the charter. O-3 (LC `inputs` metadata) is not re-examined beyond confirming compute and rule agree.
- **R2-F5 — SOURCE-POLICY RED (new, introduced by the rework; charter-global; bears on task 1).**
  - Symptom: the BD<-COC prerequisite `condition` fixes a 12-month count, while the COC rule it points at now counts over a 12/18/24-month look-back.
  - Root cause: COC's counting window changed in the rework; the `condition` field was not updated.
  - Evidence:
    - `prerequisite[1].condition`: "Once the outage records at the address in the 12 months before the payment reach the chronic threshold, the agreement carries a chronic_outage credit ..."
    - COC rule: "... once the outage records at its service address that began within the chronic look-back reach the chronic threshold" plus the look-back ladder sentence quoted in §prerequisite_graph.
  - Demonstrated consequence (same situation, two conclusions): an RS agreement with 1 planned-maintenance record and 3 other records in the last 12 months (2 of them equipment failure, so threshold 6 − 1 = 5) plus 2 records 13-18 months back. COC rule: look-back 18 months, 6 records ≥ 5, so a credit is owed and BD's state is unmet. `condition`: 12-month count 4 < 5, so the prerequisite is "met" with no credit. The structured field now disagrees with the rule it encodes, a check-7 failure.
  - Affected: `service_ext_notice_avoidance_bank_draft.prerequisite[1].condition`.
  - Task 1's own world reaches the threshold under both windows (7 ≥ 4 and 8 ≥ 4), so there is no in-world consequence.
- R2-O1: PBT anchor tier 2 realism (above).

### closing_checklist (revision 2)

Written after the round-2 reveal; nothing in §revision_2 above this heading was edited after the reveal.

**Status: NOT CLOSED.**

- Round-1 REDs: F-1, F-2, F-3, F-4 **closed** (re-check evidence in §revision_2). Task 0 findings 5 and 6 **closed**; finding 7 no longer applies.
- New in round 2:
  - **R2-F5** (charter-global SOURCE-POLICY RED): BD<-COC `condition` still fixes a 12-month count while COC now counts over a 12/18/24-month look-back. No in-world consequence.
  - **Task 1 SOURCE-TASK RED**: the 246.605 rounding tie gives a bank draft of 948.78 (GT) vs 948.79 (half-up).
  - **Task 1 SOURCE-FACTOR RED**: the COC computation lost its only near-miss, because the 2025-09-03 record now falls inside the 18-month look-back.
  - These are regressions or new defects introduced by the rework.
- Coverage, exclusivity and uuids: unchanged and satisfied. `charter_scope` task 0 = {LC, SOC, CP, RO}, task 1 = {PBT, COC, BD}. Tools are unchanged.
- Trees: task 0 has n=3 with 2 value_input edges and owner=user CP; task 1 has n=2 with 2 value_input edges and owner=user BD. Both acyclic, and the union is a DAG.
- Factors: 4-6 per computation, each with ≥ 2 honest P and 1 honest M, and multi-source and cross-difficulty factors per task. Every factor bears weight against an honest baseline, and every whole baseline is definite and differs from gold. The exception is the task 1 COC near-miss above.
- Gates: the coordinator's post-rework snapshot is cited above; this audit does not re-run them.

## revision_3

### charter_global_frozen (revision 3)

- Freeze time 2026-10-08T00:05Z. Written before either task's round-3 GT was revealed. Revisions 1 and 2 above are untouched.
- Hashes:
  - `service.extended.yaml` = `e97ff1b61f186000b4adfb2e1b554daf9a10745d5a47cc7b28f7d0fedad4b5fd` (changed).
  - `task_tools.py` `29d175fb…` (unchanged).
  - `task_0.view.json` `d6e0e1a3…` (unchanged).
  - `task_1.view.json` `d7d640f2dd3c19dc999328879b54c4197b9a0a1db7f31d82af9728bf7848cfff` (changed).
- Base lines 1-1723 are still byte-identical to the blueprint product.
- Scope of the charter change, located mechanically:
  - LC, SOC, CP, RO: the round-2 dump format (overwrite, params, rule, prerequisite, cross_category, compute, factors, baseline) was regenerated from the new file and `diff`ed against the persisted round-2 dump of those four policies. Identical.
  - PBT and COC: re-printed and compared against the round-2 text. Rule, params, compute, factors and baseline are unchanged.
  - The change is confined to BD. Its transfer-share wording is now "at half its amount, with any fraction of a cent dropped" in the rule, the `overwrite.replaced_by`, `compute_basis` and the factor ladder. Compute now truncates: `transfer_counted = int(transfers_in × 0.5 × 100 + 0.000001) / 100`. Its `prerequisite[1].condition` was rewritten.
- Mechanical re-checks on all 7 policies: every `policy_source`, `compute_basis` sentence, `baseline.rule` sentence and `replaced_by` is verbatim in its own rule, and `compute_basis` keys equal the bindings. All pass.

### re-derived sections (revision 3)

- §policy_conflict_scan, §override_declarations, §action_binding_and_uuids, §prerequisite_sentences, and §factor_ladders for LC, SOC, CP, RO, PBT and COC are carried forward from revision 2 by reference. Their inputs are unchanged (the six policies are textually identical and the tool hash is the same).
- BD re-derived:
  - The rule/compute pair for `transfer_counted` is equivalent. "any fraction of a cent dropped" is truncation toward zero, and the epsilon only guards against binary representation (it changes no value at a whole-cent boundary).
  - The ladder is unchanged in tiers: count in full / half truncated / none. It stays a parameter, and every other BD factor is unchanged.
  - The new wording leaves a single reading where revision 2 had two (the half-cent tie).
- §prerequisite_graph, BD<-COC: `condition` now reads "Once the outage records at the address that began within the chronic look-back (12, 18 or 24 months before the payment, set by the planned-maintenance records of the last 12 months) reach the chronic threshold, the agreement carries a chronic_outage credit attached to the most recent outage record." This matches COC's look-back sentence. In the revision-2 demonstration world (18-month look-back, 6 ≥ 5) the condition and the rule now give the same conclusion. **R2-F5 closed.**
- Remaining latent charter-wide point (observation R3-O2): no rounding mode is stated for any other "rounded to the cent". That is harmless only while no task world places an exact half-cent at such a step. Both task files below check for ties in their own worlds.

### findings (revision 3)

- R2-F5 **closed**. No new charter-global defect found.
- R2-O1 (PBT stop-date anchor realism) and R3-O2: observations.

### closing_checklist (revision 3)

Written after the round-3 reveal; nothing in §revision_3 above this heading was edited after the reveal.

**Status: CLOSED for the source-layer policy-task audit.** All four relationships PASS in both tasks.

- Per-task files `0.md` and `1.md` match the tasks one-to-one, with `_difficulty.md` alongside. Revisions 1, 2 and 3 are preserved in order, and every comparison section carries a verdict. Revision 3 is all-PASS.
- Round-1 REDs (F-1 to F-4, task 0 findings 5 and 6) were closed in round 2 and are still closed: LC, SOC, CP, RO, PBT and COC are textually unchanged since round 2, and BD's change touches none of them.
- Round-2 REDs (R2-F5, task 1 findings 1 and 2): closed in round 3.
- No new defect and no regression found. Task 0's hash change was checked field by field and left every scored, proof and closure value unchanged.
- Coverage: all 7 extended policies and 7 task tools, split {LC, SOC, CP, RO} / {PBT, COC, BD}. The two scopes are disjoint, and every uuid8 is independent and frozen.
- Trees:
  - Task 0: 3 prerequisite problems, 2 value_input edges, owner=user CP.
  - Task 1: 2 prerequisite problems, 2 value_input edges, owner=user BD.
  - Both acyclic, with no cross-task edges, so the union is a DAG.
- Factors: every computation has 4-6 factors with ≥ 2 honest parameters and 1 honest method. Each task has multi-source and cross-difficulty factors, seeded. Every factor bears weight against an honest baseline, every whole baseline is definite and differs from gold, and every computation has a near-miss.
- Open observations, not grounds for rework:
  - O-3 (inputs metadata);
  - O-T0-1 and O-T1-1 (passive "go ahead" persona lines);
  - O-T0-2 (returned-autopay count reading);
  - R2-O1 (stop-date anchor realism; no world takes it);
  - R2-O2 (assistance-window reading);
  - R3-O1 (non-decisive chronic near-miss);
  - R3-O2 (no rounding mode stated charter-wide; no tie in either world).
- Gates: the coordinator's post-rework snapshot (all OK, CACHE-DIFF INFO, traceability deferred until the KB is published) is cited. This audit did not re-run them.
