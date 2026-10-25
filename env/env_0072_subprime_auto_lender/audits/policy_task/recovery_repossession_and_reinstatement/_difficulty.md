# Policy-task audit — recovery_repossession_and_reinstatement / charter-global

## revision_1

## charter_global_frozen
- Frozen 2026-10-19T23:55 (before any task GT was revealed). Auditor: independent policy-task auditor (erl-task-policy-audit), unattended.
- Freeze hashes: `recovery.extended.yaml` 0031291e970c39d83551a5ab5754655944dfba16c97c274a7787d6e9906daaee; `task_tools.py` f9d961965666ae05ed8d6bc7122bcf02bd8ea6df7ad94c848021e339d2d7799c (both match the brief).
- Masked views used for the blind phase: `.audit_views/policy/recovery_repossession_and_reinstatement/r1/0.json` 1d6becce…292c, `1.json` 70fb6584…6240 (hashes re-verified; keys present: frozen_time, initial_state, user_scenario only).
- Read: blueprint.yaml, db_schema.json, share_tools.py, products/recovery.yaml (and contract.yaml for the cross-category rules), the extended charter, task_tools.py, `audits/render_source/XF_recipe.md`, the DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (build_env only). Not read: tasks/*.json, plan.md, worklog.md, any other scenario or sibling difficulty. Scratch: /tmp/audit_recovery_0072/.
- Entry conditions: gate snapshot supplied (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (--check), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK); masked views + hashes supplied. Complete.

### policy_conflict_scan
- Base section lines 1-836 of the extended charter are byte-identical to `blueprint/products/recovery.yaml` (diff shows only the appended extended header).
- Five extended policies: `recovery_ext_agency_fee` (post_agency_recovery_fee_54cbecc0, amount_usd), `recovery_ext_sale_notice_period` (mail_corrected_sale_notice_6ba1fcf2, sale_notice_days), `recovery_ext_redemption_expense_payment` (pay_redemption_recovery_expenses_4986a691, owner=user, amount_usd), `recovery_ext_surrender_fee` (post_surrender_fee_edb82254, amount_usd), `recovery_ext_reinstatement_expense_payment` (pay_reinstatement_recovery_expenses_82a1a2b9, owner=user, amount_usd).
- Overlapping subjects: agency/surrender both post `recovery_expense_posted` but are partitioned by recovery_method (involuntary_recovery vs voluntary_surrender), each overwrite tail names the sibling. Redemption/reinstatement both write `recovery_expense_settled` (paid_by_borrower); they are partitioned by the borrower's request (redeem vs reinstate) and carry identical sibling-naming overwrites of the shared base clauses. No two policies claim the same (tool, computes).
- Trigger rule (XF 26): the three event types the tools write (`recovery_expense_posted`, `recovery_notice_sent`, `recovery_expense_settled`) all carry `triggers: []` in the base. Clean.
- Cross-category read boundary: all reads are of the customer's own contract (state_code, vehicle_book_value_usd, certified_funds_only, SCRA servicing rows, reinstatement and returned payments). No write lands in another category.
- Time anchors: the sale-notice policy changes what "earliest sale date" means. Base recovery_reinstatement and recovery_disposition still fix it at mailing date + noi_min_days_before_sale. See CG-U1.
- Scope partition (claimed, before reveal): the prerequisite graph splits into two connected components, {redemption payment ← agency fee, corrected sale notice} and {reinstatement payment ← surrender fee}. M=2 tasks can cover all five policies disjointly only by taking one component each. Whether they do is checked after the reveal.

### rule_compute_equivalence
- Every `compute_basis` quote, every prerequisite `policy_source`, every `baseline.rule` sentence and every overwrite `replaced_by` is verbatim in its policy's rule, and every `superseded_clause` is verbatim in its base rule (scripted sweep, /tmp/audit_recovery_0072/ev.py; XF 16 clean).
- I checked compute against rule at the edges:
  - agency/surrender: MX floors, the RND placement and the add-after-floor order all match the assembly sentences. The keyless tiers map tow_equipment `!= 'wheel_lift'` onto "flatbed or medium_duty_flatbed", which is exhaustive over the schema values.
  - weekday arithmetic: `DAYS(monday_reference_date, d) % 7` is correct for dates on either side of the reference date (Python modulo).
  - sale notice: I brute-forced the business-day and extended-calendar conversions for all seven mailing weekdays. Compute equals the rule wording on every day: business-day tier Mon–Fri 14, Sat 13, Sun 12; extended tier Mon 21, Tue–Sat 20, Sun 22.
  - `within_months` = `0 <= MONTHS(d, NOW) < n`. That is whole months, so a row dated exactly n months ago is excluded. "Within the last n months" does not state this edge (observation O-4).
  - redemption/reinstatement: end_offset, the weekend shift (Sat +2, Sun +1 relative to the day after recovery), the impound clock start, the floor before the cap, and (rate + per-day addition) × chargeable days all match.
- Edge mismatches are recorded as findings CG-S1, CG-S3 and CG-T1.
- `stated_amount_usd` of the corrected notice is a tool argument outside `computes`. It is fully fixed by rule sentence 3 of the sale-notice policy (it conflicts with base, see CG-U2).

### action_binding_and_uuids
- Five (target_tool, computes) pairs, each claimed by one policy. Share tools are read-only apart from verify_customer_identity and transfer_to_human_agent, so each waited-on state has exactly one writer in this difficulty.
- uuid8s: 54cbecc0, 6ba1fcf2, 4986a691, edb82254, 82a1a2b9. They are pairwise distinct, with no shared prefix or suffix, no sequence and no adjacent values.
- Docstrings: no example values, no other tool named, no before/after/first. "then see / then shows" describes visibility of the tool's own effect, not position in a sequence.
- No tool body checks any policy condition or prerequisite. Each one finds the case, creates the row and updates the outstanding figure.
- The post_agency_recovery_fee docstring says "a positive decimal number", while the policy can yield 0.00 (CG-Z1).

### prerequisite_graph
- recovery_ext_agency_fee: []; recovery_ext_sale_notice_period: []; recovery_ext_surrender_fee: [].
- recovery_ext_redemption_expense_payment → recovery_ext_agency_fee (value_input, gate posted_open, state form) and → recovery_ext_sale_notice_period (value_input, gate end_offset, state form).
- recovery_ext_reinstatement_expense_payment → recovery_ext_surrender_fee (value_input, gate posted_open, state form).
- The graph is acyclic. Every `problem` is an extended id other than itself. Every `policy_source` is verbatim in the blocked rule. Every form is state, so no fallback_reason is due. Every `resolved_by` is the depended-on policy's target_tool. Every `gate` names an existing compute binding of the blocked policy. The effects hold: posted_open rises by the posted fee, and end_offset moves from the stale stated date to the payment date. No authoring-viewpoint wording.
- The redemption → sale-notice edge's `condition` reads "the latest" notice while its sentence is existential (CG-P1).

### prerequisite_sentences
- E1, redemption ← agency fee: "On a case whose vehicle an agency recovered involuntarily, the redemption expense payment is not fixed until the agency's involuntary repossession fee stands posted on the case."
  - Connective: "not … until".
  - State: an involuntary_repossession_fee expense standing posted on the case, in table words.
  - No tool, id or snake_case token. Scope matches the condition (involuntary_recovery only).
  - Single writer: post_agency_recovery_fee_54cbecc0.
  - Derivation: the reader sees no such expense on the case and looks for the rule that posts the agency's involuntary repossession fee. That is the agency fee rule, whose sentence 2 posts it "as an expense of type involuntary_repossession_fee". One reading. PASS.
- E2, redemption ← sale notice: "The redemption expense payment is fixed only after a notice of intent to sell whose earliest sale date falls at least the class minimum notice period after its mailing date stands on the case."
  - Connective: "only after". State form. No tool, id or snake_case token.
  - Single writer: mail_corrected_sale_notice_6ba1fcf2 (the system's first notice is not a write of this difficulty).
  - Derivation: the reader sees the case's notice falling short of noi_min_days_before_sale and looks for the rule that mails a compliant notice. That is the sale-notice rule, sentence 2 ("a corrected notice of intent to sell is mailed … on the day the shortfall is found").
  - Strength: the sentence is existential ("a notice … stands on the case") while the condition and the compute (`LATEST`) read only the latest notice → CG-P1.
- E3, reinstatement ← surrender fee: "On a case whose vehicle the borrower surrendered voluntarily, the reinstatement expense payment is fixed only after the voluntary surrender fee stands posted on the case."
  - Connective: "only after". State: a voluntary_surrender_fee expense. Scope matches.
  - Single writer: post_surrender_fee_edb82254. One reading.
  - PASS, except that the waited-on value can be 0.00 (CG-Z1).
- No depended-on rule restates a blocked rule's sentence. No rule names another problem's tool. No rule states a cross-problem order outside E1–E3. No base sentence grounds an edge.

### override_declarations
Sentence-by-sentence against each `base_policy_refs` entry. Retirements of conflicting text:
- agency_fee / surrender_fee vs recovery_evt_expenses: the fragments "involuntary_repossession_fee_usd for recovery_method involuntary_recovery" and "voluntary_surrender_fee_usd for voluntary_surrender" are retired. Each tail names the sibling and restates the rest of the schedule as in force (XF 18–20 clean). Every other recovery_evt_expenses sentence is followed: recovered-status posting, reasonableness, removal only once for assessed_in_error, no courtesy waiver.
- redemption / reinstatement vs recovery_disposition: "Recovery expenses are settled only when the case is reinstated, redeemed or sold." is retired, with sibling-symmetric tails.
- redemption / reinstatement vs recovery_redemption and recovery_reinstatement: the expense-portion clauses are retired, and each states that the contract portion stays.
- redemption / reinstatement vs recovery_evt_expenses: the storage-posting sentence and the storage-rate clause are retired. Each restates the in-force content for storage posted on release/sale and for storage in a reinstatement quote (XF 19 clean). The remaining base sentences are followed: certified channels, release within vehicle_release_business_days, insurance proof for a reinstatement release, no insurance for a redemption.
- sale_notice vs recovery_evt_recovery_and_noi: "The notice of intent to sell states an earliest sale date (deadline_date) exactly noi_min_days_before_sale calendar days after its mailing date" is retired. The re-mail/restart sentence stays compatible.

Undeclared or conflicting departures:
- The earliest sale date in base recovery_reinstatement and recovery_disposition (CG-U1).
- The stated reinstatement amount in base recovery_evt_recovery_and_noi (CG-U2).
- The reinstatement quote's expense portion (CG-S2).
- recovery_cure_notice (in the sale-notice refs) is followed in full. Its states equal extended_notice_states ∪ {WI}.

### factor_ladders
All-pairs method tier tables (XF 8):

| policy / method factor | pair | distinguishing input | verdict |
|---|---|---|---|
| agency_fee / book_value_reduction | low vs mid | book value (low reads book value through RND(6%·bv) and MX; mid is a constant) | PASS |
| | low vs none | book value | PASS |
| | **mid vs none** | none: flat 100.00 vs 0. Both are constants with no input, so the pair differs only in a number | **FAIL (CG-M1)** |
| surrender_fee / surrender_value_basis | low vs mid | book value | PASS |
| | low vs none | book value | PASS |
| | **mid vs none** | none: flat 20.00 vs 0 | **FAIL (CG-M1)** |
| sale_notice / state_period_convention | business-day vs extended | mailing weekday: Mon → 14 vs 21; Sat → 13 vs 20 (different counting conventions over the weekday) | PASS |
| | business-day vs flat | Sat mailing 13 / Sun 12 vs flat 15 (business-day tier reads the weekday) | PASS (Mon–Fri give a constant 14, so the shape only shows on weekend mailings) |
| | extended vs flat | Mon mailing 21 vs 15 (roll-forward reads the weekday) | PASS |
| redemption & reinstatement / storage_clock_start | impound vs weekend | latest impound_lot_charges posting date (a data-selected start) vs recovery weekday | PASS |
| | impound vs standard | impound posting date | PASS |
| | weekend vs standard | recovery weekday (start moved past the following Monday) | PASS |

Per-policy structure:

| policy | factors (label) | param / method | multi-source | cross_difficulty |
|---|---|---|---|---|
| agency_fee | state_fee_ceiling (P), book_value_reduction (M), keyless_handling (P), weekend_recovery (P) | 3 / 1 (method fails CG-M1) | keyless_handling: case.keys_obtained ∧ activity rows key_replacement_fee ∧ class tow_equipment | state_fee_ceiling, book_value_reduction (contract) |
| sale_notice_period | state_period_convention (M), military_service_days (P), reissue_days (P), prior_reinstatement_days (P), funds_arrangement_days (P) | 4 / 1 | funds_arrangement_days tier 2 (contract row ∧ returned-payment rows); tier 1 is single-condition | four contract-reading factors |
| redemption_expense_payment | lot_day_rate (P), lot_grace_days (P), storage_clock_start (M), keyless_lot_handling (P) | 3 / 1 | keyless_lot_handling (case ∧ activity rows ∧ tier param) | lot_day_rate (contract state) |
| surrender_fee | surrender_state_ceiling (P), surrender_value_basis (M), dropoff_delivery (P), surrender_timing (P) | 3 / 1 (method fails CG-M1) | none: dropoff reads storage_lot and recovery_date on one case row; timing reads two dates on one row | state ceiling, value basis (contract) |
| reinstatement_expense_payment | same four as redemption | 3 / 1 | keyless_lot_handling | lot_day_rate |

- Ladder hygiene: every ladder has ≥3 tiers, every tier is stated in the rule (condition and value or method), every tier is implemented in compute, and every fall-through equals the declared baseline. No `decides` is `result`. Binding sets are disjoint within each policy. No factor reads another factor's binding (XF 1–6 clean in compute; see CG-S3 for a rule wording that admits a factor-reads-factor reading). No factor id is a substring of a tool name (XF 7, scripted).
- Tier gaps and overlaps over scope (XF 9): one uncovered case. military_service_days does not cover "applied ≥ 1 and ended > applied"; compute gives 0, which is a state servicing does not produce (O-2). Everything else is partitioned.
- Distinct outcomes: the state ceilings coincide with the fall-through for low classes (Class 1–2 surrender fee 150 = surrender_limit_a; agency limits above the Class 1–4 fees). That is how a cap behaves, not one tier written twice (O-3).
- Realism, tier by tier:
  - state limits are worded as company schedules;
  - value-scaled fee caps, keyless and weekend recovery surcharges, the certified-funds and returned-payment notice days, reissue days after a defective notice, servicemember days, state-capped storage rates, lot grace terms, weekend lot-intake clock, impound clock and keyless lot handling are all practices a subprime servicer or its vendors use;
  - prompt-surrender and drop-off credits are plausible voluntary-surrender incentives;
  - two defects: **prior_reinstatement_days** (CG-R1) and the **program-start date conjuncts** (CG-R2).

### findings
Each finding gives symptom → root cause → evidence → demonstrated consequence → location. "Tasks" says which task files pick it up.

**CG-U1 SOURCE-POLICY RED: undeclared override of the earliest sale date (XF 21–22).**
- Symptom: the sale-notice rule makes each notice's earliest sale date "the notice's sale period … after its own mailing date … instead of being a flat noi_min_days_before_sale days". Two in-force base sentences still define that date as mailing + 15:
  - recovery_reinstatement: "The reinstatement payment must be received before the earliest sale date, which falls noi_min_days_before_sale after the notice of intent to sell was mailed."
  - recovery_disposition (not even in the policy's base_policy_refs): "The vehicle may be sold only on or after the earliest sale date, noi_min_days_before_sale after the notice of intent to sell was mailed."
- The overwrite retires only the recovery_evt_recovery_and_noi clause.
- Consequence: take a WI case whose corrected notice is mailed on day D with a 46-day period. On day D+20 a reinstatement payment is too late under base (D+15 has passed) and timely under extended (sale date D+46). A sale on D+20 is allowed under base and forbidden under extended. Two answers for act-now/refuse.
- Location: recovery_ext_sale_notice_period.overwrite; base recovery_reinstatement sentences 3–4; base recovery_disposition sentences 1–2.
- Tasks: no scored value moves in task 0 or task 1 (see their files).

**CG-U2 SOURCE-POLICY RED: undeclared override of the notice's stated reinstatement amount.**
- Base recovery_evt_recovery_and_noi says the notice states "the reinstatement amount where reinstatement is available (stated_amount_usd, otherwise 0.00)".
- The extended rule says "where reinstatement is still available it states the stated_amount_usd of the latest reinstatement quote on the case, or 0.00 while no quote stands on the case".
- No overwrite names the base clause.
- Consequence: a case with reinstatement available and no quote, needing a corrected notice, gets the computed reinstatement amount under base and 0.00 under extended. That is two values for the scored `stated_amount_usd` argument of mail_corrected_sale_notice_6ba1fcf2.
- Location: recovery_ext_sale_notice_period rule sentence 3 and its overwrite.
- Tasks: task 0 sits on the max-reinstatement branch (0.00 under both). No consequence there.

**CG-S1 SOURCE-POLICY RED: the business-day tier always yields a notice the same rule declares short.**
- Rule sentence 5: for MN/WI, 10 business days from the day after mailing, which is 14 calendar days (Mon–Fri mailing), 13 (Sat) or 12 (Sun). Brute-forced; matches compute.
- Rule sentence 1 applies the period to "the first one mailed after a recovery and any later one".
- Rule sentence 2: "A notice whose stated earliest sale date falls fewer than noi_min_days_before_sale calendar days after its mailing date does not start the sale period, and a corrected notice … is mailed".
- Consequence: a first notice on a WI contract mailed on a Tuesday, with no SCRA rows, no reinstatement payment, certified_funds_only false and no recent return, gets a 14-day period from the rule. The same rule then says that notice does not start the sale period and must be corrected. The policy contradicts itself on the notice it prescribes, and the company schedule places MN/WI below its own 15-day statutory floor (XF 10).
- Location: recovery_ext_sale_notice_period rule sentences 1, 2 and 5; params business_day_notice_days.
- Tasks: task 0's corrected notice is 46 days. No scored consequence.

**CG-S2 SOURCE-POLICY RED: two clauses fight over the expense portion of a reinstatement quote.**
- The reinstatement overwrite of base recovery_reinstatement: "The expense portion of a reinstatement is the reinstatement expense payment this rule figures". The base reinstatement amount is what a recovery_reinstatement_quoted row states, in expenses_usd and stated_amount_usd.
- The sibling storage-rate overwrite, carried in both payment rules: "storage stated in a reinstatement quote, is charged at storage_fee_per_day_usd for each chargeable day (recovery_msr_chargeable_storage_days …)".
- Consequence, on the task 1 world after the surrender fee (65.00) is posted, with a quote dated 2026-10-19 good through 2026-10-24:
  - reading A (expense portion = payment figure): 65 + (20 + 8) × (14 − 2 − 0) = 401.00;
  - reading B (class-rate quote storage): 65 + 30 × (14 − 2) = 425.00.
- Location: recovery_ext_reinstatement_expense_payment overwrite[1] vs overwrite[3]/rule sentence 4.
- Tasks: there is no quote write in either task.

**CG-S3 SOURCE-POLICY RED: "the class fee" in the value-reduction tier has two readings once a state limit applies (XF 11; also a latent XF 1).**
- Agency rule: "Where the contract's state_code is one of limit_states_a, the class fee is limited to state_limit_a_usd", then "the value reduction is the amount by which the class fee exceeds low_value_fee_pct percent of that book value". Compute uses the unlimited `P('involuntary_repossession_fee_usd')`.
- Consequence for agency: Class 6, WI, book 7,000.00: compute 500 − (600 − 420) = 320.00; the limited-fee reading gives 500 − (500 − 420) = 420.00.
- Surrender has the same structure. Consequence: Class 3, GA, book 5,000.00, no credits: compute 150 − (175 − 100) = 75.00; limited-fee reading 150 − (150 − 100) = 100.00.
- The limited-fee reading also makes the reduction factor read the ceiling factor's output.
- Location: rule sentences 4–5 of recovery_ext_agency_fee and of recovery_ext_surrender_fee.
- Tasks: both tasks sit on the mid (flat) tier. No scored consequence.

**CG-P1 SOURCE-POLICY RED: the prerequisite sentence for E2 is broader than its condition and compute.**
- Sentence: "fixed only after a notice of intent to sell whose earliest sale date falls at least the class minimum notice period after its mailing date stands on the case", which is existential.
- Condition: "The latest recovery_notice_sent row … has a deadline_date at least noi_min_days_before_sale …". Compute reads `LATEST(... 'deadline_date' ...)`.
- Consequence: a case with a compliant first notice and a later short re-mailed notice (re-mailing is a base procedure, noi_resend_if_undeliverable):
  - the sentence holds, so the reader pays with the end date capped at the short notice's stated date;
  - the condition fails, so a corrected notice is due first and the end date is the payment date;
  - two payment amounts.
- Location: recovery_ext_redemption_expense_payment rule sentence 6 / prerequisite[1].
- Tasks: task 0's case has a single notice. No consequence.

**CG-T1 SOURCE-POLICY RED: "the latest notice of intent to sell" has no same-day tie rule (XF 12).**
- The sale-notice rule has a corrected notice mailed "on the day the shortfall is found", which can be the short notice's own mailing day. Both rows then share activity_date.
- `LATEST` keeps the first row in iteration order (strict `>`), i.e. the seeded short notice.
- Consequence: a redemption or reinstatement payment that day reads the short notice's stated date as the storage end. The rule's reader takes the corrected notice. Different amounts.
- Location: latest_sale_date in both payment policies; base recovery_reinstatement / recovery_disposition "latest notice_of_intent_to_sell".
- Tasks: in task 0 the notices are on 2026-10-06 and 2026-10-19. No consequence.

**CG-Z1 SOURCE-CHAIN-class RED (XF 25): 0.00 values on prerequisite edges.**
- (a) Surrender fee → E3. Class 1/2 (150.00) in AL/FL/GA (limit 150), book 4,000.00 (reduction 150 − 80 = 70), company drop-off (50), prompt surrender (30) gives MX(0, 150 − 70 − 50 − 30) = 0.00. That is a 0.00 row "standing posted" and an edge that moves nothing. The surrender tool explicitly accepts 0.00.
- (b) Agency fee → E1. Class 6 in limit_states_a, weekday recovery, keys obtained, book ≤ 1,666.67 gives MX(0, 500 − (600 − 0.06·bv)) = 0.00 (Class 5 or limit_b: book ≤ 833.33). The docstring requires "a positive decimal number".
- Neither edge carves out the 0.00 case with a record test.
- Location: compute `result` of both fee policies; E1/E3.
- Tasks: task values are 570.00 and 65.00. No consequence.

**CG-M1 SOURCE-FACTOR RED: mislabelled method pair (XF 8).**
- book_value_reduction (agency) and surrender_value_basis (surrender): the mid tier ("the flat mid_value_reduction_usd" / "the flat surrender_mid_value_reduction_usd") and the fall-through ("no value reduction") are both constants with no input. That pair substitutes a number into an identical formula.
- With the pair failing, each fee policy has no `method` factor that passes the shape test.
- Location: factors[1] of recovery_ext_agency_fee and of recovery_ext_surrender_fee.
- Tasks 0 and 1 both take the mid tier against the "none" baseline; the demonstrations are in their files.

**CG-R1 SOURCE-FACTOR RED (realism): prior_reinstatement_days.**
- The tier conditions "a reinstatement payment … within the last reinstated_recent_months months" (+10) vs "only reinstatement payments older than that" (+5) are not something a repossession servicer weighs in setting a notice-of-sale period.
- That period follows the statutory or company minimum. The charter's own servicing-history additions (certified funds, recent returns, reissue, servicemember status) each tie to the borrower's ability to act on the notice.
- With reinstatement_max_per_contract = 1, any earlier reinstatement already means reinstatement is unavailable whatever its age. Grading it by a 24-month recency window is an invented history-recency tier (XF 10: no tenure or count inventions).
- Location: recovery_ext_sale_notice_period rule sentence 8, factors[3].
- Task 0 picks this up (+10 in its scored period).

**CG-R2 SOURCE-FACTOR RED (realism / non-dividing condition): program-start date conjuncts.**
- Affected: lot_grace_days (both payment policies) "and the recovery_date is on or after extended_grace_from / no_grace_from" (2025-01-01), and dropoff_delivery "and the recovery_date is on or after dropoff_program_from" (2025-01-01).
- Every customer who reaches these writes holds a case in recovered status on a 2026-10 clock. Under this charter's own limits (storage cap 45 days, sale after the notice period of at most ~70 days) such a case is recovered within months of the clock, so a recovered case dated before 2025-01-01 is not a state real servicing produces.
- The conjunct holds for every such customer and divides none.
- Location: factors lot_grace_days ×2, dropoff_delivery; rule sentences 8 (payment rules) and 6 (surrender).
- Tasks: no scored value moves.

Observations (not rework grounds):
- O-1: after a borrower expense payment that covers unposted storage, SUM(posted) − SUM(settled) goes negative while the tool clamps expenses_outstanding_usd at 0.00. So recovery_msr_expenses_outstanding ("equals expenses_outstanding_usd") and the case field diverge. This is by design of the storage-never-posted overwrite (the seeded prior case in task 0 already shows −120.00).
- O-2: military_service_days does not cover the applied < ended gap (see factor_ladders).
- O-3: state ceilings coinciding with the fall-through in low classes (see factor_ladders).
- O-4: the `within_months` boundary for exactly-n-months rows is unstated (see rule_compute_equivalence).
- O-5: military_service_days "left service" adds days with no time bound after separation.
- O-6: lot_day_rate keys the storage rate to the contract's state rather than the lot's location.

## closing_checklist
Not reached: open REDs.

### post-reveal difficulty notes (written after both tasks' comparisons; the charter-global section above is unchanged)
- Scope: task 0 charter_scope = {agency_fee, sale_notice_period, redemption_expense_payment}; task 1 = {surrender_fee, reinstatement_expense_payment}. Pairwise disjoint and jointly complete, as predicted from the graph components.
- Every scored value in both tasks matches the blind derivations: 570.00 / 46 / 0.00 / 1,863.00 and 65.00 / 261.00, with every factor_sensitivity and baseline_result figure equal.
- Open REDs by task:
  - task 0: T0-F1 (CG-M1), T0-F2 (CG-R1), T0-P1 (stale proof text, 7 members (a)–(g));
  - task 1: T1-F1 (CG-M1), T1-P1 (false multi-source claim).
- Open charter-wide REDs: CG-U1, CG-U2, CG-S1, CG-S2, CG-S3, CG-P1, CG-T1, CG-Z1, CG-M1, CG-R1, CG-R2.
- Closing checklist not run: REDs remain open.

VERDICT revision_1: task0=RED task1=RED charter=CG-U1,CG-U2,CG-S1,CG-S2,CG-S3,CG-P1,CG-T1,CG-Z1,CG-M1,CG-R1,CG-R2

## revision_2

## charter_global_frozen (revision_2)
- Re-derived in full because both source hashes changed: `recovery.extended.yaml` 0031291e… → e996dc6301643c470f8402d303564271154d5be0b3ce36da15a244c92921c0ae; `task_tools.py` f9d96196… → 4e39b836e2e6aac7448f0f3354c5a51ef4bb0b5f849329df47e801c787cbc583.
- Written 2026-10-20T05:55 from the charter, the tools, XF_recipe.md and rework_claims_r2.md (item ids only), before any round-2 GT read.
- Gate (worklog tail): `REWORK round 2: gates 7/7 green`.
- Gate snapshot (coordinator snapshot.sh, 2026-10-20T05:45:27): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Views: r2/0.json ba0636c0…76bc, r2/1.json cf7f3011…9d68.
- Not read: plan.md (it holds the reworker's probe table), worklog.md beyond its last line, any other scenario or sibling.

### policy_conflict_scan / action_binding_and_uuids / prerequisite_graph (revision_2)
- Base section still byte-identical to blueprint/products/recovery.yaml.
- Five policies, tools, (tool, computes) pairs and uuid8s are unchanged and distinct.
- Tool bodies are unchanged and validate nothing. Both fee docstrings now say "positive". There are no example values and no ordering words.
- XF 26 trigger rule: clean.
- The graph is unchanged and acyclic: E1, E2, E3 are all state form, value_input, with gates that exist.
- Scopes: two components, matching the two tasks.

### rule_compute_equivalence (revision_2)
- Scripted sweep: every compute_basis quote, prerequisite source, baseline sentence and replaced_by is verbatim in its rule. Every superseded_clause is verbatim in its base rule, including the two new ones in recovery_reinstatement and recovery_disposition.
- Business-day tier at 12 days, brute-forced against compute for all seven mailing weekdays: Mon/Tue/Wed/Sun 16, Thu/Fri 18, Sat 17. All are ≥ noi_min_days_before_sale 15.
- Taper, minimum floors, after-hours/weekday drop-off, grace window (DAYS(recovery_date, NOW) ≤ 30), late-mailing lag, and LATEST by deadline_date all match the rule wording.
- The returned-payment boundary sentence now matches MONTHS() exactly.

### prerequisite_sentences (revision_2)
- E1 and E3 are unchanged: PASS.
- E2: "The redemption expense payment is fixed only after the notice of intent to sell on the case that states the latest earliest sale date allows at least the class minimum notice period between its own mailing date and that date."
  - Connective: "only after". State form.
  - Sentence, condition ("the row with the latest deadline_date") and compute (`LATEST(... date_field='deadline_date')`) now read the same row.
  - Single writer: the corrected-notice tool. PASS.
  - Residual tie case (two notices stating the same latest date, only one compliant): see O2-1.

### override_declarations (revision_2)
- Retirements:
  - recovery_evt_recovery_and_noi deadline clause;
  - recovery_reinstatement earliest-sale-date sentences 3–4 (new);
  - recovery_disposition sentences 1–2 (new);
  - the agency/surrender schedule fragments, disposition settlement, redemption/reinstatement expense clauses and storage clauses, as in revision_1, with self-naming, sibling-symmetric tails.
- The notice's stated amount now follows the base meaning ("the reinstatement amount where reinstatement is available"), refined to a same-day quote and adding charged-off from base recovery_reinstatement. No conflict.
- The quote's expenses_usd is now assigned once, to the reinstatement payment rule, in both the overwrite and the sibling storage sentence. The class-rate clause is kept only for storage posted on release or sale.

### factor_ladders (revision_2)
All-pairs method tier tables:

| factor | pair | distinguishing input | verdict |
|---|---|---|---|
| book_value_reduction | low vs taper | low reads the class tier parameter and floors at 0 (Class 1, book 7,000: MX(0, 375 − 420) = 0; taper at 8,000 = 120) | PASS |
| | low vs none | book value | PASS |
| | taper vs none | book value (9,800 → 66.00; 11,000 → 30.00 vs 0) | PASS |
| surrender_value_basis | same structure (taper 1.5% below 10,000) | — | PASS ×3 |
| state_period_convention | business-day vs extended vs flat | mailing weekday (16/18/17 vs 20/21/22 vs 15) | PASS ×3 |
| storage_clock_start | unchanged | — | PASS ×3 |

Per-policy counts:

| policy | factors | param / method | multi-source | cross_difficulty |
|---|---|---|---|---|
| agency_fee | 4 | 3 / 1 | keyless_handling | 2 |
| sale_notice | 5 (state_period_convention, military, reissue, late_mailing_days, funds) | 4 / 1 | funds tier 2 | 3 contract-reading |
| redemption | 4 | 3 / 1 | keyless_lot_handling | lot_day_rate |
| surrender | 4 | 3 / 1 | none (task 1 carries one in the payment) | 2 |
| reinstatement | 4 | 3 / 1 | keyless_lot_handling | lot_day_rate |

- Every ladder has ≥3 disjoint tiers, stated in the rule and in compute, with the fall-through equal to the baseline.
- No factor reads another factor's binding.
- No factor id is a substring of a tool name.
- Realism of the new tiers:
  - taper reductions and fee minimums: real fee-schedule shapes;
  - staffed vs after-hours drop-off credit: real;
  - extended grace only when paid within 30 days of recovery: a dividing, plausible lot term;
  - no-grace lots unconditional;
  - late_mailing_days: a company remediation allowance for a notice mailed late after recovery (O2-2).

### closure of round-1 REDs (each re-checked on the r2 text)
- **CG-U1 closed.** Both base clauses are retired and both policies are in base_policy_refs. The new definition carries a residual ambiguity (CG2-E1).
- **CG-U2 closed.** The undeclared "0.00 while no quote" departure is gone. The new same-day-quote wording leaves a residual cross-policy dependence (CG2-Q1).
- **CG-S1 closed.** The minimum business-day period is 16.
- **CG-S2 closed as a clause conflict:** one rule now owns the quote's expense portion. Residual reading: CG2-Q1.
- **CG-S3 closed.** "taken before any state limit" names the unlimited fee; compute matches.
- **CG-P1 closed.** Sentence, condition and compute agree.
- **CG-T1 closed.** LATEST by deadline_date: same-day mailings no longer select different dates, and equal deadline dates give equal end dates.
- **CG-Z1 closed.** Minimums of 150 and 25 apply; neither fee can be 0.00; both docstrings say positive.
- **CG-M1 closed.** Taper tiers pass every pair.
- **CG-R1 closed.** The factor and its contract reads are removed.
- **CG-R2 closed.** Date conjuncts are removed; the grace window divides customers.
- **O-2 and O-4 closed.**

### findings (revision_2)
**CG2-E1 SOURCE-POLICY RED: the redefined earliest sale date has two readings when a later notice is short (introduced by the CG-U1 rework).**
- The replaced_by now carried in both base policies' place reads: "the earliest sale date, which is the latest earliest sale date stated in the case's notices of intent to sell when the notice that states it allows at least noi_min_days_before_sale calendar days after its own mailing date … and while no such notice stands no earliest sale date has started to run" (and "… the vehicle may not be sold").
- Situation:
  - notice A is mailed on day D stating D+16 (compliant);
  - later notice B is mailed D+10 stating D+20 (10 days, short), for example a clerical re-mail. A clerical short notice is the very state task 0's world seeds.
  - A reinstatement payment arrives on D+18.
- Reading 1 ("latest among the compliant notices"): the earliest sale date is D+16, so the payment is too late and the vehicle may be sold.
- Reading 2 ("the latest stated date, provided its own notice is compliant"): the latest date D+20 sits on a short notice, so no qualifying notice states the latest date and no earliest sale date is running. The payment is allowed and the sale is forbidden.
- Consequence: two act-now/refuse outcomes for reinstatement and two sale-eligibility outcomes.
- Location: recovery_ext_sale_notice_period overwrite[1] and overwrite[2], rule sentences 3–4.
- Tasks: not reached in task 0 (only one notice before the correction) or task 1 (single compliant notice).

**CG2-Q1 SOURCE-POLICY RED: a quote's expense portion borrows the payment rule's grace window, which keys on "the payment date"; the notice's scored stated amount inherits the ambiguity (also XF 6).**
- The reinstatement overwrite says: "The expense portion of a reinstatement, including the expenses_usd a reinstatement quote states, is the reinstatement expense payment this rule figures, with storage running through the quote's good-through date for a quote".
- The grace sentence it borrows says: "where the case's storage_lot is one of extended_grace_lots and the payment date is no more than extended_grace_window_days calendar days after the recovery_date …". A quote has no payment date.
- Members, listed exhaustively:
  - (a) recovery_ext_reinstatement_expense_payment overwrite[1] / rule sentence 2 with rule sentence 8;
  - (b) the sibling storage sentence (rule sentence 4 of both payment policies, overwrite[3]), which routes quote storage through "the … payment rule that matches it";
  - (c) recovery_ext_sale_notice_period rule sentence 5: "it states the reinstatement amount a reinstatement quote dated the mailing date states". This defines the scored `stated_amount_usd` of mail_corrected_sale_notice_6ba1fcf2 as another policy figures it (XF 6).
- Demonstration:
  - Lakeshore lot, WI, Class 6, keys obtained, weekday recovery on day R, reinstatement available;
  - corrected notice and quote dated R+28, good through R+33;
  - reading "payment date" as the quote date (R+28 ≤ 30): 5 grace days, chargeable 28, storage 560.00;
  - reading it as the good-through date (R+33 > 30): class grace 2, chargeable 31, storage 620.00;
  - the stated amount differs by 60.00.
- Tasks:
  - task 0's notice states 0.00 (reinstatement used up);
  - task 1's seeded notice sits on a no-grace lot, where both readings give 913.56.
  - Neither task reaches the ambiguity.

**T0-R2-S1** (task-level, see 0.md): the seeded 2025 notice states 0.00 where the r2 rule gives 1,929.27, and the proof claims the 2025 case is priced by the current rules.

Observations:
- O2-1: E2 and the earliest-sale-date clauses assume one notice states the latest date. Two notices stating the same latest date, one compliant and one short, leave "the notice that states it" undetermined. The end date is equal either way.
- O2-2: late_mailing_days adds days to a corrected notice according to how long after recovery it is mailed. This is a company remediation, partly overlapping reissue_days. It is not statutory (UCC 9-611/9-612 set reasonableness, not added days), but it is a plausible published practice.
- O-1, O-3, O-5 and O-6 from revision_1 stand.

## closing_checklist (revision_2)
- Both tasks' values, owners, order and trees match GT.
- Factor structure passes.
- Scopes are disjoint and complete.
- Not closed: CG2-E1, CG2-Q1 and T0-R2-S1 remain open.

VERDICT revision_2: task0=RED task1=PASS charter=CG2-E1,CG2-Q1

## revision_3

## charter_global_frozen (revision_3)
- Hashes:
  - `recovery.extended.yaml` e996dc63… → a19c1ee30aa12bc2e044b57eb47999238b58b321175d34768b358440378dd653 (changed, so the changed sections are re-derived below);
  - `task_tools.py` 4e39b836e2e6aac7448f0f3354c5a51ef4bb0b5f849329df47e801c787cbc583 (unchanged, so action_binding_and_uuids is carried forward from revision_2 by reference).
- Gate (worklog tail): `REWORK round 3: gates 7/7 green`.
- Snapshot (snapshot.sh, 2026-10-20T06:59:46): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Views: r3/0.json c009bb69…6769, r3/1.json ede6aa4e…0eed.
- Written 2026-10-20T07:05, before any round-3 GT read. plan.md not read.

### re-derived sections (revision_3)
- **Verbatim sweep (scripted).** Every compute_basis, prerequisite source, baseline sentence and replaced_by is in its rule. Every superseded_clause is verbatim in its base rule, including the new recovery_evt_recovery_and_noi "the reinstatement amount where reinstatement is available (stated_amount_usd, otherwise 0.00)" and recovery_reinstatement "the contract portion posts to the contract as a reinstatement payment and the expense portion settles the case's expenses". No factor id is a substring of a tool name. Compute of all five policies evaluates to the revision_2 figures on both worlds.
- **Overrides.**
  - Sale notice retires 4 clauses (deadline, stated amount, reinstatement sale-date, disposition sale-date). Each is self-naming and restates its in-force content: "0.00 where reinstatement is not available"; the counting, the endpoints, and the no-notice case.
  - Reinstatement payment retires the base expense-settlement clause. It keeps the base quote meaning: expenses outstanding through the good-through date at storage_fee_per_day_usd.
  - The base reinstatement-amount clause is no longer retired and stays in force for quotes; the payment replaces the quote's expense portion only at payment, as declared.
  - Redemption overwrites are unchanged.
  - XF 18–22 clean.
- **Prerequisites.** E2 now reads: "The redemption expense payment is fixed only after the latest earliest sale date stated on the case is stated by at least one notice of intent to sell that allows the class minimum notice period between its own mailing date and that date." The condition reads "at least one row carrying the latest deadline_date has that deadline_date at least noi_min_days_before_sale … after its own activity_date". Compute uses LATEST by deadline_date.
  - Sentence, condition and compute agree, and the tie case now has one reading (O2-1 closed).
  - Connective "only after"; state form; single writer. E1 and E3 are unchanged. Graph acyclic. PASS.
- **Factor ladders.** Unchanged from revision_2, carried forward by reference: method all-pairs PASS; counts 4/5/4/4/4; multi-source and cross-difficulty present.
- **XF recipe, all 31 points re-checked on the r3 text.**
  - Points 1–7: no factor reads another, assembly is ordered, nothing defined "as another policy figures it". The only remaining cross-rule mentions are sibling-scope tails (agency/surrender, settlement, storage), as XF 20 requires.
  - Points 8–10: method tables PASS; tiers partition their scope; realism unchanged from revision_2.
  - Points 11–17: edges and decoys probed by recomputation; the earliest-sale-date record test is unique for compliant-then-short, short-then-compliant, same-day and tied-date sequences; rounding and boundary wording match.
  - Points 18–22: clean.
  - Points 23–26: state-form routes, no cross-holding pairing, minimums prevent 0.00, triggers clean.
  - Points 27–29: both seeded notices reproduce under the r3 stated-amount formula (1,849.27 and 775.56); the proof text is current.
  - Points 30–31: renderer items, not applicable.

### closure of revision_2 REDs
- **CG2-E1 closed.** The earliest sale date is now one record test ("the latest deadline_date among the case's notices … whose own deadline_date falls at least noi_min_days_before_sale … after their own activity_date; a notice whose deadline_date falls fewer days … never sets or moves the earliest sale date"). In the revision_2 demonstration (compliant A stating D+16, later short B stating D+20, payment on D+18) there is now one answer: the date is D+16 and the payment is too late.
- **CG2-Q1 closed.**
  - (a) The quote keeps the base expenses at the class rate; no grace test keyed on a payment date is borrowed.
  - (b) The sibling storage sentence is self-contained.
  - (c) The notice's stated amount has its own mailing-date formula, declared as an overwrite. No rule defines a figure as another policy figures it.
  - The revision_2 Lakeshore demonstration now has one value (class-rate quote storage; the notice uses its own mailing-date figure).
- **T0-R2-S1 closed** (see 0.md revision_3).

### findings (revision_3)
- No RED.
- O3-1 (observation): "earliest sale date" is now a defined case-level term (compliant notices only). The payment rules also use "the latest earliest sale date stated in any notice" in the field sense. "stated in any notice" and E2's "stated by at least one notice that allows …" fix the field reading, and once E2 holds the two coincide, so there is no second value.
- O-1, O-3, O-5, O-6 and O2-2 stand.

## closing_checklist (revision_3)
- Per-task audit files 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json. revision_1 to revision_3 are preserved, and each revision_3 comparison carries PASS.
- All five extended policies are covered. Scopes {agency_fee, sale_notice_period, redemption_expense_payment} and {surrender_fee, reinstatement_expense_payment} are disjoint and complete. Tool uuid8s are independent and frozen.
- Trees:
  - task 0: n = 2 with 2 value_input edges, root owner=user;
  - task 1: n = 1 with 1 value_input edge, root owner=user;
  - the difficulty graph is acyclic.
- Every computation declares a self-sufficient baseline and 4–5 factors, with ≥2 parameter and 1 method each; per task, ≥1 multi-source and ≥1 cross-difficulty factor. Every factor bears weight and every all-baseline figure differs from gold:
  - task 0: 600 / 15 / 2,259;
  - task 1: 175 / 311.
- Instantiation-stage gates re-run on the final form: the coordinator snapshot of 2026-10-20T06:59:46 shows 7/7 OK.

VERDICT revision_3: task0=PASS task1=PASS charter=CLEAN

## revision_4

## charter_global_frozen (revision_4)
- Trigger: render_r1 STOP (S1, plus a docstring observation), read at audits/render_source/recovery_repossession_and_reinstatement/render_r1.md.
- Gate (worklog tail): `REWORK round 4: gates 7/7 green`.
- Snapshot (snapshot.sh, 2026-10-20T09:32:06): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Views: r4/0.json c009bb69…6769 and r4/1.json ede6aa4e…0eed, both identical to r3.
- Source hashes: `recovery.extended.yaml` a982c53cdbf7c331fa4969cdadc74d16c528f668aa945d0799ca0fcf116d3f2a; `task_tools.py` 1561879292450f042b227d058364897903a96119ebee2f43dc41d6b7ccbc7a2c. Both changed, so the edited sections are re-derived below and the rest is re-verified by script.
- Claims: rework_claims_r4.md.

### re-derived checks (revision_4)
- **S1 closed.** The storage sentence (overwrite[3].replaced_by = rule sentence 4) in both payment policies now reads, in the redemption policy: "Storage that the borrower's own redemption expense payment covers is charged as this rule sets out, and storage that the borrower's own reinstatement expense payment covers is charged by its own reinstatement expense payment rule; storage posted on release or sale … at storage_fee_per_day_usd …". The reinstatement policy carries the mirror. Each sentence:
  - names its own scope and the sibling by name (XF 20);
  - no longer lists any factor and no longer defers its own storage elsewhere;
  - is verbatim between the rule and replaced_by;
  - is quoted by no compute_basis.
- **Docstring item closed.** Neither payment docstring claims a certified channel any more. The bodies are unchanged; signatures and uuid8s are unchanged; no tool validates anything.
- **Regression sweep (scripted).**
  - Every compute_basis, prerequisite source, superseded_clause and replaced_by is still verbatim.
  - Compute is unchanged: 604.00 / 45 / 1,897.00 / 101.00 / 297.00 recomputed on both worlds, equal to GT with every sensitivity equal.
  - Prerequisite graph and sentences: unchanged.
  - Factor ladders: unchanged.
  - Worlds: unchanged.
- **Class sweep: rule/replaced_by sentences naming other factors' quantities.** I tested each factor's own rule sentence (its compute_basis for `decides`) against the business terms of every other factor in the same policy, and every rule and replaced_by sentence for multi-factor inventories. No inventory remains. Two single-mention members remain; see CG4-N1.
- **Class sweep: docstrings claiming effects the body lacks.**
  - Every effect stated after "One call records …" is performed by the body. That includes the notice's "certified mail with return receipt", which the body records as delivery_method.
  - The payment docstrings' "from their own funds" and the reinstatement docstring's "getting their repossessed vehicle back" describe who pays and why. They claim no recorded effect and the body does not contradict them. Same non-blocking kind as the renderer's channel observation, so they are recorded as O4-1, not RED.

### findings (revision_4)
**CG4-N1 SOURCE-POLICY RED (XF 6 / XF 31 class: a factor's own rule sentence names another factor's quantity).**
- Members, exhaustive over all five policies:
  - (a) recovery_ext_agency_fee rule sentence 5, the compute_basis of `fee_value_reduction`, owned by book_value_reduction: "the value reduction is the amount by which the collateral class's involuntary_repossession_fee_usd, **taken before any state limit**, exceeds low_value_fee_pct percent of that book value …". It names the quantity decided by state_fee_ceiling.
  - (b) recovery_ext_surrender_fee rule sentence 5, the compute_basis of `surrender_value_reduction`, owned by surrender_value_basis: "the amount by which the collateral class's voluntary_surrender_fee_usd, **taken before any state limit**, exceeds surrender_low_value_fee_pct percent …". It names the quantity decided by surrender_state_ceiling.
- Consequence: like S1, each sentence has no legal home in a lossless render.
  - The factor document for the value reduction must carry the sentence verbatim, but a factor document may not name or describe another factor (XF 31).
  - The hub and the computation document cannot carry factor variation.
  - Compute is unaffected: the reduction reads `P(...)`, not `fee_state_limit`. No scored value moves on either task world, since both sit on the taper tier.
- Relation to previous revisions: this wording is the CG-S3 closure (revision_2), which I accepted in revisions 2 and 3, and render_r1's scan did not flag it. It falls inside the class the coordinator named for this round ("sentences … naming factor quantities"), so it is reported now. CG-S3's requirement, that the low-value tier compares the unlimited class fee, remains.

Observations:
- O4-1 (docstrings, see above).
- O-1, O-3, O-5, O-6, O2-2 and O3-1 stand.

## closing_checklist (revision_4)
- Task files, scopes, trees, factors and gates are as in revision_3's checklist, re-verified on the r4 hashes. The gates are the round-4 snapshot, 7/7 OK.
- Open: CG4-N1 (charter-wide; no task-level consequence).

VERDICT revision_4: task0=PASS task1=PASS charter=CG4-N1

## revision_5

## charter_global_frozen (revision_5)
- Gate (worklog tail): `REWORK round 5: gates 7/7 green`.
- Snapshot (snapshot.sh, 2026-10-20T10:10:34): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Views: r5/0.json c009bb69…6769 and r5/1.json ede6aa4e…0eed, both unchanged since r3.
- Source hashes:
  - `recovery.extended.yaml` a3e3835d2924e4e86b0a9824dbbdff989c81fbd42e77b9ed30e20a3e1bc1497d (changed);
  - `task_tools.py` 1561879292450f042b227d058364897903a96119ebee2f43dc41d6b7ccbc7a2c (unchanged since r4, so the tool sections carry forward from revision_4).
- Claims: rework_claims_r5.md.

### re-derived checks (revision_5)
- **CG4-N1 closed.**
  - (a) Agency rule sentence 5 now reads "the value reduction is the amount by which the standard agency recovery fee exceeds low_value_fee_pct percent of that book value …". The ladder low tier reads "the excess of the standard agency recovery fee over low_value_fee_pct percent of the book value, floored at zero".
  - (b) The surrender policy mirrors this with "the standard voluntary surrender fee".
  - Both terms are the quantity each policy's baseline sentence defines ("The standard … fee is the collateral class's …_fee_usd"), so the comparison base stays the unlimited class fee and CG-S3 does not reopen. The state-limit sentence speaks of "the class fee", and the assembly sentence subtracts from "the limited fee".
  - Compute is unchanged (`P(...)`).
- **Whole-class sweep, exhaustive (scripted).** For every factor of all five policies, I took the compute_basis of every one of its bindings plus its ladder `when` and `method`/`value` text, and searched it for the business terms and parameter names of every other factor in the same policy (state limit / limited to; value reduction / book value; keyless / key_replacement; weekend / Saturday / Sunday; drop-off / after-hours / staffed; timing credit / opened_date; business-day / extended_notice / base sale period; rate_cap / service; reissue; late-mailing; certified_funds / returned; day rate / rate_states; grace; storage clock / impound).
  - **0 hits.**
  - The generic assembly sentences are unchanged and name no factor quantity.
  - The S1 storage sentences stay as in revision_4.
- **Regression.**
  - Every compute_basis, replaced_by and baseline sentence is verbatim in its rule.
  - Figures are recomputed on both worlds: 604.00 / 45 / 0.00 / 1,897.00 and 101.00 / 297.00, equal to GT, with every factor sensitivity equal.
  - Worlds, trees, prerequisite sentences and ladders are unchanged.
  - No task JSON carries the retired phrase.

### findings (revision_5)
- No RED.
- O5-1 (observation): "the standard agency recovery fee" and "the standard voluntary surrender fee" depend on the baseline sentence's definition to mean the pre-limit class fee. The limit sentence's own wording ("the class fee is limited to …") and the assembly's "limited fee" keep a single reading.
- O-1, O-3, O-5, O-6, O2-2, O3-1 and O4-1 stand.

## closing_checklist (revision_5)
- Revision_3's checklist holds on the r5 hashes: one-to-one task files; disjoint, complete scopes; trees of n = 2 and n = 1 with value_input edges and user-owned roots; an acyclic graph; every factor bearing weight against an honest baseline; methods passing all pairs; multi-source and cross-difficulty factors present.
- Gates: round-5 snapshot, 7/7 OK.

VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN

## revision_6

## charter_global_frozen (revision_6)
- Seed-only round, triggered by KB re-judge S1 (`audits/policy_kb/recovery_repossession_and_reinstatement/_difficulty.md`).
- Gate (worklog tail): `REWORK round 6: gates 7/7 green`.
- Snapshot (snapshot.sh, 2026-10-21T00:54:12): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Views: r6/0.json 2b3f6fc9fa922ba6245dd97b04cf9692872ff5507f46626b2cc450fd226ceae0 and r6/1.json f42d1ffc381e05f63c5c6af639ab0d4f30ed7b39533ea487b3946c2106c79dda.
- Source hashes: `recovery.extended.yaml` a3e3835d2924e4e86b0a9824dbbdff989c81fbd42e77b9ed30e20a3e1bc1497d and `task_tools.py` 1561879292450f042b227d058364897903a96119ebee2f43dc41d6b7ccbc7a2c, both byte-identical to revision_5. All charter-global sections are therefore carried forward from revision_5 by reference, with these two hashes as grounds.
- Claims: rework_claims_r6.md.

### seed verification (revision_6)
- Every changed row (diff r5 → r6) was re-priced independently from the published contract docs and the Tier 5 Rebuild terms. All match; the detail is in 0.md / 1.md revision_6.
  - Task 0: 6 late charges, 2 returned fees, 3 fee settlements and their payment amounts, fees_due, 2 cure notices, the 2025 notice.
  - Task 1: 2 late charges, 1 returned fee, 1 settlement, fees_due, 1 notice.
- Unchanged rows still reconcile: principal balances, certified-funds status from return counts, the 2025 recovery fee and settlement, the current cases.
- Dependent recovery rows follow the frozen charter:
  - base right-to-cure stated amount (installments past due plus fees due on the mailing date);
  - the r3 mailing-date stated-amount formula;
  - sale periods unchanged.
- Scored values are unchanged (604.00 / 45 / 0.00 / 1,897.00; 101.00 / 297.00), as are every sensitivity and every edge-skip figure. No scored computation reads a contract fee amount.

### findings (revision_6)
- No RED.
- KB S1 is closed in both worlds.
- KB S2 (no CPI tracking record) stands as the coordinator-accepted residue.
- The observations of earlier revisions stand.

## closing_checklist (revision_6)
- Revision_5's checklist holds on unchanged charter and tool hashes and the round-6 worlds.
- Gates: round-6 snapshot, 7/7 OK.

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN
