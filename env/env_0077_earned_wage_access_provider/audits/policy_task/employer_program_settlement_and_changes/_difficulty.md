# Policy-task audit — employer_program_settlement_and_changes / charter-global

## charter_global_frozen
- Freeze: 2026-10-23 00:10 UTC (revision_1), auditor: independent policy-task auditor (erl-task-policy-audit), not the instantiator.
- Hashes (sha256, first 16): `program.extended.yaml` = 24819766561fc15c, `task_tools.py` = c8002da6be720cd4; masked views `r1/0.view.json` = 61e130018fefeb90, `r1/1.view.json` = ff6a00b45a42fc96. All four match the coordinator snapshot `/tmp/erl0077_coord/snap_employer_program_settlement_and_changes_r1.txt`.
- Entry conditions (Step 0): the snapshot carries all 7 instantiation gates with their output lines (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK); check_traceability deferred by coordinator ruling. Input complete.
- Read: blueprint.yaml, db_schema.json, share_tools.py, products/program.yaml (and, for holding uniqueness only, the multi-holding sentences of products/paycard.yaml and products/disburse.yaml), program.extended.yaml, task_tools.py, the DSL semantics in skills/erl-task-instantiate/scripts/check_compute.py (MONTHS/DAYS/_within/LATEST/CFIELD), audits/render_source/XF_recipe.md, audits/render_source/owner_ruling.md, the two masked views.
- Masked and unread while this section was written: tasks/*.json, plan.md, worklog.md, every evaluation_criteria / computations / charter_scope / required_documents / design_rationale / solvability_contract / prerequisite_closure field. Nothing in this section derives from a revealed GT.
- Base copy: `diff` of the base section of program.extended.yaml (lines 1-1757) against blueprint/products/program.yaml prints nothing — verbatim identical.

### policy_conflict_scan
Extended policies (5), target tools, triggers:

| id | target_tool (owner) | trigger | subject | prerequisite |
|---|---|---|---|---|
| P1 program_ext_worker_fee_rerate | credit_worker_fee_overbilling_e0c50836 (agent) | state_due | program_credit_memo | [] |
| P2 program_ext_sla_claim_credit | file_sla_credit_claim_b00aa839 (user) | on_request | program_sla_credit | P1, value_input, gate worker_net, state |
| P3 program_ext_shortfall_late_charge | assess_shortfall_late_charge_82f1f096 (agent) | state_due | program_late_charge | [] |
| P4 program_ext_return_late_charge | assess_return_late_charge_9954ff84 (agent) | state_due | program_late_charge | P3, value_input, gate prior_count, state |
| P5 program_ext_termination_fee | sign_termination_notice_c67c1163 (user) | on_request | program_termination_notice | P4, value_input, gate late_count, state |

Overlapping subjects and the conclusions they reach:
- SLA credit base (P2) vs the program_paycard_bundle sentence as P1 restated it: conflict, finding **C-02**.
- Early termination fee platform-fee part (P5) vs program_paycard_bundle "never to ... termination ... fee lines" / "holding an Instant Pay Disbursement service earns none": conflict, finding **C-01**.
- Late charge on employer-liable notices (P3) and on reinstated schedules (P4): the two scopes are disjoint (P3 excludes a schedule that carries a remittance return, P4 excludes a schedule that carries an employer-liable notice), and the two overwrites of the one base clause name both cases (XF C3 satisfied). But a schedule that carries both falls into neither, and so does every item outside the two "most recent" selections. This is a gap, finding **C-03**.
- P1 (billing-error credit) vs base payments_and_credits caps and dedup: conflict, finding **C-05**.
- Time anchors: P2's month is the latest census month, P1's line is the latest employer_paid_pepm billing_month. An invoice line needs its census, so P1's line is the claimed month's per-worker line whenever that month has one. No conflict.
- Terminal states: P5 moves the agreement live→terminating (base program_termination_notice transition). The other four only add billing rows. No conflict.
- Cross-category reads are declared for every CFIELD: paycard status/launch_date/variant_name, and disburse status/activated_date. Both products hold at most one per employer (paycard.yaml l.717, disburse.yaml l.716), so first-match CFIELD with an exact status filter is well-defined.
- Trigger rule (XF E1): every event the five tools write (program_credit_memo, program_sla_credit, program_late_charge, program_invoice_line, program_termination_notice transition) has `triggers: []`. No row lands in another category.
- Scope: the five policies split into two prerequisite components, {P1, P2} and {P3, P4, P5}. With M=2 the only partition that respects the edges is task0 = {P1, P2} and task1 = {P3, P4, P5}, which together cover all five. Each task file confirms its own world.

### rule_compute_equivalence
- A sweep script (`/tmp/audit_employer_program_settlement_and_changes_0077/charter_checks.py`) checked all five policies. Every compute_basis quote is verbatim in its own rule (XF B5 clean), every superseded_clause is verbatim in its base rule, and every replaced_by is verbatim in the extended rule. Every baseline.rule sentence is a rule sentence.
- P1: binding `month_start` has no compute_basis entry. The rule does state "the first day of the billing month", so this is observation **O-1**. All the other bindings agree with the rule both ways: bands, proration (`DAYS>0 and <30`), the live+launch+package conjunction, MONTHS(signed, renewal), MONTHS(go_live, month_start), the zero-headcount share, the sum of percentages taken off once, RND once, and MX(0, …).
- P2: the bindings for band, credit base, the three-way covered-lines branch, COUNT within_months=6 (`0 <= MONTHS(entry, today) < 6` matches "fewer than … whole months have passed to today"), footprint, reach, hypercare and `credit_pct … if band_pct > 0 else 0` all match the rule.
- P3: the in_scope conjunction, open amount, reason, cure share, frequency "this one included", relationship, bands, and the rounding before the greater-of all match the rule.
- P4: in_scope, bounce "other than the latest one" (−1), resend share, prior count, channel, relationship, bands and rounding all match. **Exception:** the tie case, finding **C-04**.
- P5: days_left, the 30-day periods counted down, MN with ETF months, the line part by fee model, the bundle tiers, contract-year MONTHS, the SLA, standing and workforce windows, and RND last all match.
- Ladders: every tier of every `factors[].ladder` is a rule sentence and a branch of its `decides` binding, and every branch is a stated tier. Fall-through tiers equal the factor baselines.
- Edge cases (XF B1/B2):
  - Absent records: P3/P4 with no notice or return have in_scope false and book nothing. P1 with no line gives billed 0 and result 0. P2 with no census row gives month_start NOW and availability 0 → band floor; this is out of world.
  - Decoys: cancelled or pending change requests are excluded by `request_status='effective'`. Provider-absorbed notices are excluded by `liability`. Billing-error credits on other lines are excluded by `related_entry_id`. A terminated paycard is excluded by `status='live'`.
  - Same-day ties: handled in P3 by the scope test (one notice that day). Not handled in P4 (C-04).
  - Month-end: MONTHS decrements when day2<day1, which matches "a month counting as whole only once the day of the month … is reached".
- Rounding (XF B4): compute uses `RND(x + 0.000000001, 2)` on non-negative values, and every tool body uses `Decimal.quantize(ROUND_HALF_UP)`, as the run's ruling requires.

### action_binding_and_uuids
- Each (target_tool, computes) pair is claimed by exactly one policy: (e0c50836, credit_amount), (b00aa839, credit_amount), (82f1f096, charge_amount), (9954ff84, charge_amount), (c67c1163, early_termination_fee).
- share_tools.py has only read tools plus verify_customer_identity and transfer_to_human_agent, so no shared write can bring about any waited-on state.
- Docstrings:
  - None states a sequence position, names another tool, or carries before/after/first/then/next (script sweep: 0 hits).
  - None carries a concrete example value (XF D1/F5).
  - No arg is a composite string (XF D2).
  - The forbidden-import list is absent (XF D3).
  - Every write tool calls ctx.create/ctx.update in its own body.
- No tool body reads a prerequisite state or refuses a call; they read only the agreement row (customer_id, fee_receivable).
- uuid8s e0c50836, b00aa839, 82f1f096, 9954ff84, c67c1163 share no prefix or tail, are not sequential, and none is reused.
- No factor id is a substring of any tool name (XF A8, script: 0 hits).
- Owner ruling:
  - P2: an SLA claim is the employer's own assertion of a contractual right (ruling (c)). The base already conditions the credit on "the employer claims it", and P2's rule says outright "the authorized employer contact files the claim personally". Accepted.
  - P5: a termination notice signed by the employer contact is ruling (a)'s named example, and the base lifecycle says "Termination is the employer's own decision, given in writing by an authorized requester". Accepted.

### prerequisite_graph
- `prerequisite` is filled on every policy (P1 and P3 have []). Edges: P2→P1, P4→P3, P5→P4. Every `problem` is an extended policy id of this file and none points at itself. The graph is two disjoint chains, so it is acyclic.
- Every `policy_source` is verbatim in its own policy's rule (script: True ×3). Every `form` is state, with no fallback_reason, which is correct for the state form. Every `gate` is a real compute binding (worker_net, prior_count, late_count) and every `kind` is value_input.
- `resolved_by` equals the depended-on policy's target_tool in all three edges.
- `effect` wording matches the compute:
  - P1's memo lowers P2 worker_net, because P2 subtracts billing_error memos whose related_entry_id is the line.
  - P3's charge raises P4 prior_count, because P4 counts every program_late_charge within 12 months.
  - P4's charge raises P5 late_count, because P5 counts every program_late_charge within 12 months.
- No authoring-viewpoint phrasing appears.
- `condition` vs sentence:
  - P4: the condition adds "with an open amount", which the sentence carries as "the late charge owed". That is equivalent and neither stronger nor weaker.
  - P5: the same.
  - P2: the condition adds "or no amount was billed above that fee", which the sentence carries as "for any amount billed above". Equivalent.

### prerequisite_sentences
Four-point test, per edge:
1. **P2 ← P1**: "A service level credit for a month is not fixed until the per-worker fee line billed for that month carries the billing-error credit owed on it for any amount billed above the per-worker fee."
   - The ordering connective is "not … until".
   - The waited-on state is record-visible: a billing_error memo whose related_entry_id is the month's employer_paid_pepm line. The wording is business words.
   - It names no tool, no policy id and no snake_case token.
   - Its scope matches the condition.
   - Exactly one write brings the state about: only credit_worker_fee_overbilling books program_credit_memo, and file_sla_credit_claim books program_sla_credit, which P2's worker_net does not subtract.
   - Derivation: the sentence names a billing-error credit on the per-worker line. The only rule that settles a billing-error credit on a per-worker line is P1 ("This policy settles the per-worker fee line most recently billed … and the billing-error credit owed on it"), and P1's line is the claimed month's whenever that month has one. So there is a single reading.
   - P1's rule does not restate the sentence.
2. **P4 ← P3**: "A late charge on a deduction schedule reinstated by a returned remittance is fixed only after every employer-liable shortfall notice whose late-charge grace has passed carries the late charge owed for the late-charge period it is in."
   - The ordering connective is "only after".
   - The state is a program_late_charge whose related_entry_id is the notice.
   - It names nothing forbidden.
   - The one write that books late charges on notices is assess_shortfall_late_charge.
   - Derivation: "late charge on an employer-liable notice" leads to P3's rule ("prices the late charge on the employer-liable shortfall notice booked most recently …").
   - **However**, the sentence waits on *every* such notice, while P3 prices one notice and "in any other case books nothing", and the base pricing of these notices is excepted. For a notice outside P3's selection, no write can bring the state about: finding **C-03** (XF E3).
   - P3's rule does not restate the sentence.
3. **P5 ← P4**: "The early termination fee is fixed only after every deduction schedule reinstated by a returned remittance whose late-charge grace has passed carries the late charge owed for the late-charge period it is in."
   - This edge has the same structure as edge 2.
   - The resolving write is assess_return_late_charge, and the derivation leads to P4's rule.
   - The same *every* vs one-schedule gap applies (C-03).
- No rule states a cross-problem order that grounds no declared edge. The base lifecycle sentence "a termination … bills the early termination fee under program_evt_monthly_invoice" is a pointer, not an order between problems.
- No docstring carries order.
- No base rule sentence grounds an edge.

### override_declarations
Sentence by sentence against each `base_policy_refs` entry. "Follows" means the extended policy leaves the scored quantity as the base sentence fixes it.

- **P1** (refs: payments_and_credits, monthly_invoice, paycard_bundle).
  - monthly_invoice: the platform_fee, sponsored, APG, implementation, ETF, ach_return and zero-line sentences are followed. The employer_paid_pepm sentence is replaced (declared).
  - paycard_bundle: the "platform_fee line is reduced …" sentence is followed. "The discount applies only to the platform fee, never to per-worker …" is replaced (declared). "A month in which the employer held no Payroll Card Program for the whole month earns no discount" is followed (P1's live + launch ≤ first day test).
  - payments_and_credits: "A line billed in error is credited in full" is replaced (declared). But **"A credit memo … never exceeds what is unpaid on it" and "A billed line receives at most one credit memo of each reason" are departed from without declaration**. P1's credit is "the amount billed … less any billing-error credit already booked against that line, above the per-worker fee". That presupposes a second billing_error memo on one line, and it carries no unpaid cap: finding **C-05**.
- **P2** (refs: payments_and_credits, paycard_bundle, monthly_invoice).
  - The SLA sentence of payments_and_credits is replaced (declared, with the earlier-month case restated per XF C1). The claim-window sentence is inherited.
  - **paycard_bundle "an SLA credit for the same month is computed on the discounted fee"**, which P1 restates in force as "an SLA credit for the same month is computed on the discounted platform fee", is contradicted by P2's covered-lines provision (the base adds employer_paid_pepm or sponsored lines). P2 declares no overwrite of program_paycard_bundle, and P1's rewrite does not carve out P2's case: finding **C-02**.
- **P3** (refs: late_charge, shortfall, remittance).
  - The overdue-item sentence is replaced (declared). The pricing clause is replaced (declared). Grace, periods, one per period, pointer/invoice_line/due, provider-absorbed never charged, and waiver are inherited.
  - shortfall: due_date = cure date is followed. remittance: application to the named schedule is followed.
  - The replaced_by of the pricing clause excepts *every* employer-liable notice from base pricing, but P3 prices only the latest in-scope notice: finding **C-03** (XF C1).
- **P4** (refs: late_charge, remittance).
  - The pricing clause is replaced (declared, sibling tail names both cases). "A late charge caused by a returned remittance runs from the schedule's original due_date" is followed. remittance reinstatement is followed.
  - Same gap as P3 for every reinstated schedule outside P4's selection (C-03).
- **P5** (refs: lifecycle, monthly_invoice).
  - The ETF sentence of monthly_invoice is replaced (declared, other notices restated). The lifecycle notice-period, live-only and authorized-requester sentences are inherited.
  - **program_paycard_bundle is not referenced, yet P5 departs from two of its in-force sentences.** First, "The discount applies only to the platform fee, never to … termination … fee lines" (base), restated by P1 as "never to sponsored, implementation, termination or return fee lines". Second, "holding an Instant Pay Disbursement service earns none". termination_bundle reduces the ETF's platform-fee part by paycard_bundle_discount_percent, plus suite_extra_percent when an Instant Pay service is held: finding **C-01**.
- Disguised forms:
  - No anonymous intermediate factor beyond those above.
  - No 0/1 multiplier on a base-fixed amount. P2's `if band_pct > 0` is the base's own existence condition.
  - No dropped base branch.

### factor_ladders
Counts as declared (param / method / cross_difficulty):
- P1: 6 factors (4 parameter / 2 method). Cross-difficulty: card_bundle_depth (paycard).
- P2: 5 factors (4 / 1). Cross-difficulty: product_footprint (paycard + disburse).
- P3: 5 factors (4 / 1). Cross-difficulty: shortfall_relationship.
- P4: 6 factors (5 / 1). Cross-difficulty: return_relationship.
- P5: 6 factors (5 / 1). Cross-difficulty: termination_bundle.

Every ladder has three pairwise-disjoint tiers, and every fall-through equals the factor baseline and the baseline.rule. No two tiers of any ladder share a value or method. `decides` is never `result`. No binding is shared between factors, and the transitive factor-reads table is empty (script; XF A1). Shared selections (bill_month, month_start, claim_month, notice/return ids, sched_id) are plain bindings (XF A5).

Method-shape all-pairs table (XF A6):

| factor | pair | distinguishing input or operation | verdict |
|---|---|---|---|
| P1 proration_anchor | T1/T2 | data-selected anchor date (change effective_date vs go_live_date) plus the "no such date" pick | pass |
| | T1/T3, T2/T3 | adds the day proration operation | pass |
| P1 enrollment_bands | T1/T2 | adds the third band | pass |
| | T2/T3 | adds the second band | pass |
| P2 covered_fee_lines | T1/T2/T3 | adds employer_paid_pepm net, or sponsored nets, or nothing (no tier is 0 over the other's domain) | pass |
| P3 notice_balance_bands, P4 reinstated_balance_bands | T1/T2, T2/T3 | adds a band | pass |
| P5 termination_fee_lines | T1/T2/T3 | PEPM window sum vs sponsored window sums vs none | pass |

Labels are honest: every parameter-labelled factor's tiers substitute a number, and every method-labelled factor's tiers change the formula.

Multi-source (a tier beyond the fall-through that is a conjunction over distinct records):
- P1: proration_anchor (change request × billing month × agreement) and card_bundle_depth (paycard program × billing month).
- P2: product_footprint (paycard × disburse × census month).
- P3: shortfall_relationship (paycard × disburse).
- P4: return_relationship.
- P5: termination_bundle.

Assembly sentences (XF A2/A3):
- Every policy fixes one order, and all multiplicative parts commute, so XF A3 is clean.
- **A2 violations** (the sentence names factor quantities): finding **C-06**.
  - P1 "the way the workers are billed sets the fee, the part of the month billed then multiplies that fee" names graded_fee and billed_share.
  - P3 and P4 "the open amount, weighted as the adjustments set" names weighted_open.
  - P5 "its platform fee part reduced and its line part added as the adjustments set" names bundle_pct and line_part.
- P2's sentence ("points … multiplied by each multiplier …") is generic.

A4: no single-factor quantity is defined in a baseline sentence.

A7 (min/max shapes):
- P1 MX(0, …), and P3/P4 MX(minimum, …): T2 holds for every factor in every policy, because each factor moves its policy's result whenever that result is above its floor/minimum with all other factors at baseline. T1 is judged per task.
- P5 MN(early_termination_fee_months, months_left) is not a factor.

Realism (XF F1; the user's top priority). The industry yardsticks are a flat contractual monthly late-charge rate with a minimum (and sometimes a cap), SLA credits laddered by availability band, chronic-breach escalation, and ETFs that recover remaining committed fees and decline with contract year. Against those:
- **P1**: all six factors stand. Mid-month proration, graduated per-worker volume pricing, a payroll-card bundle discount, a multi-year commitment discount, introductory launch pricing and an adoption incentive are all dimensions a B2B EWA price list carries, at plausible figures (3 to 10 %).
- **P2**:
  - covered_fee_lines stands (SLA credits computed on the fees of the affected service).
  - breach_recurrence stands (chronic-failure escalator).
  - hypercare_window is unusual (stabilization periods are more often excluded from credits than enhanced) but publishable, so it is observation **O-3**.
  - **product_footprint** adds credit points for holding other Paystride products. That is a loyalty ladder on a service-level credit for the EWA platform's own availability, and no SLA schedule weighs it.
  - **enrolled_reach** adds credit points by enrolled-worker count. The credit base already scales with the per-worker line (covered_fee_lines), and SLA schedules do not ladder the credit percentage by the customer's size.
  - Both are finding **F-P2**.
- **P3**:
  - shortfall_reason_points (a surcharge for deducted-but-not-remitted, that is, withheld worker money) and liable_frequency (repeat-offender escalation) stand.
  - **shortfall_relationship** is a lower penalty rate for multi-product clients, which is a loyalty ladder on a penalty and has no real basis.
  - **notice_balance_bands** is a degressive weighting that charges large overdue balances a lower effective rate. Late-charge schedules apply a flat percentage, sometimes capped, and never discount the larger arrears.
  - **cure_progress** cuts the rate when part has been remitted. The charge already runs on the open amount only, so this double-counts the cure, and no published late-charge schedule does it.
  - These three are finding **F-P3**.
- **P4**:
  - bounce_history and prior_late_charges stand (repeat escalation).
  - **return_relationship** is a loyalty ladder on a penalty.
  - **returned_channel** adds late-rate points by the payment rail of the returned money. The rail's cost is already billed as the ach_return_fee line, and no late-charge schedule prices the rail.
  - **reinstated_balance_bands** is degressive.
  - **resend_relief** double-counts the re-sent part.
  - These four are finding **F-P4**.
- **P5**:
  - termination_fee_lines (average recent fees), contract_year (declining ETF), breach_relief (SLA-failure relief) and workforce_reduction (reduction-in-force relief) stand.
  - termination_bundle is plausible in realism terms but rests on C-01.
  - **remittance_standing** halves or reduces the ETF for a clean remittance record. An ETF recovers lost committed revenue, and payment conduct is not weighed in ETF schedules. That makes it a loyalty ladder. It is finding **F-P5**. It is also the factor through which the P4→P5 edge carries its value.

Counts after the realism tests (factors struck by them are not factors):
- P1: 6 (4 / 2). Within bounds.
- P2: 3 (2 / 1). **Below 4.**
- P3: 2 (2 / 0). **Below 4, no method.**
- P4: 2 (2 / 0). **Below 4, no method.**
- P5: 5 (4 / 1). Within bounds.
- Cross-difficulty factors left: task0 has card_bundle_depth. Task1 has only termination_bundle, which is itself the undeclared override of C-01.

### findings
Each finding is listed as id | verdict | tasks it bears on.

- **C-01** | SOURCE-POLICY RED (undeclared override, XF C2) | task1.
  - Symptom: P5 discounts the ETF's platform-fee part and adds an Instant Pay suite tier.
  - Root cause: P5 has no overwrite of program_paycard_bundle.
  - Evidence: base program_paycard_bundle "The discount applies only to the platform fee, never to per-worker, sponsored, implementation, termination or return fee lines … holding an Instant Pay Disbursement service earns none". P1's in-force restatement: "never to sponsored, implementation, termination or return fee lines". P5 rule: "The platform fee part of the monthly charge carries the Payroll Card Program bundle: … reduced by paycard_bundle_discount_percent plus suite_extra_percent percent; … reduced by paycard_bundle_discount_percent percent". P5 `overwrite` lists only program_evt_monthly_invoice.
  - Consequence: demonstrated in 1.md.
  - Affected: program.extended.yaml, P5 rule / overwrite / factor termination_bundle.
- **C-02** | SOURCE-POLICY RED (in-force sentence contradicted, XF C2/C3) | task0.
  - Evidence: P1 replaced_by (in force) "an SLA credit for the same month is computed on the discounted platform fee". P2 rule "where the month's invoice carries an employer_paid_pepm line, the credit base adds that line's amount …". P2 has no overwrite of program_paycard_bundle, and P1's tail does not exclude P2's case.
  - Consequence: demonstrated in 0.md.
  - Affected: P1 overwrite[1].replaced_by, and P2 overwrite / covered_fee_lines.
- **C-03** | SOURCE-POLICY RED (out-of-scope pricing retired, unsatisfiable wait; XF C1/E3) | task1 (structural).
  - Evidence: P3/P4 replaced_by "except the late charge on an employer-liable shortfall notice and the late charge on a deduction schedule reinstated by a returned remittance, which are priced under their own provisions". P3 "in any other case this policy books nothing". P4 "in any other case this policy books nothing". The P4/P5 prerequisite sentences say "every employer-liable shortfall notice …" and "every deduction schedule reinstated …".
  - Producible worlds:
    - Two employer-liable notices booked the same day: P3 books neither, and P4's wait can never close.
    - A schedule carrying both a return and an employer-liable notice: neither P3 nor P4 prices it.
    - An older reinstated schedule still open behind a newer return: P4 prices only the newest, so P5's wait can never close.
  - Not demonstrable on task1's world. Each task file states why.
- **C-04** | SOURCE-POLICY RED (no tie rule, XF B1) | task1 (structural).
  - Evidence: P4 scope "when every remittance return booked that day concerns that schedule" admits several same-day returns on one schedule. "the remittance return booked most recently", "the returned amount" and "the returned remittance was an employer_ach_credit" then have no tie rule. Compute `LATEST(..., date_field='entry_date')` keeps the first-inserted row (strict `>`).
  - Second reading: the returned amount is the sum of that day's returns. For example, with returns of 30,000 and 20,000 the resend share is computed on 30,000 in one reading and 50,000 in the other.
  - Not demonstrable on task1 (one return on 2026-10-09).
- **C-05** | SOURCE-POLICY RED (undeclared departure, XF C2) | task0 (structural).
  - Evidence: base "A credit memo points to the line it credits and never exceeds what is unpaid on it." and "A billed line receives at most one credit memo of each reason." P1 "The billing-error credit is the amount billed on the per-worker fee line, less any billing-error credit already booked against that line, above the per-worker fee". The compute has no unpaid cap and presupposes a second billing_error memo.
  - Producible world: the line is partly paid or already carries a billing_error memo, so the two sentences give different credits.
  - Not demonstrable on task0 (line e7044a60 fully unpaid, no memo).
- **C-06** | SOURCE-POLICY RED (XF A2 assembly naming factor quantities) | task0 (P1), task1 (P3, P4, P5).
  - The sentences are quoted under factor_ladders above. In both tasks the consequence is the KB computation document announcing the factor quantities it must stay silent about.
- **F-P2** | SOURCE-FACTOR RED (unreal ladders; count 3 < 4) | task0.
  - Members: product_footprint and enrolled_reach.
  - Demonstrated in 0.md.
- **F-P3** | SOURCE-FACTOR RED (unreal ladders; count 2 < 4, no method) | task1.
  - Members: shortfall_relationship, notice_balance_bands and cure_progress.
- **F-P4** | SOURCE-FACTOR RED (unreal ladders; count 2 < 4, no method) | task1.
  - Members: return_relationship, returned_channel, reinstated_balance_bands and resend_relief.
- **F-P5** | SOURCE-FACTOR RED (unreal ladder carrying an edge) | task1.
  - Member: remittance_standing.

Observations (not grounds for rework):
- **O-1**: P1 `month_start` has no compute_basis entry.
- **O-2**: P1 commitment_term measures signed_date→current renewal_date, so it grows with each renewal (tenure rather than committed term).
- **O-3**: P2 hypercare_window, as above.
- **O-4**: P2 offers no line to point to for tiers whose monthly_platform_fee_usd is 0.0 (Starter, Growth), because "A line that comes to zero is not billed".
- **O-5**: P2's SLA credit can exceed the unpaid amount of the platform_fee line it points to. Whether the base credit-memo cap reaches program_sla_credit rows is not stated.
- **O-6**: persona-name uniqueness across difficulties (XF D5) was not checkable under read isolation.

## closing_checklist
Written after both reveals (2026-10-23 00:14 UTC). The difficulty is **not closed**, because neither task passes all four relationships.
- Audit files: 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json, and this file sits alongside them. This is the first revision, so there are no older revisions. Both comparison sections are present. Neither carries PASS on all four relationships.
- Coverage and scope:
  - Five of five extended policies are covered. The scopes are disjoint: charter_scope of task0 = {P1, P2} and of task1 = {P3, P4, P5}, which matches the partition derived blind in policy_conflict_scan.
  - The task tools and GT are closed: every gold write uses a tool of this module.
  - The uuid8s are independent (action_binding_and_uuids).
- Trees: task0 has 1 prerequisite problem and 1 value_input edge; task1 has 2 prerequisite problems and 2 value_input edges. Each has one owner=user write. The difficulty-wide graph is acyclic (two disjoint chains).
- Factors: **fail**.
  - P2, P3 and P4 fall below 4 real factors, and P3 and P4 have no real method (F-P2, F-P3, F-P4).
  - P5's edge-carrying factor is unreal (F-P5).
  - Task1's only cross-difficulty factor that is left rests on an undeclared override (C-01).
  - Every factor bears weight against an honest baseline on its own world, and each all-baseline figure is definite and differs from gold (task files → factor_weight).
- Instantiation gates: the coordinator snapshot shows all 7 green on the audited hashes. Not re-run here; re-running is the coordinator's step after rework.
- RED ids:
  - Charter: C-01, C-02, C-03, C-04, C-05, C-06, F-P2, F-P3, F-P4, F-P5.
  - Task-local: T1-D6.

VERDICT revision_1: task0=RED task1=RED charter=C-01,C-02,C-03,C-04,C-05,C-06,F-P2,F-P3,F-P4,F-P5

## revision_2

### charter_global_frozen (revision_2)
- Freeze: 2026-10-23 00:58 UTC. Auditor: the same independent auditor as revision_1.
- Entry condition: the last non-blank line of worklog.md reads `REWORK round 2: gates 7/7 green`.
- Gate snapshot: `/tmp/erl0077_coord/snap_employer_program_settlement_and_changes_r2.txt`, run by this auditor through the coordinator's snapshot.sh (execute-only). It shows all 7 gates OK.
- Hashes:
  - `program.extended.yaml` 49689ec2f8665c0d (changed from 24819766561fc15c), so every charter-global section is **re-derived in full** below.
  - `task_tools.py` c8002da6be720cd4 (unchanged), so action_binding_and_uuids is carried forward on that hash.
  - Views: r2/0 246edf6548415a1b, r2/1 552b8c4f431ba31f.
- Base copy: `diff` against blueprint/products/program.yaml is still empty.
- Read in addition to revision_1's set: the section "REWORK round 2 claims" of worklog.md (claims by item id), and products/paycard.yaml for the paycard_funding event types, the paycard fee and reserve rules, and the package fee figures.
- Masked and unread while this section was written: tasks/*.json and every GT field.
- Contamination disclosure: the revision_1 GT of both tasks is known to this auditor from the revision_1 reveal. It concerns P1's and P5's unchanged inputs; every revision_2 figure below is recomputed from the r2 views.

### policy_conflict_scan (revision_2)
- Extended policies P1 to P5 have the same ids, tools and triggers as in revision_1.
- P2 now reads the paycard and disburse ledgers (`XSUM` over paycard_funding and disburse_ledger fee debits).
- P3 has no cross-category read. P4 counts `paycard_funding_return` rows (`XCOUNT`). P5 reads the paycard holding (status, launch_date, variant_name).
- The program_paycard_bundle sentence is overwritten three times, by P1, P2 and P5. All three replaced_by texts are identical except their last clause ("these provisions settling the per-worker fee / the base of the service level credit / the early termination fee"). Each names all three cases, so XF C3 holds.
- The late-charge pricing clause is overwritten twice, by P3 and P4. Both replaced_by texts now read "for every overdue item except the employer-liable shortfall notice and the reinstated deduction schedule that the provisions on those two late charges select". That restates base pricing for every other overdue item, so XF C1 holds.
- Edges:
  - P2←P1: value_input, state.
  - P4←P3: value_input, state, with a new sentence.
  - P5←P4: **now state_gate**, state, with a new sentence.
  - The graph is acyclic.
- Scopes: the partition {P1, P2} / {P3, P4, P5} is unchanged.
- Trigger rule (XF E1): no tool changed and every written event has `triggers: []`, so XF E1 is clean.

### rule_compute_equivalence (revision_2)
- Script sweep (`charter_checks.py`): every compute_basis quote, superseded_clause, replaced_by and baseline sentence is verbatim. P1 `month_start` now has a basis entry, which closes O-1.
- P1: the new result `MX(0, MN(line_unpaid, billed − fee))`, guarded by `prior_error_count == 0`, matches "never more than what is still unpaid on that line, the line amount less the payments and credits pointing to it; … a line that already carries a billing-error credit receives no second one".
- P2:
  - The credit base `platform_net + line_add + service_add` matches the rule.
  - consecutive_breach: `MONTHS(prev+'-01', month_start)` gives the month gap, which matches "the month immediately before" / "consecutive_near_months or fewer months before".
  - stabilization matches its rule sentence.
- P3:
  - Points are summed into the rate, then `pct_charge = RND(open × rate)`, then the culpability method is applied. This matches the rule.
  - days past due = `DAYS(notice due_date, today)` matches "counted in calendar days from the notice's due_date to today".
- P4: the in_scope test requires the latest return to be the only return that day, which matches the rule. The returns count (program returns plus `XCOUNT` paycard_funding_return) includes the latest one, which matches "counting the remittance returns … and the funding returns … where at least returns_high_count were booked".
- P5: matches its rule. The bundle tiers are now by package, and there is no Instant Pay tier.
- Rounding (XF B4) follows the run's ruling in every policy.
- **Transitive factor-reads table (XF A1/A5), scripted** in `/tmp/audit_employer_program_settlement_and_changes_0077/r2`:
  - P3 culpability_method's binding `charge` reads pct_charge, which reads rate, which reads freq_pts, dpd_pts, balance_pts, exposure_pts and prior_pts. Those are the outputs of five other factors.
  - P4 returned_payments_method's binding `charge` likewise reads rate and pct_charge, which read the outputs of five other factors.
  - In both policies `result = RND(charge) if in_scope`, so the result is assembled inside a factor binding.
  - P1, P2 and P5 have no factor-to-factor reads.
  - This is finding **N-A1**.
- **Ties (XF B1):**
  - The two scope tests now exclude same-day ties, which closes C-04's member.
  - But the two new prerequisite sentences select by "most recently" with no tie rule. P4: "the employer-liable shortfall notice booked most recently". P5: "the deduction schedule named by the remittance return booked most recently".
  - program_settlements has no time field, so two notices (a schedule gets "one shortfall notice … per schedule and reason") or two returns booked the same day are both "booked most recently".
  - In that world the resolver's scope is false and the items are base-priced, so which item or items the wait covers has two readings. For P4 the readings give a prior_count of 1 or 2, which changes P4's points.
  - This is finding **N-B1**.

### action_binding_and_uuids (revision_2)
- Carried forward on the unchanged task_tools.py hash c8002da6be720cd4.
- One change in the claims: base pricing of non-selected late-charge items books through the same two tools, which are generic in their docstrings. No other policy claims (target_tool, computes).

### prerequisite_graph (revision_2)
- P2←P1 is unchanged and passes, as in revision_1.
- P4←P3:
  - policy_source "A late charge on a deduction schedule reinstated by a returned remittance is fixed only after the employer-liable shortfall notice booked most recently, once its late-charge grace has passed, carries the late charge owed for the late-charge period it is in." It is verbatim in P4's rule, and the gate binding prior_count exists.
  - The condition ("the notice with the latest entry_date, if it is past due plus grace with an open amount, has a program_late_charge pointing to it …") has the sentence's strength.
- P5←P4:
  - kind state_gate, with gate `program_billing.related_entry_id`. That is a column, not an eligibility gate id; extended policies carry no eligibility block. The gate exists only as P5's rule sentence. This is observation **O-7**.
  - **Condition vs sentence:** the condition requires "a program_late_charge pointing to it [the schedule]", while the sentence requires the schedule to "carr[y] the late charge owed".
  - Where the latest return's schedule also carries an employer-liable notice, the overwrite in force says the schedule is "charged through that notice … and is not charged as a schedule as well". The sentence is then satisfied (nothing is owed on the schedule) but the declared condition can never hold. Neither P4 (out of scope) nor the base pricing books a charge on that schedule.
  - So the condition is strengthened against the sentence, and the gate as declared can never open in that producible world (XF E3, check 7). This is the residual member of **C-03**.

### prerequisite_sentences (revision_2)
- All three sentences have an ordering connective ("not … until" / "only after" ×2), name a record-visible state in business words, contain no tool name, id or snake_case token, and appear in no depended-on rule.
- Edge P4←P3:
  - When the latest notice is in P3's scope, P3 prices it.
  - When it is out of scope, P3's restated base clause prices it, and the shortfall tool books it.
  - So exactly one write kind brings the state about, with a single reading, except for the same-day tie (N-B1).
- Edge P5←P4: the same structure, with the residual condition gap (C-03) and the same-day tie (N-B1).
- Docstrings are unchanged and carry no sequence words (script: 0 hits).

### override_declarations (revision_2)
- **P1** (refs as before):
  - The unpaid-cap and one-memo-per-reason sentences are now followed, which closes C-05.
  - The bundle sentence is declared with the sibling tail.
  - The other sentences are as in revision_1.
- **P2:**
  - The SLA sentence is declared (earlier months restated) and the bundle sentence is declared (sibling tail naming "the base of the service level credit for the latest census month"). This closes C-02.
  - The base "holding an Instant Pay Disbursement service earns none" concerns the platform-fee discount; adding the Instant Pay monthly fee to an SLA credit base is not a discount. No conflict.
- **P3 / P4:**
  - The pricing clause is declared and restated for every non-selected item, which closes C-03's C1 half.
  - Culpability's "percentage charge alone, with no minimum", and the returned-payments tier1 "rate applied to the whole returned amount", depart from base pricing only for the selected items, which are excepted. Declared.
  - The tier1 base (the whole returned amount) equals base's "open amount on the first day of that period" for a schedule reinstated as of its original due_date, so it is base-consistent.
- **P5:**
  - program_paycard_bundle is now in refs and overwritten with the sibling tail. The suite tier is gone. This closes C-01.
  - Lifecycle: the new acceptance gate adds a necessary condition to "A termination notice is accepted only while the agreement status is live". That is no contradiction.
  - **New framing defect (XF B6).** The rule says "The platform fee part of the monthly charge of the early termination fee carries the Payroll Card Program bundle the employer is billed under: where … Premier or … Elite package, it is reduced by paycard_bundle_discount_percent plus premium_package_extra_percent percent".
  - The bundle any employer is billed under is the base platform-fee reduction of paycard_bundle_discount_percent, for every package ("the platform_fee line is reduced by paycard_bundle_discount_percent"). No record carries a bundle of paycard_bundle_discount_percent plus premium_package_extra_percent.
  - For a Premier or Elite employer the framing clause ("the bundle the employer is billed under", which equals paycard_bundle_discount_percent) and the tier (that figure plus premium_package_extra_percent) give two reductions. This is finding **N-B6**. Not engaged on task1, whose package is Advantage.

### factor_ladders (revision_2)
Declared counts (param / method / cross-difficulty):
- P1: 6 (4 / 2), cross-difficulty card_bundle_depth. Unchanged.
- P2: 5 (3 / 2), cross-difficulty affected_services.
  - covered_fee_lines: the fall-through is now "no fee line is added".
  - affected_services, breach_recurrence, consecutive_breach and stabilization_window complete the list.
- P3: 6 (5 / 1), no cross-difficulty factor. The factors are culpability_method, liable_frequency, notice_days_past_due, notice_overdue_balance, notice_remittance_exposure and notice_prior_charges.
- P4: 6 (5 / 1), cross-difficulty returned_payments_method (paycard funding returns). The others are return_days_past_due, return_overdue_balance, return_remittance_exposure, return_prior_charges and return_liable_history.
- P5: 5 (4 / 1), cross-difficulty termination_bundle. The others are termination_fee_lines, contract_year, breach_relief and workforce_reduction.
- Every ladder has 3 disjoint tiers, and every fall-through equals the baseline.

Method all-pairs (XF A6):

| factor | pair | distinguishing input or operation | verdict |
|---|---|---|---|
| P3 culpability_method | min+pct vs pct alone | adds the minimum | pass |
| | pct vs max(min, pct) | adds the greater-of | pass |
| | min+pct vs max(min, pct) | addition vs greater-of | pass |
| P4 returned_payments_method | T1 vs T2 | adds the returned-amount input | pass |
| | T2 vs T3 | addition vs greater-of | pass |
| P2 covered_fee_lines | per-worker vs sponsored vs none | different inputs; per-worker excludes sponsored lines in a split month | pass |
| **P2 affected_services** | all three tiers | see below | **FAIL** |

- **P2 affected_services** is one method written as three tiers.
  - Tier 1 "adds both fees" is card_fee + pay_fee.
  - Tier 2 "adds that fee" (exactly one fee > 0) equals card_fee + pay_fee on its domain.
  - Tier 3 "nothing" (both 0) equals card_fee + pay_fee too.
  - The compute `service_add` equals card_fee + pay_fee in every producible world, because fee debits are always > 0.
  - No tier changes the formula, so two tiers select the same method ("add the program fees debited for the month"). This is finding **N-F1**.

Realism (XF F1):
- **Stand:**
  - P2: consecutive_breach (chronic-breach escalator) and stabilization_window (reduced credits in the stabilization period, which closes O-3).
  - P3: culpability (a penalty minimum on wages deducted and kept, no minimum on processing errors) and days past due (escalation).
  - P3 and P4: repeat-delinquency counts (liable_frequency, prior charges, liable history).
  - P4: returned-payments history across the counterparty's Paystride programs.
  - Overdue-balance size points are accepted as a company schedule; observation **O-8** (progressive and unusual, but not padding).
- **Fail:** **notice_remittance_exposure (P3) and return_remittance_exposure (P4)**.
  - Both raise the late-charge rate on the employer's whole remittance receivable, "the amount of every deduction schedule of the agreement less …".
  - That receivable includes schedules not yet due. A late charge compensates for the overdue item, and no late-charge schedule raises its rate because the customer has current, not-yet-due receivables.
  - The factors also double-count the item's own overdue balance, which is already a factor.
  - This is finding **N-F2**.
- Counts after the tests:
  - P2: 4 (3 / 1).
  - P3: 5 (4 / 1).
  - P4: 5 (4 / 1).
  - P5: 5 (4 / 1).
  - All within bounds.
  - Cross-difficulty survivors: task0 has card_bundle_depth. Task1 has returned_payments_method and termination_bundle.
- Assembly sentences (XF A2): all five are now generic ("an adjustment that changes how the fee is worked out comes first, a multiplier comes next …", "what they add to the credit base is added first …", "the percentage points they add … the way the late charge is worked out is then applied", "those that change what the monthly charge is made of come first …"). This closes C-06.

### findings (revision_2)
Round-1 REDs:

| id | status | how closed / what remains |
|---|---|---|
| C-01 | **CLOSED** | declared overwrite, Instant Pay tier gone |
| C-02 | **CLOSED** | sibling overwrite |
| C-03 | **NOT CLOSED** (narrowed) | C1 half closed. The residual is P5's condition-vs-sentence gap when the latest return's schedule carries an employer-liable notice: the gate can never open (E3, check 7). |
| C-04 | **CLOSED** for its member (P4 scope) | the same class reappears in the two new prerequisite sentences, see N-B1 |
| C-05 | **CLOSED** | |
| C-06 | **CLOSED** | |
| F-P2 | **CLOSED** for its members | new P2 factor affected_services is a fake ladder, see N-F1 |
| F-P3 | **CLOSED** for its members | new member, see N-F2 |
| F-P4 | **CLOSED** for its members | new member, see N-F2 |
| F-P5 | **CLOSED** | |
| T1-D6 | judged in 1.md after the reveal | |

New REDs:
- **N-A1** | SOURCE-POLICY RED (XF A1/A5) | task1.
  - P3 culpability_method and P4 returned_payments_method read five other factors' outputs transitively and assemble the result inside a factor binding.
- **N-B1** | SOURCE-POLICY RED (XF B1) | task1 (structural).
  - P4's and P5's prerequisite sentences have no tie rule for "booked most recently".
- **N-B6** | SOURCE-POLICY RED (XF B6) | task1 (structural).
  - P5's framing "the bundle the employer is billed under" contradicts its Premier/Elite tier.
- **N-F1** | SOURCE-FACTOR RED (two tiers select the same method; XF A6) | task0.
  - P2 affected_services.
- **N-F2** | SOURCE-FACTOR RED (unreal ladder) | task1.
  - P3 notice_remittance_exposure and P4 return_remittance_exposure.

Observations:
- **O-7**: P5's state_gate names a column rather than an eligibility gate. Separately, making acceptance of a termination notice wait on Paystride booking its own late charge is a provider-side precondition on the employer's right to give notice; real agreements bill outstanding charges on the final invoice.
- **O-8**: the overdue-balance points (above).
- **O-9**: the worklog claim "persona conditional lines no longer name the prerequisite's kind" is false: `user_scenario` is byte-identical between the r1 and r2 views in both tasks.
- **O-10**: task1's Advantage paycard funding balance sits below the 5 % reserve after every recent batch (about 17.5k against about 20k). paycard_reserve's "asked to restore" leaves no ledger record, so the ledger itself is not incomplete.

### closing_checklist (revision_2)
Not closed: both tasks remain RED.
- Coverage: 5 of 5 policies, disjoint scopes.
- Trees: task0 has n = 1 with 1 value_input edge. Task1 has n = 2 with 1 value_input edge (plus 1 state_gate). Each has an owner=user write. The graph is acyclic.
- Factors: every factor bears weight against an honest baseline on its world, figure for figure with GT. All counts are within bounds after the tests. The ladder defects are N-F1 and N-F2.
- Gates: the r2 snapshot shows 7/7 green on the audited hashes.
- Final sweep of every class raised in either revision, across all five policies:
  - C1/C2/C3 overwrites: clean except C-03's residual.
  - E3 waits: C-03 residual.
  - B1 ties: N-B1.
  - B6 framing: N-B6.
  - A1/A5: N-A1.
  - A2 assembly: clean.
  - A6 method shape: N-F1.
  - F1 realism: N-F2.
  - D6 proof text: T0-D6 and T1-D6b.
  - C-05-type caps and dedup: clean.
  - A8 and B5: clean (script).
- RED ids:
  - Charter: C-03, N-A1, N-B1, N-B6, N-F1, N-F2.
  - Task-local: T0-D6, T1-D6b.

VERDICT revision_2: task0=RED task1=RED charter=C-03,N-A1,N-B1,N-B6,N-F1,N-F2

## revision_3

### charter_global_frozen (revision_3)
- Freeze: 2026-10-23 01:35 UTC (revision_3), by the same auditor.
- Entry line: `REWORK round 3: gates 7/7 green`. The snapshot was run by this auditor (execute-only): `/tmp/erl0077_coord/snap_employer_program_settlement_and_changes_r3.txt`, 7/7 OK.
- Hashes:
  - extended.yaml f14765d38d72c336 (changed). The charter-global sections are re-derived; a copy is in /tmp/audit_employer_program_settlement_and_changes_0077/r3/ext_r3.yaml.
  - task_tools.py c8002da6be720cd4 (unchanged). action_binding_and_uuids is carried forward.
  - Views: r3/0 7a041fc32ead5224, r3/1 008ad7b75488b868.
- Base copy diff: empty.
- Claims read by item id from worklog.md, section "REWORK round 3 claims".
- GT masked until both task derivations were frozen.
- Contamination: the GT of revisions 1 and 2 is known. Every revision_3 figure is recomputed from the r3 views.

### policy_conflict_scan / rule_compute_equivalence (revision_3)
- P1 is unchanged from revision_2 (rule, compute and factors diffed: identical).
- P2:
  - affected_services and the cross-category reads are gone.
  - New factor **downtime_depth** (parameter): the shortfall is sla_uptime_target_percent less availability_percent. At least 0.5 points multiplies by 1.3; at least 0.25 by 1.15; otherwise 1. The compute `depth` / `depth_mult` matches the rule sentence, and credit_pct multiplies it in, which matches the generic assembly sentence ("the credit percentage is then multiplied by each multiplier").
- P3 and P4:
  - The exposure factors are replaced by **notice_concurrent_delinquency** and **return_concurrent_delinquency**. Each reads the other policy's selected item (the schedule of the latest return, or the schedule of the latest liable notice), guarded by "the only one booked that day". Tiers: at least 40000 adds 0.2; above zero adds 0.1; otherwise none. Compute matches the rule.
  - The method factors now decide a label (`charge_rule`) from their own records only. `charge` and `result` are plain bindings.
- P5:
  - The framing clause is dropped ("is reduced for a Payroll Card Program: …").
  - The gate sentence now reads "The early termination fee is billed, and the termination notice recorded with it, only after, where the remittance return booked most recently is the only remittance return booked that day and the deduction schedule it names carries no employer-liable shortfall notice, that schedule carries the late charge owed …".
- Script sweep: every compute_basis, superseded_clause, replaced_by and baseline quote is verbatim.
- **Transitive factor-reads table: 0 hits** across all five policies, which closes N-A1. No factor id is a substring of any tool name (XF A8).
- **"most recently" sweep** (every occurrence across the charter):
  - P1 "most recently billed" is the latest billing_month, unique per line kind.
  - P3 and P4 scope: guarded by "only … booked that day".
  - P3 and P4 concurrent factors: guarded.
  - P4 and P5 prerequisite sentences: guarded.
  - No unguarded tie remains, which closes N-B1.

### prerequisite_graph / prerequisite_sentences (revision_3)
- P4←P3: the sentence carries P3's whole scope test ("only employer-liable notice booked that day and the only one on the deduction schedule it concerns, and that schedule carries no remittance return"). The condition ends "in every other case nothing is waited on".
- P5←P4: the sentence carries P4's whole scope test.
- In every world where a wait is engaged, its record is exactly the item its resolver prices. Outside the scope nothing is waited on, and the restated base clause prices the item. XF E3 and check 7 therefore hold, and the condition equals the sentence. **C-03 closed.**
- Four-point test: passes for all three edges.
- O-7: the gate is now phrased on billing the fee and recording the notice. The column-valued `gate` remains an observation.

### override_declarations (revision_3)
- No new departure.
- downtime_depth acts only on the latest-month amount, which P2's declared overwrite settles. The earlier-month base ladder is restated.
- The concurrent factors act only on the selected items, whose base pricing is excepted.
- The P5 tier wording now states only the reduction, which closes **N-B6**.

### factor_ladders (revision_3)
- Counts (param / method):
  - P1: 6 (4 / 2), cross-difficulty card_bundle_depth.
  - P2: 5 (4 / 1), no cross-difficulty factor.
  - P3: 6 (5 / 1).
  - P4: 6 (5 / 1), cross-difficulty returned_payments_method.
  - P5: 5 (4 / 1), cross-difficulty termination_bundle.
- All ladders have 3 disjoint tiers, each fall-through equals its baseline, and no two tiers share a value or method.
- Method all-pairs:
  - P3 culpability_method: unchanged outcomes, pass.
  - P4 returned_payments_method: unchanged outcomes, pass.
  - P2 covered_fee_lines: pass.
  - P5 termination_fee_lines: pass.
  - The fake ladder N-F1 is removed.
- Realism (XF F1):
  - downtime_depth is a finer availability step within the commitment, a published SLA dimension.
  - Concurrent delinquency (a second overdue item open at the same time) is a credit-control dimension, and it reads only an overdue item's open amount.
  - No not-yet-due receivable is read anywhere, which closes N-F2.
  - Observation **O-11**: for availability below band_low_threshold, the depth is at least 0.5 at every tier's target, so the 1.3 step always applies in the 25 % and 50 % bands. The ladder is still real across the policy's scope, because it splits the 10 % band.
- Every assembly sentence is generic (XF A2).
- Task floors: task0 has card_bundle_depth (cross-difficulty) and proration_anchor / card_bundle_depth (multi-source). Task1 has returned_payments_method and termination_bundle (cross-difficulty and multi-source).

### findings (revision_3)
- Closed: **C-03, N-A1, N-B1, N-B6, N-F1, N-F2.** O-10 is closed: a reserve sweep of the r3 paycard ledger found 0 regular batches after which the 5 % reserve fails.
- T0-D6 and T1-D6b are judged in the task files after the reveal.
- New charter defects: none found.
- Final sweep of every class raised in any revision, across all five policies:
  - C1–C4: clean.
  - E3: clean.
  - B1 ties: clean.
  - B4 rounding: clean.
  - B5 verbatim: clean.
  - B6 framing: clean.
  - A1/A5: clean.
  - A2: clean.
  - A6: clean.
  - A7: T1 judged per task.
  - A8: clean.
  - F1: clean.
  - C-05 caps and dedup: clean.
  - E1 triggers: clean.
  - D1–D3 tools: unchanged, clean.

### closing_checklist (revision_3)
Written after both revision_3 reveals (2026-10-23 01:38 UTC).
- Audit files: 0.md and 1.md map one-to-one to the tasks, alongside this file. Revisions 1 to 3 are all present and older text is untouched. Both revision_3 comparisons carry PASS on all four relationships.
- Coverage and scope: 5 of 5 extended policies covered. Scopes are disjoint: {P1, P2} / {P3, P4, P5}. Task tools and GT are closed. The uuid8s are independent and frozen (task_tools.py unchanged since revision_1).
- Trees and graph:
  - task0: 1 prerequisite problem, 1 value_input edge.
  - task1: 2 prerequisite problems, 1 value_input edge plus 1 state_gate edge.
  - Each tree has an owner=user write (an SLA claim under ruling (c); a termination notice under ruling (a)).
  - The difficulty-wide graph is acyclic.
- Factors:
  - Every computation has a self-sufficient baseline giving a definite number different from gold.
  - Each has 4 to 6 factors, with at least 2 parameter and at least 1 method.
  - Each task has at least 1 multi-source and 1 cross-difficulty factor whose rows are seeded.
  - Every ladder has 3 distinct, real tiers.
  - Every factor bears weight on its world, figure for figure with GT.
- Instantiation gates: the r3 snapshot (run by this auditor on the audited hashes) shows 7/7 OK.
- Open observations (not grounds for rework):
  - O-2: commitment counted signed_date to renewal_date.
  - O-4: zero-fee tiers have no platform line.
  - O-5: the SLA credit vs unpaid cap.
  - O-6 and the D5 name check: not checkable.
  - O-7: column-valued `gate`.
  - O-8: progressive overdue-balance points.
  - O-11: depth step constant in the 25/50 bands.

VERDICT revision_3: task0=PASS task1=PASS charter=CLEAN

## revision_4

### charter_global_frozen (revision_4)
- Freeze: 2026-10-23 05:40 UTC, by the same auditor.
- Entry line: `REWORK round 4: gates 7/7 green`. The snapshot was run by this auditor (execute-only): `/tmp/erl0077_coord/snap_employer_program_settlement_and_changes_r4.txt`, 7/7 OK.
- Hashes:
  - extended.yaml 3e397e699a7b5a53 and task_tools.py 0afad5185ffe98ca. Both changed, so the charter-global sections are re-derived.
  - Views r4/0 7a041fc32ead5224 and r4/1 008ad7b75488b868, identical to r3. The task worlds and personas are unchanged.
- Base diff: empty.
- Inputs: the source items S-1, S-2 and S-3 of `audits/policy_kb/employer_program_settlement_and_changes/_difficulty.md` (read for their item text only), and the claims in worklog "REWORK round 4 claims".
- Contamination: the revision_1 to revision_3 GT is known. The task worlds are unchanged.

### delta and re-derivation (revision_4)
- **Rule diff against r3** (sentence by sentence, scripted). The only changes are these:
  - S-3 convention clauses: "a month counting as whole once the day of the month of the entry date is reached, or on the first day of the next month where that month has no such day". They are added to every whole-month count and look-back window: P1 term and launch; P2 recurrence and stabilization; P3 frequency and prior; P4 returns, prior and liable; P5 basis window, contract year and SLA window.
  - P2 sentence "Where the claimed month's invoice carries no platform_fee line, as on a tier whose monthly platform fee is zero, no service level credit is given under these provisions". In compute this is `platform_lines = COUNT(platform_fee lines of the month)` and `result … if platform_lines > 0 else 0`, with a verbatim basis.
  - P5 sentence "Where the early termination fee comes to zero, the termination notice is recorded and no early_termination_fee line is billed, a line that comes to zero not being billed". P5's replaced_by adds "a fee that comes to zero being recorded with the notice and not billed".
  - Nothing else changed: compute (apart from P2), factors, params, prerequisites and baselines.
- **S-3 convention vs the DSL.**
  - MONTHS(d1, d2) decrements when day2 < day1, and windows test `0 <= MONTHS(entry, today) < N`.
  - Probes: 01-31→02-28 gives 0; 01-31→03-01 gives 1; 01-30→02-28 gives 0; 03-31→04-30 gives 0; 03-31→05-01 gives 1; 01-31→04-30 gives 2; 12-31→02-28 gives 1.
  - Every probe equals the rule's count ("whole on the same day, or on the first day of the next month where that month has no such day"). **S-3 closed.**
  - A sweep for any "whole month" count lacking the convention finds none. The remaining day counts are calendar days or 30-day periods, and P2's consecutive gap runs between first days of months, so they need no convention.
- **S-2.**
  - The record test settles the zero-platform-fee world. "No credit" agrees with the base, whose credit on a 0.00 platform fee is itself 0.00 and is not billed.
  - The claim tool is never called in that world.
  - **S-2 closed.**
- **S-1.**
  - The P5 rule, its replaced_by, and the base "A line that comes to zero is not billed" now agree.
  - Tool body: `if amt == 0:` records the notice (status terminating, termination_notice_date) and creates no line. No floor is added.
  - The docstring describes the zero-fee effect and its receipt without example values.
  - The other four tool bodies are unchanged from revision_1, as are all signatures and names.
  - XF D1 to D3 sweep clean: no forbidden imports and no sequence words.
  - **S-1 closed.**
  - Observation **O-12**: `due_date` stays "never empty" for a zero fee. The rule's 45-day net-terms date is still computable from the notice date, so this has no consequence.
- Scripted checks:
  - compute_basis, superseded_clause, replaced_by and baseline quotes are all verbatim.
  - Transitive factor-reads: 0 hits.
  - XF A8: 0 hits.
  - The only `False` is P5's column-valued state_gate (O-7).

### class sweep (revision_4): S-1's class (zero amounts inside writes and waits) across all five policies
- P1: "no credit is booked when that amount is not above zero". P2's wait condition carves out "or no amount was billed above that fee". Clean.
- P2: zero cases (availability not below target; no platform line) give no credit, and nothing waits on P2. Clean.
- P5: fixed by S-1. Clean.
- P4's own charge is never 0.00 in scope: every tier includes late_charge_minimum_usd, either as a floor or as an addend. Clean.
- **P3: not clean.**
  - The culpability tier for payroll_processing_error / deduction_not_taken is "the percentage charge alone, with no minimum".
  - Where the notice's open amount is small enough that the rate times it rounds to 0.00, the late charge owed is 0.00. The base rule then says it is not billed ("A line that comes to zero is not billed"). One example: an open amount of 0.30 at a rate of 1.25 % gives 0.00375, which rounds to 0.00.
  - That notice is still past grace with an open amount above zero. **P4's declared condition** reads "the notice is past its due_date plus late_charge_grace_business_days business days with an open amount: a program_late_charge pointing to that notice for the late-charge period it is in". It therefore demands a late-charge row that the rules say is not billed. P4's sentence ("carries the late charge owed") is satisfied vacuously.
  - So the declared condition is stronger than the sentence, and the wait as declared cannot close: XF E3/E4 (no 0.00 carve-out by a record test) and check 7.
  - This is the same class as S-1, now in the P4←P3 edge. It is finding **R4-E4**. It is untriggered in both tasks: task1's notice is open 12480.90, and its reason is deducted_not_remitted.
- S-2's class (a write pointing to a record the base never creates):
  - P1 points to its own per-worker line.
  - P3 and P4 point to settlement items that exist by scope.
  - P5 points to no line in the zero case.
  - Clean.
- S-3's class: clean (above).
- Classes from revisions 1 to 3 re-swept across all five policies:
  - Clean: C1–C4; B1 ties ("most recently" guarded everywhere); B4; B5; B6; A1/A5; A2; A6 (ladders unchanged); F1 (no factor changed); E1; C-05 caps and dedup.
  - E3 is clean except R4-E4.

### findings (revision_4)
- **S-1 CLOSED. S-2 CLOSED. S-3 CLOSED.**
- No regression: the factors, prerequisites and task worlds are unchanged.
- **R4-E4** | SOURCE-POLICY RED (XF E3/E4, check 7; S-1's class) | task1 (structural, untriggered).
  - The P4←P3 condition requires a program_late_charge row on the latest in-scope notice even when P3's percentage-only tier prices the charge at 0.00, which the in-force base clause says is not billed. There is no 0.00 carve-out by a record test.
  - Affected: program.extended.yaml, P4 `prerequisite[0].condition`, and P3's percentage-only tier.

### closing_checklist (revision_4)
- S-1, S-2 and S-3 are closed across the whole charter. The task worlds, gold and sensitivities are unchanged, figure for figure.
- The 7 gates are green on the audited hashes (r4 snapshot).
- One new member of S-1's class (zero amounts inside a declared wait) remains: **R4-E4**, in the P4←P3 condition.
- Not closed: task1 carries R4-E4.

VERDICT revision_4: task0=PASS task1=RED charter=R4-E4

## revision_5

### charter_global_frozen (revision_5)
- Freeze: 2026-10-23 05:50 UTC, by the same auditor.
- Entry line: `REWORK round 5: gates 7/7 green`. The snapshot was run by this auditor (execute-only): `/tmp/erl0077_coord/snap_employer_program_settlement_and_changes_r5.txt`, 7/7 OK.
- Hashes:
  - extended.yaml 8edfe41cb636a001 (changed), so the charter-global sections are re-derived against the r4 copy.
  - task_tools.py 0afad5185ffe98ca (unchanged since revision_4), so the tool sections are carried forward.
  - Views r5/0 7a041fc32ead5224 and r5/1 008ad7b75488b868, identical to r3 and r4.
- Base diff: empty.
- Claims read by item id from worklog "REWORK round 5 claims".
- Contamination: the GT of revisions 1 to 4 is known. The worlds are unchanged.

### delta and re-derivation (revision_5)
- **Charter diff against r4.** These are the only changes:
  - P3: a new sentence "A late charge is booked on a shortfall notice only where the notice has an open amount of at least the de minimis amount, deminimis_open_usd; a notice with a smaller open amount carries no late charge and no line is booked for it". New param deminimis_open_usd = 25.0. Compute `result … if (in_scope and open_amt >= K('deminimis_open_usd')) else 0`, with a verbatim basis.
  - P4: the prerequisite sentence and condition add "and the notice has an open amount of at least the de minimis amount" (the condition names "at least deminimis_open_usd"). P4 params add deminimis_open_usd = 25.0.
  - P2: the sentence adds "or its platform_fee line carries billing-error credits equal to its whole amount". Compute `… if (platform_lines > 0 and platform_net > 0) else 0`.
  - Nothing else changed: factors, other compute, baselines, other prerequisites, tools.
- **R4-E4 check.**
  - At the lowest tier rate in the charter (late_charge_monthly_rate_percent 1.0, Strategic; points are never negative), an open amount of at least 25.00 gives a percentage charge of at least 0.25. So the percentage-only tier never prices 0.00 in P3's scope.
  - P4's sentence and condition now carry the same test, so the wait is never engaged on a notice whose charge would not be billed.
  - Sentence and condition have equal strength: "at least the de minimis amount" equals "at least deminimis_open_usd".
  - **R4-E4 closed.**
- **P2 addition.** A billing-error credit on a platform_fee line is "credited in full" (P1's exception covers only the per-worker line), so platform_net is either the line amount or 0. "equal to its whole amount" is therefore equivalent to platform_net > 0 failing. Rule and compute agree. Nothing waits on P2.
- Scripted checks:
  - Verbatim compute_basis, superseded_clause, replaced_by and baseline: clean.
  - Transitive factor-reads: 0. XF A8: 0. Factor counts unchanged (P1 6, P2 5, P3 6, P4 6, P5 5).
  - The only `False` is P5's column-valued state_gate (O-7).
- Four-point test on the edited P4 sentence:
  - Connective "only after". State is record-visible: open amount and late-charge row.
  - No tool name, id or snake_case token (the sentence says "the de minimis amount", not the param).
  - Its scope equals P3's scope plus the de minimis test, so the waited-on record is exactly P3's write in every engaged world (XF E3).
- Observations:
  - **O-13**: P3's de minimis sentence says "a shortfall notice". By the policy's own usage ("adds to the rate on a shortfall notice", "applied … for a shortfall notice the employer is liable for") this means the notice P3 prices. The base-priced notices always carry at least the minimum, so the reading changes no amount that could be 0.00.
  - **O-14**: P4 declares `deminimis_open_usd` (25.0) but uses it only in the prerequisite condition, not in compute. The threshold is stated in words in P4's sentence and defined in P3's rule. The two copies are equal.

### class sweep (revision_5)
Zero amounts (S-1 / R4-E4 class), every member across the five policies:
- P1: credit not above zero gives no memo. P2's wait carves out "or no amount was billed above that fee". Clean.
- P2: no credit when availability is not below target, when there is no platform line, or when the platform line is wholly credited. Nothing waits on P2. Clean.
- P3: the percentage-only tier is covered by the de minimis test. The other tiers carry the minimum. Clean.
- P4: every tier carries the minimum. Its wait carries the de minimis test. Clean.
- P5: a zero fee records the notice and books no line. Its wait engages only on an open schedule past grace whose P4 charge carries the minimum. Clean.

Re-swept classes from revisions 1 to 4, all clean:
- C1–C4.
- E3/E4.
- B1 (every "most recently" is guarded) and the S-3 month-end conventions (unchanged).
- B4, B5, B6.
- A1/A5, A2, A6, A8.
- F1: no factor changed. A de minimis threshold for late charges is standard collections practice, and 25.00 is a plausible figure.
- E1, the C-05 caps, S-2, D1–D3.

### findings (revision_5)
- **R4-E4 CLOSED.**
- No new defect. No regression: factors, the other prerequisites, tools and worlds are unchanged.

### closing_checklist (revision_5)
Written after both revision_5 reveals.
- The audit files correspond one-to-one with the tasks. Revisions 1 to 5 are appended and older text is untouched. Both revision_5 comparisons carry PASS on all four relationships.
- Coverage: 5 of 5 policies. Scopes are disjoint. Tools and GT are closed. uuid8s are independent.
- Trees: task0 has n = 1 with 1 value_input edge. Task1 has n = 2 with 1 value_input edge and 1 state_gate edge. Each has an owner=user write. The graph is acyclic.
- Factors:
  - Every computation has 4 to 6 factors (at least 2 parameter, at least 1 method), with a definite baseline that differs from gold.
  - Each task has at least 1 multi-source and 1 cross-difficulty factor, with seeded rows.
  - Every factor bears weight, figure for figure with GT.
- Gates: 7/7 green on the audited hashes (r5 snapshot).
- Open observations (not grounds for rework): O-2, O-4, O-5, O-6/D5, O-7, O-8, O-11, O-12, O-13, O-14.

VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN

## revision_6

### charter_global_frozen (revision_6)
- Freeze: 2026-10-23 11:03 UTC, by the same auditor.
- Entry line: `REWORK round 6: gates 7/7 green`. The snapshot was run by this auditor (execute-only): `/tmp/erl0077_coord/snap_employer_program_settlement_and_changes_r6.txt`, 7/7 OK.
- **Hashes unchanged:** extended.yaml 8edfe41cb636a001 and task_tools.py 0afad5185ffe98ca, the same as revision_5. Every charter-global section is therefore carried forward on those two hashes, with no re-derivation needed.
- Views:
  - r6/0 7a041fc32ead5224 (unchanged).
  - r6/1 d1eec43d70a9a996 (changed; seed-only round).
- Inputs: the source items S-4, S-5 and S-6 of `audits/policy_kb/employer_program_settlement_and_changes/_difficulty.md` (revision_3; item text only), and the claims in worklog "REWORK round 6 claims".

### seed delta and check (revision_6)
- Task1 world diff r5→r6 (scripted). frozen_time and user_scenario are unchanged. The only changes:
  - paycard_funding: one row added, 233056e8 (paycard_fee_debit, fee_type late_funding, 50.00, entry 2026-08-24, pay_date 2026-08-21, pointing to batch 7100752c). Fee debits 600af9d8 and e85b733e move 2025-07-07 → 2025-07-08, and 7f7e23db and a03cb4ce move 2025-09-05 → 2025-09-08.
  - paycard_programs.funding_balance: 24710.50 → 24660.50.
  - program_billing: the August-2025 lines bc61e2f9, c762079e and 3345d84e move entry 2025-09-03 → 2025-09-04 (due 2025-10-18 → 10-19). Their payments 389f6657, 96eda813 and ebc57bc6 move 2025-09-23 → 09-24.
- **S-4.**
  - paycard_evt_funding: "Funds arriving after that deadline are still credited, and the batch is charged late_funding_fee_usd". The 2026-08-21 batch's ACH funding was returned 2026-08-21 and replaced by the 2026-08-24 wire, after the deadline.
  - Advantage late_funding_fee_usd = 50.00, and the row points to the batch, so the fee is priced as the owning charter produces it.
  - The balance rolls to 24660.50. A reserve sweep finds the 5 % reserve held after every regular batch.
  - **Closed.**
- **S-5.** "the fifth business day of the following month". In July 2025, July 4 is a holiday, so the 5th business day is 07-08. In September 2025, September 1 is Labor Day, so it is 09-08. **Closed.**
- **S-6.** "the invoice_issue_business_day [3rd] business day of the following month". September 2025 skips Labor Day, so the 3rd business day is 09-04. The due date is +45 calendar days, giving 10-19. **Closed.**
- **Exhaustive class sweep (S-5/S-6 class: business-day-dated rows), both worlds**, scripted with a Federal Reserve holiday calendar for 2024–2026 (`/tmp/audit_employer_program_settlement_and_changes_0077/r6_bd.py`). Families checked:
  - invoice-line entry = 3rd business day of the following month;
  - invoice-line and late-charge due = entry + invoice_net_terms_days;
  - paycard monthly_program and active_card debits = 5th business day;
  - paycard receipts, batches and returns on business days;
  - deduction-schedule due = pay date + remittance_due business days;
  - schedule delivery no later than the lead business days;
  - employer-liable cure due = notice + cure business days;
  - every settlement row on a business day.
  - Result: task0 0 issues; task1 0 issues on every charter-dated family.
- Observation **O-15**: six program_invoice_payment rows in task1 are booked on non-business days. They are 30833ca1, a8daa7aa and 13dd2cef on 2025-05-25 (a Sunday), and 16f6d724, 847a247b and d0d5d68f on 2026-05-25 (Memorial Day). No charter sentence dates employer payments, so these are not members of the class. No read reaches them except as paid lines.
- **Scored reads:** none of the moved or added rows is read by any task1 compute. P4's XCOUNT counts paycard_funding_return rows only. P5's 3-month line window and SLA count read 2026 entries only. The August-2025 lines fall outside every window. Gold cannot move.

### findings (revision_6)
- **S-4, S-5 and S-6 CLOSED.** No new defect.
- No regression: the charter and tools are byte-identical, and task0 is unchanged.
- Class re-sweep: every class raised in revisions 1 to 6 was re-checked. With the hashes identical, the revision_5 charter sweep stands, and the seed-side families are clean as above.

### closing_checklist (revision_6)
- Revision_5's closing checklist stands on the identical charter and tool hashes.
- S-4, S-5 and S-6 are closed, and the seed-side business-day sweep of both worlds is clean.
- Gold and every sensitivity are unchanged, figure for figure.
- Gates are 7/7 green (r6 snapshot).
- Observations are open but not grounds for rework, with O-15 added.

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN
