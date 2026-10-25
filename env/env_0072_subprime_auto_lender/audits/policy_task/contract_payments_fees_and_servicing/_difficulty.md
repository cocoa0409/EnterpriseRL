# Policy-task audit — contract_payments_fees_and_servicing / charter-global

## revision_1

## charter_global_frozen
- Frozen 2026-10-19 (session clock), auditor: independent policy-task auditor (not the instantiator). Written before any task GT was revealed; nothing in this section derives from a revealed GT.
- Source hashes (verified by sha256sum, equal to the brief): `contract.extended.yaml` 6ec54ccc856252f31f6bb366d2cc51009eec6090ba28dc28af662af65a149992; `task_tools.py` 5078f93b171fc5fcaeab332979e180b51afe00196a090c627b037905b3b9a8f7. Masked views r1: 0.json 6f0fb643…cf168, 1.json 973fe0c4…2eb (match the brief).
- Read: blueprint/{blueprint.yaml, db_schema.json, products/contract.yaml, products/cpi.yaml, products/recovery.yaml}, the extended charter, task_tools.py, the masked views (frozen_time, user_scenario, initial_state only), audits/render_source/XF_recipe.md, and the gate DSL implementation `skills/erl-task-instantiate/scripts/check_compute.py` (for MONTHS/within_months/LATEST/CFIELD semantics). Masked and unread: tasks/*.json, plan.md, worklog.md, every evaluation_criteria / computations / charter_scope / required_documents / design_rationale / solvability_contract / prerequisite_closure field. No other scenario and no sibling difficulty was read.
- Entry conditions: gate snapshot supplied in the brief (all seven gates OK, replay in --check mode); masked views and hashes supplied. Entry conditions met.
- Base copy: the base section of the extended charter is dict-equal to blueprint/products/contract.yaml on every top-level key (category … policies).
- Scratch: /tmp/audit_contract_0072/ (notes.md, scripts/derive.py — evaluates every compute with the gate's own DSL on the masked worlds).

### policy_conflict_scan
Six extended policies:

| id | target_tool (owner) | computes | prerequisite |
|---|---|---|---|
| contract_ext_delinquency_late_charge (LC) | assess_late_charge_1a8e6313 (agent) | amount_usd | [] |
| contract_ext_deferral_agreement_months (DM) | sign_extension_agreement_772d986b (user) | requested_extension_months | [] |
| contract_ext_hardship_extension_charge (HF) | grant_hardship_extension_883d335d (agent) | extension_fee_usd | DM value_input; LC value_input |
| contract_ext_returned_item_fee (RPF) | assess_returned_payment_fee_c98c0726 (agent) | amount_usd | [] |
| contract_ext_payoff_statement_amount (STMT) | issue_payoff_quote_f4f38627 (agent) | quoted_payoff_usd | RPF value_input |
| contract_ext_borrower_payoff_amount (PAY) | authorize_payoff_payment_7f0b790b (user) | amount_usd | STMT state_gate; RPF value_input |

- Overlapping subjects: DM and HF both list subject contract_extension_granted (different computes and tools — no binding clash; see observation O-12). LC and RPF both write contract_fee_assessed with different fee_type; no overlap in computes.
- Triggers: every event the six tools write (contract_fee_assessed, contract_extension_granted, contract_payoff_quoted, contract_payment_posted with payment_type payoff) carries only in-category triggers (contract_servicing_update, contract_fee_paid, contract_paid_off -> contract_lien_released); the recovery triggers of contract_payment_posted fire only for reinstatement/redemption. XF E-26 clean.
- Eligibility/time anchors: LC inherits active status, grace, one-per-installment; DM/HF inherit contract_extension's active status, recovery-case bar, signed agreement, signature window, min installments paid, dpd band and 180/120-day spacing; STMT inherits quote status; PAY inherits payment status, payoff fee exemption, certified-funds restriction. No extended rule contradicts these deontic gates (extended allowances are only stricter).
- Cross-category reads: DM reads cpi (cpi_coverages.status, cpi_activities notice_type); HF and STMT read recovery_cases (status, recall_reason, closed_date) through CFIELD. Read boundaries respected (read-only).
- Scope partition (inferred from the prerequisite graph; charter_scope is masked): two components {LC, DM, HF} and {RPF, STMT, PAY}; pairwise disjoint and jointly covering all six policies. Re-checked against charter_scope after reveal (see each task file).
- Conflicts found: CW-3 (PAY framing clause vs in-force base clearance clause), CW-1/CW-2 (term definitions with two readings). Listed under findings.

### rule_compute_equivalence
Mechanical sweep (script over the charter): every compute binding has a compute_basis entry, no extra entries, and every compute_basis quote, every overwrite.replaced_by, every prerequisite.policy_source and every baseline.rule is a verbatim substring of its own rule (XF C-16 clean). Every overwrite.superseded_clause is verbatim in the base rule it names.

Per policy, sweep back rule -> compute:
- LC: rate schedule, amount basis (final installment MN; partial credit tier gated on `latest_payment_date <= next_due_date`), 12-month counts (within_months=12 = rolling, `0 <= MONTHS(d, NOW) < 12`), combined reduction, cap after reduction, single RND at end — all implemented as worded. Absent-record: no posted payment -> partial tier false -> scheduled installment (matches "while the latest posted payment … is dated on or before").
- DM: the three tier limits, six allowances, MX(0, MN(...)) — implemented; the "request date" of the delinquency and spacing allowances is implemented as NOW (CW-1). "whole calendar months" windows implemented as rolling MONTHS windows (CW-2). Absent-record: no cpi record -> 1 ("every other case"); no earlier extension -> cap; no payment -> 0. "when that smallest figure is zero no agreement is offered" is an act/refuse statement (no compute counterpart needed).
- HF: deferred installments from LATEST signed request (`or 0`), schedule, charged installments (fractional tier), late-charge credit (full / capped / none), collections stage, review charge, recovery review (CFIELD), waiver multiplier, MX(0,·) then RND — implemented. CFIELD first-match vs "a repossession case … closed" (CW-7).
- RPF: schedule fee, subsequent-return count (four fee-bearing reasons enumerated — equal to fee_bearing_return_reasons in every tier), reason charge, offset, late-return lag, restriction count incl. this one, MX(0,·) then RND — implemented. The monthly-cap sentence is a write/no-write gate with no compute counterpart (O-14). Same-day-tie reads (CW-7).
- STMT: interest from latest posted payment (returned -> reversed interest in place of unpaid interest), window/cushion/estimate/referral/repeat/anchor, MX(0, days) floor, RND points as worded — implemented; "in the last whole calendar month before the quote date" implemented as within_months=1 (CW-2).
- PAY: interest same shape as STMT, five holds summed, RND as worded — implemented; "in the last autopay_lookback_months whole calendar months" as within_months=3 (CW-2).
- Rounding: every "rounded half-up … once at the end" matches the single outer RND; STMT/PAY round the new interest separately as worded (XF C-14 clean; RND is Python round — no .xx5 tie arises in either world, O-17).
- Edge probes (XF C-11/12) run on scratch copies: zero/negative lags (RPF same-day return -> 0; PAY return 0 days -> full 4-day window), DM current account (`request_days_late <= 0` -> cap), HF zero-month agreement -> one charge, absent recovery/cpi rows -> fall-through. Mismatches only at first-match/tie reads (CW-7).

### action_binding_and_uuids
- Six distinct (target_tool, computes) pairs, each claimed by exactly one policy.
- Docstrings: no ordering word (grep for before/after/first/then/prior/once/until — only "later by that many months", a date shift), no other tool named, no example values (formats only), every claimed effect present in the body (late charge dated today; RPF dated on the return's txn_date; grant moves both dates on the same due day, books or waives the fee, marks the agreement applied; payoff zeroes balances, records the fee settlement, closes paid_off/borrower_payoff). No tool refuses, errors or hints on an unresolved prerequisite (grant reads months from whatever agreement id is passed; authorize does not look for a quote). XF F-28 clean.
- uuid8s 1a8e6313, 772d986b, 883d335d, c98c0726, f4f38627, 7f0b790b: no shared prefix/suffix, not sequential, one per tool. No factor id is a substring of any tool name (XF A-7 clean).

### prerequisite_graph
- Every policy fills `prerequisite`; every `problem` names an extended policy of this file; no self-edge; graph HF->{DM, LC}, STMT->RPF, PAY->{STMT, RPF} is acyclic.
- Every policy_source is verbatim in the blocked policy's own rule (sweep above). All edges form `state`; no fallback_reason present, none needed.
- kind/gate: value_input gates deferred_installments, oldest_installment_late_charge (HF), statement_fees (STMT), payoff_fees (PAY) are real compute bindings; resolved_by is the depended-on target_tool in every case and its write moves the binding (DM sign -> requested_extension_months read by LATEST signed; LC -> SUM late charges on next_due_date; RPF -> fees_due_usd). PAY's state_gate names `contract_servicing_events.quoted_payoff_usd` while its condition tests `effective_date` = posting date (O-15, observation).
- No authoring-viewpoint wording in any prerequisite field.

### prerequisite_sentences
| edge | sentence (blocked rule) | connective / form | one write brings it about | reading |
|---|---|---|---|---|
| HF<-DM | "The hardship extension fee is fixed only after the contract's records carry an extension agreement the borrower has signed, naming the installments it defers." | only after / state | sign_extension_agreement (only tool that sets request_status signed) | words broader than condition — CW-8 |
| HF<-LC | "The hardship extension fee is not fixed until the contract's oldest unpaid installment carries its late charge whenever that installment's late-charge grace period has ended." | not until / state | assess_late_charge (only writer of fee_type late_charge) | single reading: LC rule "fixes the late charge booked on the oldest unpaid installment … once … grace period has ended" |
| STMT<-RPF | "A payoff statement's figure is fixed only after each returned payment on the contract that owes a returned-payment fee carries it." | only after / state | assess_returned_payment_fee | single reading via RPF rule + base cap clause |
| PAY<-STMT | "A payoff payment is taken only after the contract's records carry a payoff statement quoted on the posting date." | only after / state | issue_payoff_quote (only writer of contract_payoff_quoted) | single reading |
| PAY<-RPF | "The payoff amount is not fixed until each returned payment on the contract that owes a returned-payment fee carries it." | not until / state | assess_returned_payment_fee | single reading |

No sentence names a tool, policy id, snake_case token or row id; no rule carries a second wording of an edge; no depended-on rule restates the sentence. Base sentence "An extension is applied only under an extension agreement … that the borrower has signed" states an order but the HF rule carries its own sentence (observation only). No undeclared cross-problem order found in any extended rule.

### override_declarations
Sentence-by-sentence against each base_policy_refs entry:
- LC vs contract_evt_late_charge: s1 active, s2 grace, s3 counting, s4 unpaid/16 CFR 444.4, s5 one per installment, s7 deferred installments — followed/inherited; s6 (amount, round-then-cap) — retired by the declared overwrite, replaced_by restates installment_due_date recording. vs contract_evt_payment_channel_fees / contract_evt_returned_payment — no sentence governs the late-charge amount; no conflict.
- DM vs contract_extension: s1–s6, s8–s9 inherited (allowances are stricter, never looser); s7 (per-request/12m/life caps) — retired, replaced_by restates the three tier limits; s10–s11 not this quantity.
- HF vs contract_extension: s11 (fee) — retired; rule restates the one-charge baseline and the first-extension waiver; s10 (date moves) restated in the rule; others inherited. Dangling "the first-extension waiver above" in replaced_by (O-11).
- RPF vs contract_evt_returned_payment: s3 retired with cap and dating restated; s4 (unauthorized_debit/bank_error, fee-settlement-only payments) inherited via scope "return_reason is in fee_bearing_return_reasons".
- STMT vs contract_payoff_and_lien_release: s2 first half (figure via contract_msr_accrued_interest, valid days) retired; tail "a payoff received after the good-through date …" stays in force; other sentences inherited.
- PAY vs contract_evt_payment_application: s5 (payoff equals principal+accrued interest+fees) retired; s2 (general accrual from the latest non-returned payment) remains in force while PAY's own interest sentence anchors on the latest posted payment and swaps in the reversed interest — equal in T1's world (192.97 both ways) and differing only by a split rounding point or with two consecutive returns (O-9). vs contract_evt_payment_channel_fees: payoff fee exemption and certified-funds gate inherited.
- Not in PAY's refs but in force: contract_payoff_and_lien_release s6 "Payoff funds become final payoff_funds_clearance_business_days after posting for the paying channel …" — contradicted by PAY's framing clause (CW-3).
- Anonymous-intermediate / 0-1 multiplier / dropped-branch sweep: HF's waiver multiplier is the declared base waiver; no dropped base branch found.

### factor_ladders
Counts (declared): LC 4 (3 parameter, 1 method); DM 6 (5 p, 1 m; insured_collateral cross_difficulty cpi); HF 6 (4 p, 2 m; recovery_history_review cross_difficulty recovery); RPF 6 (5 p, 1 m); STMT 6 (4 p, 2 m; referral_history_shortening cross_difficulty recovery); PAY 5 (4 p, 1 m). Every ladder has >= 3 tiers stated in full in the rule and implemented in the `decides` binding; every fall-through equals the factor's baseline binding, and every factor baseline equals what baseline.rule gives for that input. Binding sets are disjoint within each policy; no `decides` is `result`; no factor reads another factor's binding (transitive check: shared reads per_request_cap, deferred_life, deferred_installments, scheduled_installment, latest_return_date, returned_payment_id are plain bindings) — XF A-1/A-2/A-5/A-6 clean except assembly wording (CW-4).

Tier disjointness over each policy's own scope (XF B-9): all ladders pairwise disjoint and gap-free as stated. Dead/collapsed tiers by variant: DM top tier = fall-through for Tier 6/5 (extension_max_months_per_request 1) on all six allowances (O-1); DM delinquency tier 2 unreachable for Tiers 4–6 (min dpd 1) (O-2); RPF restriction fall-through unreachable for Tiers 4–6 (count 2, this return always counted) (O-3).

Multi-source (every non-fall-through tier a conjunction/disjunction over distinct records): HF charge_units (tier 1: signed request x contract past-due x partial credit; tier 2: request x NOT contract-tier-1 condition) qualifies; DM insured_collateral tier 1 (cpi_coverages x cpi_activities) qualifies but its tier 2 is a disjunction on one record; LC charge_basis tier 2 (contract x latest payment) qualifies but tier 1 is single-record; RPF failed_payment_offset tier 1 (return row x agent-fee row); PAY / STMT: none fully multi-source (STMT referral tier 2 reads two recovery conditions on case records; PAY returned_channel_hold tier 1 latest return date x channel — same row). Task-level coverage is settled per task.

Method-shape all-pairs tables (XF B-8; distinguishing input given for every pair):

| policy.factor | tiers | pair | distinguishing input | verdict |
|---|---|---|---|---|
| LC.charge_basis | T1 MN(sched, principal+unpaid) / T2 sched − partial / T3 sched | T1–T2 | sched 599.25, principal+unpaid 400, partial 250 -> 400 vs 349.25 | pass (different inputs/op) |
| | | T1–T3 | principal+unpaid 400 -> 400 vs 599.25 | pass (adds MN) |
| | | T2–T3 | partial 250 -> 349.25 vs 599.25 | pass (adds input) |
| DM.deferral_scope | T1 MONTHS(next_due, request)+2 / T2 P(per_request) / T3 1 | T1–T2 | 40 dpd, cap 2 -> 3 vs 2 | pass (data-derived count) |
| | | T1–T3 | 12 dpd -> 2 vs 1 | pass |
| | | T2–T3 | Tier 4 cap 2 -> 2 vs 1 | pass by recipe (tariff parameter); collapses for Tier 5/6 (O-1) |
| HF.charge_units | T1 N − partial/sched / T2 N / T3 1 | T1–T2 | N 2, partial 250, sched 599.25 -> 1.583 vs 2 | pass |
| | | T2–T3 | N 2 -> 2 vs 1 | pass (reads N) |
| | | T1–T3 | -> 1.583 vs 1 | pass |
| HF.late_charge_credit_rule | T1 x / T2 MN(x, 5) / T3 0 | T1–T2 | x 7.68 -> 7.68 vs 5.00 | pass (adds cap) |
| | | T1–T3, T2–T3 | x 7.68 -> 7.68 / 5.00 vs 0 | pass (reads x; nothing-tier not 0 elsewhere) |
| RPF.failed_payment_offset_rule | T1 agent fee on returned payment / T2 K 5 / T3 0 | T1–T2 | agent fee 7.95 -> 7.95 vs 5 | pass (reads ledger) |
| | | T1–T3 | 7.95 vs 0 | pass |
| | | T2–T3 | autopay return -> 5 vs 0 | pass only under the recipe's nothing-tier clause (constant vs nothing; O-6) |
| STMT.late_estimate_basis | T1 MN(cap, pct·MN(sched, principal)) / T2 MN(cap, pct·sched) / T3 0 | T1–T2 | principal 300, sched 524.47 -> 15.00 vs 25.00 | pass (adds MN) |
| | | T2–T3, T1–T3 | -> 25 vs 0 | pass |
| STMT.business_day_anchor | Fri K 3 / Sat K 2 / Sun K 1 / Mon–Thu 0 | Fri–Sat, Fri–Sun, Sat–Sun | any quote day: 3 vs 2 vs 1 constants | FAIL — same shape (add a constant day count), only the number differs (CW-5) |
| PAY.recent_return_window | T1 4 − days_since / T2 K 1 / T3 0 | T1–T2 | 2 days since -> 2 vs 1 | pass (data-derived) |
| | | T1–T3 | 2 vs 0 | pass |
| | | T2–T3 | 10 days since -> 1 vs 0 | pass only under the nothing-tier clause (O-6) |

Parameter labels: every `parameter` factor's tiers substitute a number into one formula (honest).

Realism (XF B-10) — every factor, every tier:
- LC: state late-charge schedule (company schedule, worded as such) — real; final-installment and unpaid-portion bases — real; first-delinquency relief — real practice; autopay relief — unusual company schedule (O-5).
- DM: insurance in force, seasoning, remaining term, past-due scope, spacing, recent payment activity — all real deferment-eligibility factors (partial-credit conjunct of the delinquency tier, O-5).
- HF: per-installment state deferral charge — real; charged installments pro-rated by partial credit — defensible as charging on the deferred amount (O-5); late-charge credit on deferment — real; collections handling, cumulative-deferral review, repossession-history review — plausible company schedules (O-5).
- RPF: state tiered schedule, escalating repeat fee, reason surcharge, convenience-fee offset, restriction review — plausible; **late_return_handling — unreal (CW-6)**; stacked total above common state NSF caps (O-5).
- STMT: delinquency window, funds cushion (shorter for certified-funds-only contracts — realistic), late-charge estimate, referral-history shortening, weekend anchor — real/plausible; **repeat_statement_shortening — unreal (CW-6)**.
- PAY: returned-channel, weekend-receipt, recent-return, delinquency holds — plausible risk/funds holds; autopay-history hold — weak (O-5).

### findings
Charter-wide REDs (each class listed exhaustively; the task each bears on is named so its file carries the demonstration):

**CW-1 SOURCE-POLICY — "request date" has two readings in DM (bears on task 0).**
Symptom: DM's delinquency and spacing allowances are keyed to "the request date"; compute uses NOW (`request_days_late: DAYS(F('next_due_date'), NOW)`, `MONTHS(latest_extension_date, NOW)`), while the records carry the borrower's request as a contract_service_requests row with its own created_at, and the inherited base clause calls that row "the request" ("The extension agreement must be signed no later than extension_signature_valid_days after the request was created"). Members (all in DM's rule): (1) "when the request date is more than late_charge_grace_days days after next_due_date …", (2) "the installments past due on the request date …", (3) "from next_due_date to the request date plus two", (4) "when next_due_date is on or after the request date", (5) spacing "… whole calendar months before the request date" (twice). No other policy uses "request date". Consequence demonstrated in 0.md.

**CW-2 SOURCE-POLICY — "whole calendar months" window wording vs rolling MONTHS windows (XF C-13) (bears on task 1; weaker member on task 0).**
Compute counts rows with `0 <= MONTHS(d, NOW) < N` (rolling, anniversary-day) while the rule words read naturally as complete calendar months. Members: (a) DM "payments posted on the contract in the last recent_activity_months whole calendar months"; (b) DM spacing "at least spacing_long_months / fewer than spacing_short_months whole calendar months before the request date"; (c) HF "within the last recovery_window_months whole calendar months" (x2); (d) STMT "had a late charge assessed in the last recent_late_months whole calendar months"; (e) STMT "within the last reinstated_lookback_months / cured_lookback_months whole calendar months"; (f) STMT "in the last whole calendar month before the quote date"; (g) PAY "in the last autopay_lookback_months whole calendar months". Consequences in task 1 for (f) and (g); task 0 (a), (c) same tier under both readings, (b) differs only under the complete-months reading (see 0.md).

**CW-3 SOURCE-POLICY — PAY framing clauses contradict in-force base text and PAY's own values (XF C-17, D-21) (bears on task 1).**
(i) PAY rule and replaced_by: "payoff interest runs through the posting date plus those hold days, because the contract is held open until the payoff funds are final"; in-force base contract_payoff_and_lien_release: "Payoff funds become final payoff_funds_clearance_business_days after posting for the paying channel (business days are Monday to Friday excluding federal holidays)". (ii) PAY weekend hold: "a payoff posted on a Friday adds friday_hold_days [2] and one posted on a Saturday adds saturday_hold_days [1] … because funds received then are credited on the following business day" — the following business day is 3 days after a Friday and 2 after a Saturday (STMT's own anchor uses 3/2 for the same Friday/Saturday->Monday shift). Both clauses assert a fact the charter's numbers contradict.

**CW-4 SOURCE-POLICY — assembly sentences name factor quantities (XF A-3).**
Members: HF "the per-installment charge multiplied by the charged installments, plus every handling charge, less the credit" (names deferral_charge_schedule, charge_units, late_charge_credit_rule quantities); RPF "the schedule fee plus every charge they add, less the offset they subtract" (return_fee_schedule, failed_payment_offset_rule); STMT "plus the statement window, plus the cushion days and the business-day anchor days, less the shortening days … adds any late-charge estimate" (all six factors); DM "the smallest of the three tier limits and the six allowances below" (enumerates the factor set). Not members: LC ("the reductions … the late-charge rate … the amount it applies to" — generic/baseline quantities), PAY ("Where the holds below apply, their days are added together"). Bears on task 0 (HF, DM) and task 1 (RPF, STMT).

**CW-5 SOURCE-FACTOR — STMT.business_day_anchor labelled `method` with constant tiers (XF B-8) (bears on task 1).** Table above: Fri/Sat/Sun tiers are 3/2/1 days added to one sum — a number substituted into one formula, i.e. a parameter.

**CW-6 SOURCE-FACTOR — unreal ladders (XF B-10) (bears on task 1).**
(i) RPF.late_return_handling: the returned-payment fee rises with the days between the payment's posting and the bank's return (+5 over 5 days, +10 over 10). Return latency is set by the banks' return windows, not the borrower, and no auto lender prices its returned-payment fee on it. (ii) STMT.repeat_statement_shortening: a payoff statement's good-through date is cut by 1 or 3 days because the borrower already asked for a statement in the last month; good-through dates reflect per-diem/transit, and no lender shortens a payoff quote's validity because an earlier quote was requested.

**CW-7 SOURCE-POLICY — first-match and same-day-tie reads diverge from the rule words (XF C-12, E-24) (no consequence on either current world).**
(i) CFIELD first match on recovery_cases: HF reinstated_closed, cured_closed; STMT reinstated_closed_on, cured_closed_on. Rule: "when a repossession case on the contract closed as reinstated / recalled … within the last N … months". Recovery charter allows several cases per contract ("one case per default episode"; "A new case on the same contract opens only after the earlier case has closed"). Situation: case A recalled account_brought_current closed 2022-03-01 stored first, case B recalled account_brought_current closed 2026-02-04 -> rule: B qualifies (cut/charge applies); compute: CFIELD returns A's date -> MONTHS >= window -> 0. (ii) LATEST same-day ties (strict `>`; first stored row wins) where the rule says "the latest" without a tie rule: RPF returned_payment_id, returned_amount, return_reason_value, returned_channel, return_date ("the contract's latest returned payment" — two returns posted the same day, e.g. an autopay and a one-time draft returned together, give no unique row and the compute can price only one of the two fees the STMT/PAY prerequisite sentences require); STMT/PAY latest_payment_id ("the latest posted payment" — two payments the same day, one returned, change latest_payment_returned); PAY latest_return_channel ("came through an ACH channel … was a mailed check" — same-day ACH and check returns).

**CW-8 SOURCE-POLICY — HF<-DM prerequisite sentence broader than its condition (check 6) (bears on task 0).** Sentence: "… only after the contract's records carry an extension agreement the borrower has signed, naming the installments it defers." Condition: "a row of request_type extension with request_status signed …". Any earlier agreement the borrower signed and that was since applied (request_status applied, signed_at set, requested_extension_months > 0) satisfies the sentence's words but not the condition.

**CW-9 SOURCE-TASK (seed legality, XF F-27) — seeded late charges the charter cannot produce (bears on both tasks).** Base contract_evt_late_charge: "At most late_charge_max_per_installment late charge is assessed on one installment due date" (1 in every tier) and "the installment due date is the contract's next_due_date for the oldest unpaid installment". Exhaustive member list: task 0 contract_transactions 455b6c62-20a5-4523-a384-7bf43a144b0c (2024-12-19, 17.98) and dc1fc472-bf88-4cb1-9ff4-c43fc40bbaa8 (2025-01-19, 23.97), both installment_due_date 2024-11-08 which already carries cf24ec62-1e97-4e99-abc4-8ed2ee94cc9e (2024-11-19); task 1 fe8b5e89-bfbb-422f-97e9-5d24e10ed4f9 (2025-12-29, 20.98) and 4e3acf96-65bf-4f80-a32b-f4f274b663a2 (2026-01-29, 23.60), both on 2025-11-18 which already carries 7a75e191-0c83-4370-8028-0ba4f2ec79ca (2025-11-29). In both worlds next_due_date stayed on that installment until the cure payment, so no later installment could have been charged either. Every other seeded row reconciles: principal (amount financed − principal applied + principal returned) equals principal_balance_usd in both worlds, every interest_applied_usd equals actual/365 accrual from the previous non-returned payment, fees_due_usd reconciles, the 2024 extension fee (20.00), the 2026-05-20 returned-payment fee (25.00), the 2026-10-05 quote (8411.70 good through 2026-10-16) and every other late charge reprice exactly under the extended formulas; cpi and recovery rows are producible under their charters (lapse notice -> proof -> compliant clears lapse_date; referral at >= 60 dpd, recall account_brought_current on the cure payment; GA/AL need no cure notice).

Observations (not grounds for rework): O-1 DM ladders collapse for Tier 5/6; O-2 DM delinquency tier 2 dead for Tiers 4–6; O-3 RPF restriction fall-through dead for Tiers 4–6; O-5 softer realism notes (LC autopay relief; LC charge_basis "dated on or before that installment's due date" conjunct; DM partial-credit conjunct; HF fractional charged installments, collections handling, recovery review; RPF reason surcharges and stacked total — 42.05 in task 1 exceeds the $30 returned-check charge common in state law, e.g. Alabama; PAY autopay-history hold and use of the latest return's channel rather than the payoff's channel); O-6 constant-vs-nothing method pairs accepted only via the recipe's nothing-tier clause; O-9 STMT/PAY interest anchor vs base payment_application s2 (declared via retired clauses; equal in task 1); O-10 HF "every handling charge" vs two rules named "review charge" (a reader who excludes them gets a smaller fee; unlikely reading because those rules would then feed nothing); O-11 HF replaced_by "the first-extension waiver above" dangles outside the rule; O-12 DM subject contract_extension_granted while its tool writes the intake row; O-13 baseline.rule of STMT/PAY uses "statement/payoff interest" defined in a separate plain sentence; O-14 RPF monthly cap is a gate with no compute; O-15 PAY state_gate field vs condition field; O-16 STMT late-charge estimate uses a different formula than LC; O-17 RND is Python round vs "half-up" (no tie in either world); O-18 base "Installments deferred by an extension … carry no late charge for the deferred months" vs HF booking the oldest installment's late charge before deferring it (HF's own sentence governs).

## closing_checklist
Written after both reveals (2026-10-20). The difficulty does **not** close in revision_1: both tasks carry REDs.
- Audit files: 0.md, 1.md, _difficulty.md present, one per task; revision_1 is the first revision. Comparison sections: every scored argument, order, tree edge and factor_sensitivity figure equals the blind derivation in both tasks — but under the readings CW-1/CW-2/CW-3 contest, so neither comparison is a PASS.
- Coverage and scope: charter_scope task 0 = {LC, DM, HF} + their three tools; task 1 = {RPF, STMT, PAY} + their three tools — pairwise disjoint, jointly all six extended policies, matching the blind partition. uuid8s independent (see §action_binding_and_uuids).
- Trees: task 0 — 2 prerequisites, 2 value_input, user write (sign), acyclic; task 1 — 2 prerequisites, 2 value_input + 1 state_gate, user write (payoff), acyclic; the difficulty-wide graph is acyclic.
- Factors: counts within bounds in every computation; every factor bears weight on its world against an honest baseline; whole-baseline fall-backs differ from gold (task 0: 25.00/1/30.00; task 1: 25.00/8537.99/8493.11); multi-source and cross-difficulty floors met (task 0: HF.charge_units, cpi + recovery; task 1: RPF.return_fee_schedule, recovery). Open: CW-5 (mislabel), CW-6 (unreal ladders).
- Additional proof-text defect found at reveal: both tasks' solvability_contract.seed_consistency (and task 0's design_rationale gate note) assert the CW-9 duplicate late charges are legal, single-per-installment charges "the day after grace" — false; part of CW-9.
- Instantiation gates not re-run by this auditor (artifacts unchanged; check_traceability excluded by brief).
- Open charter-wide REDs: CW-1, CW-2, CW-3, CW-4, CW-5, CW-6, CW-7, CW-8, CW-9.

VERDICT revision_1: task0=RED task1=RED charter=CW-1,CW-2,CW-3,CW-4,CW-5,CW-6,CW-7,CW-8,CW-9

## revision_2

### charter_global_frozen (revision_2)
- Frozen 2026-10-20, before either task's round-2 GT was read. Gate: worklog tail `REWORK round 2: gates 7/7 green`. Round-2 gate snapshot (coordinator `snapshot.sh contract_payments_fees_and_servicing 2`, 2026-10-20T06:22:41): check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks --check REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK; check_grounding GROUNDING OK; check_cross_fire SCOPE OK. Masked views r2: 0.json c0912b99bfd355918a94e643a3daa3365a3ac7962333c0bc9208cb5ce0c7d227, 1.json 6cc6c8af72ce65b2fa76774998ebc281d4586b09bd7bb04bcd82b830fb4bb65b.
- Source hashes: `contract.extended.yaml` 800247a3d39ac84b39068b66ad238f81144396f671166b94dbf98e21a18ec210 (CHANGED from 6ec54ccc… -> every charter-global section re-derived below); `task_tools.py` 5078f93b… (unchanged -> §action_binding_and_uuids of revision_1 carried forward by reference on that hash).
- Read: the r2 charter (copy at /tmp/audit_contract_0072/r2/charter_r2.yaml), rework_claims_r2.md (item ids only), the r2 masked views, blueprint recovery.yaml (reinstatement_max_per_contract) and cpi.yaml (accepted_verification_sources). Not read before freezing: tasks/*.json, plan.md, worklog.md (only its tail line, as instructed).
- Base copy: still dict-equal to blueprint/products/contract.yaml on every top-level key.

### policy_conflict_scan (revision_2)
Same six policies, tools, computes and prerequisite graph (HF<-{DM, LC}, STMT<-RPF, PAY<-{STMT state_gate, RPF}); triggers unchanged (in-category only). Changed factor sets: RPF late_return_handling -> bank_charge_recovery (+ a plain "State cap" rule); STMT referral_history_shortening -> insurance_lapse_shortening (cpi), repeat_statement_shortening -> remittance_method_days, business_day_anchor relabelled parameter; PAY holds renamed review days, autopay_history_hold -> referral_history_review (recovery). No new conflict among policies; DM's new "signing date" and HF's "effective date" are both the call date (the DM write is the signature; the grant tool sets effective_date today).

### rule_compute_equivalence (revision_2)
Mechanical sweep: every compute binding has a compute_basis, none extra; every compute_basis quote, replaced_by, policy_source and baseline.rule is verbatim in its own rule; every superseded_clause verbatim in its base rule.
- Rolling-window wording vs MONTHS: "later than the same calendar day N months before D (the last day of that month when that day does not exist)" ⟺ `0 <= MONTHS(d, D) < N`, and "on or before the same calendar day N months before D" ⟺ `MONTHS(d, D) >= N` — checked on day-31/Feb-28/Feb-29 cases against the gate's MONTHS (day-adjusted). Holds for DM spacing/activity, HF recovery, STMT window/remittance, PAY referral; "rolling 12 months ending on …" for the 12-month counts.
- DM seasoning "monthly due dates from first_payment_date up to but not including next_due_date" = MONTHS(first_payment_date, next_due_date) and remaining "from next_due_date through maturity_date" = MONTHS+1, exact while the due day is unchanged (a due-date change moving the day below the first-payment day would make them differ — O-19, no member world).
- DM delinquency tier 1 "each monthly due date from next_due_date through the signing date plus the next" = MONTHS(next_due, NOW)+2 ✓.
- RPF: assembly MX(0, …) then MN(state cap) then one RND, as worded ("never below zero and never above the state cap, rounded … once at the end"); bank charge reads the return's date and channel; "when the fee worked out below is zero, no fee is booked" unreachable (minimum 25.00 − 9.95).
- STMT remittance: rule tiers "a payment by mailed check posted … mail_days; when none did but a one-time … payment did, one_time_days; when only recurring autopay drafts or no payments posted in that period, none" — compute's fall-through also covers a period whose only payments are third_party_remittance (not listed in one_time_channels), a case no stated tier covers (N-1). The rule does not say whether a posted payment later returned counts (N-2).
- Same-day tie rules now stated for every "latest" row a factor or plain binding reads by row (RPF latest return; STMT/PAY latest posted payment; PAY latest return); remaining LATEST reads are date-only (LC latest payment date, DM latest extension date) or timestamped (HF signed agreement).

### prerequisite_graph / prerequisite_sentences (revision_2)
Graph unchanged and acyclic; all edges `state`. HF<-DM sentence now "… an extension agreement the borrower has signed and that has not yet been applied, naming the installments it defers", condition "request_status signed (signed, not yet applied)" — words and condition coincide (an applied agreement no longer satisfies it). PAY state_gate now names `contract_servicing_events.effective_date` (matches its condition). Other sentences unchanged (revision_1 table stands).

### override_declarations (revision_2)
Same superseded clauses; replaced_by texts rewritten generically. HF replaced_by now restates the first-extension waiver itself (self-contained). PAY replaced_by no longer mentions funds-final; it defines a payoff good-through date (posting date + review days) with the per diem through it; base contract_payoff_and_lien_release s6 (funds final after clearance days, lien release timing) is no longer contradicted. Base payment_application s2 vs PAY interest anchor: unchanged (O-9; equal again on task 1's world, see 1.md).

### factor_ladders (revision_2)
Counts: LC 4 (3 p, 1 m); DM 6 (5 p, 1 m; cpi); HF 6 (4 p, 2 m; recovery); RPF 6 (5 p, 1 m); STMT 6 (5 p, 1 m; cpi); PAY 5 (4 p, 1 m; recovery). Every ladder >= 3 tiers, stated in the rule, fall-through = baseline binding; no factor reads another's binding (plain shared reads: per_request_cap, deferred_life, deferred_installments, return_date, returned_channel, latest_return_date). No factor id is a substring of a tool name.
- Method all-pairs: LC.charge_basis, DM.deferral_scope, HF.charge_units, HF.late_charge_credit_rule, RPF.failed_payment_offset_rule, PAY.recent_return_window — unchanged tiers, revision_1 table stands; STMT.late_estimate_basis unchanged; STMT.business_day_anchor now `parameter` (constants 3/2/1/0 — honest).
- New ladders, disjointness: RPF bank charge (state × date × channel ACH/check/else) complete; STMT insurance-lapse (placed/lapse status; else notice in 12 months; else) complete; STMT remittance — gap (N-1); PAY weekend 4 tiers complete; PAY referral (reinstated within 24 months; else any cured recall; else) complete; HF recovery same shape, complete.
- Realism (XF B-10), new/changed factors: bank-charge recovery (pass-through of the bank's returned-item charge by company state schedule) — plausible; state cap schedule (FL/LA 40, AL/MS/GA 30, worded as company limits) — realistic; remittance-method days (extra days for mailed payers) — real payoff-letter practice; insurance-lapse shortening (a force-placed premium may be capitalised before the good-through date) — plausible; PAY referral-history review and HF/PAY permanent "any cured recall" tier (no look-back) — weak but in the risk-review family already accepted (O-5).
- XF A-3 assembly sentences: all six generic now ("the rules below may replace … add … take"; "every allowance they set"; "every review day added"); RPF's names only the plain State cap rule, not a factor quantity.
- Framing (XF C-17): "a contract is reinstated at most once" — true (recovery reinstatement_max_per_contract 1 in every tier); weekend/anchor clauses consistent with 3/2/1; "the bank's own charge for the returned item" describes the schedule values (O-20).

### findings (revision_2)
Closure of revision_1 charter-wide REDs (re-checked on the r2 charter):
- CW-1 closed: "request date" gone; "the signing date is the date the borrower signs it", and the DM write is that signature.
- CW-2 closed: every month window restated in the rolling same-calendar-day convention matching MONTHS (members a–g: a, b, c, d, e rewritten; f, g removed with their factors).
- CW-3 closed: funds-final framing removed; weekend days 3/2/1 now match "the following Monday".
- CW-4 closed: assembly sentences generic in HF, RPF, STMT, DM (and PAY).
- CW-5 closed: business_day_anchor relabelled parameter.
- CW-6 closed: late_return_handling and repeat_statement_shortening removed; replacements realistic.
- CW-7 closed: reinstated case unique by charter parameter (CFIELD safe), cured case by EXISTS; tie rules stated for every row-valued latest read.
- CW-8 closed: sentence and condition both exclude applied agreements.
- CW-9: closed on the charter side (seed check per task: both r2 ledgers carry one late charge per installment; see task files).

New charter-wide REDs:
**N-1 SOURCE-POLICY — STMT remittance-method ladder has a gap (XF B-9).** The three stated tiers are (mailed check posted) / (none, but a one_time_channels payment posted) / ("only recurring autopay drafts or no payments posted"). A period whose posted payments include a third_party_remittance payment (insurer, auction or other third party — a payment_channel of contract_payment_posted the tools offer) and no check or one-time payment falls in no stated tier; compute returns 0 days. Member: STMT remittance_method_days (only one). No member world in either task.
**N-2 SOURCE-POLICY — STMT remittance-method days silent on returned payments (XF C-11/C-12).** "when a payment by mailed check … posted on the contract in the rolling remittance_lookback_months months …; when none did but a one-time draft, card or transfer payment … did" — unlike every other payment count in the charter (LC autopay count "returned or not", LC latest payment "returned or not", DM activity "returned or not"), this rule does not say whether a payment later returned counts; compute counts it. Members: recent_check_payments, recent_one_time_payments (both in STMT). Consequence on task 1 (see 1.md).

Observations added: O-19 (DM seasoning/remaining under a due-day change), O-20 (bank-charge framing), O-21 (STMT on task 1: the five day factors net to the baseline window — see 1.md), O-22 (two same-day good-through dates in task 1: statement vs payoff review days). Revision_1 observations O-1…O-18 otherwise stand except O-11, O-15 (fixed) and the parts of O-5 about removed factors.

## closing_checklist (revision_2)
Written after both round-2 reveals (2026-10-20 06:30 UTC). The difficulty does **not** close: task 1 carries N-2.
- Files: 0.md, 1.md, _difficulty.md each carry revision_1 untouched and revision_2 appended; revision_2 derivations frozen before the reveal.
- Comparisons: every scored argument, order, edge and factor_sensitivity figure equals the r2 blind derivation in both tasks; task 0 comparison PASS; task 1 RED on N-2 only.
- Scope: task 0 {LC, DM, HF}, task 1 {RPF, STMT, PAY} — disjoint, jointly complete; tool module unchanged (uuid8s as revision_1).
- Trees: both 2 prerequisites, 2 value_input, one user write, acyclic; difficulty graph acyclic.
- Factors: counts within bounds; all bear weight; fall-backs differ (task 0: 25.00 / 1 / 30.00; task 1: 25.00 / 8,493.41 / 8,448.53); multi-source (HF.charge_units; RPF.return_fee_schedule) and cross-difficulty (cpi + recovery in task 0; cpi + recovery in task 1) seeded and producible.
- XF_recipe sweep on the r2 charter: A 1–7 clean; B 8 clean (business_day_anchor now parameter), B 9 one member (N-1), B 10 clean (removed unreal ladders; replacements plausible); C 11–12 one member (N-2), C 13–17 clean; D 18–22 clean; E 23–26 clean; F 27 clean (both seeds reconcile, one late charge per installment), F 28 clean, F 29 no stale text found.
- Gates: the coordinator's round-2 snapshot (7/7 green) is cited; not re-run by the auditor.
- Revision_1 charter REDs CW-1 … CW-9: all closed. Open charter-wide REDs: N-1, N-2.

VERDICT revision_2: task0=PASS task1=RED charter=N-1,N-2

## revision_3

### charter_global_frozen (revision_3)
- 2026-10-20. Gate: worklog tail `REWORK round 3: gates 7/7 green`. Round-3 snapshot (`snapshot.sh contract_payments_fees_and_servicing 3`, 2026-10-20T06:38:05): check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks --check REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK; check_grounding GROUNDING OK; check_cross_fire SCOPE OK. Masked views r3: 0.json c0912b99…d227, 1.json 6cc6c8af…b65b — identical to r2, so both worlds are unchanged and the revision_2 frozen derivations stand by reference (no fresh freeze needed).
- Source hashes: `contract.extended.yaml` 37caa7b6c176444a71700f3b047c81da2e39c5239bf6bf3c7a427eec564a4510 (changed from 800247a3…); `task_tools.py` 5078f93b… (unchanged). Re-derivation scope set by a structural diff against the saved r2 charter (/tmp/audit_contract_0072/r2/charter_r2.yaml vs charter_r3.yaml): base section, every policy's compute, params, prerequisite, overwrite and baseline are identical; only rule sentences, compute_basis quotes and one factor ladder text changed:
  - LC: first-delinquency count "late charges assessed on the contract, waived or not, …".
  - HF: late-charge credit "the late charges assessed on the installment due on next_due_date, waived or not, …".
  - STMT: window tier 2 "had a late charge assessed, waived or not, …"; remittance "counting payments posted on the contract whether or not later returned, …" and last tier "in every other case (only recurring autopay drafts or third-party remittances, payment_channel ach_autopay or third_party_remittance, or no payments posted in that period), none are added"; remittance_method_days ladder text matches.
- Mechanical sweep repeated: every compute_basis, replaced_by, policy_source and baseline.rule verbatim in its rule.

### re-derived checks (revision_3)
- Rule/compute: each new "waived or not" / "whether or not later returned" phrase matches compute, which never filters waivers or returns in those reads (COUNT/SUM over contract_fee_assessed late_charge; COUNT over contract_payment_posted by channel). The remittance ladder now covers all ten payment channels a posted payment can carry (check_mail; the seven one_time_channels; ach_autopay, third_party_remittance in "every other case") — disjoint and gap-free.
- Every other revision_2 conclusion (conflict scan, graph, sentences, overrides, factor counts/labels/method tables, realism, assembly sentences, tie rules, rolling windows) rests on unchanged text and stands by reference to §revision_2.
- XF_recipe sweep on the r3 charter: A 1–7 clean; B 8–10 clean (B 9: N-1 closed); C 11–12 one member (N-3 below), C 13–17 clean; D 18–22 clean; E 23–26 clean; F 27–29 clean (worlds unchanged; task proof texts updated to say the returned 2026-10-14 payment is counted — consistent with the rule now).

### findings (revision_3)
- N-1 closed: the remittance ladder's last tier names every remaining source explicitly ("in every other case …"); no channel falls outside a stated tier.
- N-2 closed: "counting payments posted on the contract whether or not later returned" — task 1's reading B is excluded by the rule text.
- Class sweep (rows whose returned/waived status a read leaves open), exhaustive over every fee-row and payment-row read of the charter: LC late-charge count — states "waived or not" ✓; LC autopay count and latest payment — "returned or not" ✓; DM payment activity — "returned or not" ✓; HF late-charge credit — "waived or not" ✓; STMT window late-charge test — "waived or not" ✓; STMT remittance — "whether or not later returned" ✓; STMT/PAY latest posted payment — returned case stated ✓; RPF/STMT/PAY return counts and latest return — returns by reason, no waiver question ✓; RPF monthly cap — "assessed and unwaived" ✓; **RPF failed-payment offset — open (N-3)**.

**N-3 SOURCE-POLICY — RPF failed-payment offset silent on a waived agent-assisted fee (XF C-11/C-12).** Rule: "when the returned payment was taken by a representative (a payment_channel listed in agent_channels) and an agent-assisted payment fee was charged on it, that agent-assisted fee is taken from the returned-payment fee". Compute: `agent_fee_on_returned = SUM(… event_type='contract_fee_assessed', fee_type='agent_payment_fee', related_txn_id=returned_payment_id)` — counts the fee whether or not it was later waived. Producible situation: base contract_evt_fee_waiver lets an agent-assisted fee "shown to be assessed in error" be waived (assessed_in_error); a payment carrying such a waived fee is then returned. Reading A (compute; the fee "was charged"): offset = the fee (e.g. 7.95). Reading B (a waived fee is not owed, so nothing is refunded twice; the charter now says "waived or not" wherever it means to count waived fees): offset 0 — the returned-payment fee is higher by the fee amount. Only member left in the class. It was already present in the revision_2 charter and was not listed in revision_2 (missed by that pass). No consequence on either current world (task 1's agent fee dd5d5691… is unwaived).

Observations unchanged from revision_2 (O-21 and O-22 still apply to task 1).

## closing_checklist (revision_3)
- Files: revision_3 appended to _difficulty.md, 0.md, 1.md; earlier revisions untouched.
- Scored solutions: GT call arguments and every computations expected / baseline_result / factor_sensitivity figure in both tasks are unchanged from revision_2 and equal the frozen revision_2 derivations (re-read 2026-10-20 after the r3 snapshot).
- Scope, trees, factor floors, uuid8s: unchanged, as revision_2.
- Gates: the coordinator's round-3 snapshot (7/7 green) is cited; not re-run by the auditor.
- Revision_2 charter REDs N-1, N-2: closed. Open: N-3 (charter-only, RPF — a task 1 policy).

VERDICT revision_3: task0=PASS task1=RED charter=N-3

## revision_4

### charter_global_frozen (revision_4)
- 2026-10-20. Gate: worklog tail `REWORK round 4: gates 7/7 green`. Round-4 snapshot (`snapshot.sh contract_payments_fees_and_servicing 4`, 2026-10-20T08:05:41): check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks --check REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK; check_grounding GROUNDING OK; check_cross_fire SCOPE OK. Masked views r4: 0.json c0912b99…d227, 1.json 6cc6c8af…b65b — identical to r2/r3; worlds unchanged, revision_2 frozen derivations stand.
- Source hashes: `contract.extended.yaml` fe9a90945d3d34b64a2dd4f156efc1220ee185d535a3c7ba49d53f73594d54c0 (changed from 37caa7b6…); `task_tools.py` 5078f93b… (unchanged).
- Structural diff r3 -> r4 (saved copies charter_r3.yaml / charter_r4.yaml): base section identical; in all six policies compute, params, prerequisite, overwrite and baseline identical. Only change: RPF rule sentence "Failed-payment offset: … and an agent-assisted payment fee was charged on it, waived or not, that agent-assisted fee is taken from the returned-payment fee; …", its three compute_basis quotes, and the failed_payment_offset_rule tier-1 ladder text ("…, waived or not"). Mechanical sweep: every compute_basis, replaced_by, policy_source, baseline.rule verbatim in its rule; every superseded_clause verbatim in its base rule.

### findings (revision_4)
- N-3 closed: the rule now says the agent-assisted fee is taken "waived or not", which is what `agent_fee_on_returned` (SUM over assessed agent fees on the returned payment, no waiver filter) computes; the ladder text matches. Reading B of revision_3 is excluded by the text.
- Class sweep re-run exhaustively over every fee-row and payment-row read (the revision_3 list): LC late-charge count "waived or not"; LC autopay count and latest payment "returned or not"; DM activity "returned or not"; HF late-charge credit "waived or not"; STMT window late-charge test "waived or not"; STMT remittance "whether or not later returned"; STMT/PAY latest posted payment with returned case stated; RPF agent-fee offset "waived or not"; RPF monthly cap "assessed and unwaived"; return-row reads (RPF, STMT cushion, PAY) by reason/date — no waiver question. No open member.
- XF_recipe sweep on the r4 charter: A 1–7, B 8–10, C 11–17, D 18–22, E 23–26, F 27–29 — no member (unchanged text otherwise; revision_2/3 conclusions stand by reference).
- No regression: GT (re-read after the snapshot) unchanged in both tasks — task 0: 7.69 / 2 / 43.97 with sensitivities 9.61 / 13.19 / 11.18 / 10.49 (25.00), 1×6 (1), 59.80 / 32.31 / 51.66 / 38.97 / 38.97 / 33.97 (30.00); task 1: 39.55 / (2026-11-02, 8518.41) / 8488.92 with sensitivities 34.55×3 / 40.00 / 34.55 / 37.05 (25.00), 8540.85 / 8504.94 / 8493.41 / 8527.38 / 8513.92 / 8504.94 (8493.41), 8479.94 / 8475.46 / 8479.94 / 8484.43 / 8484.43 (8448.53); resolution orders unchanged — all equal to the frozen revision_2 derivations.
- Observations still open (not grounds for rework): O-1, O-2, O-3, O-5 (softer realism notes), O-6, O-9, O-10, O-12, O-13, O-14, O-16, O-17, O-18, O-19, O-20, O-21 (task 1: the five statement day factors net to the baseline window, so the all-baseline good-through date equals 2026-11-02), O-22.

## closing_checklist (revision_4)
- Per-task files 0.md, 1.md and _difficulty.md each carry revisions 1–4; old revisions untouched; derivations frozen before every reveal; both comparison sections PASS (revision_2 comparisons stand; revision_4 re-read confirms no change).
- Coverage/scope: task 0 {LC, DM, HF}, task 1 {RPF, STMT, PAY} — pairwise disjoint, jointly all six extended policies; task tools closed against GT; uuid8s independent and frozen (module unchanged since revision_1).
- Trees: each task has 2 prerequisite problems, 2 value_input edges, one owner=user write, no cycle; the difficulty graph HF->{DM, LC}, STMT->RPF, PAY->{STMT, RPF} is acyclic.
- Factors: every computation has a self-sufficient baseline and 4–6 factors (>= 2 parameter, >= 1 method); per task >= 1 multi-source (HF.charge_units; RPF.return_fee_schedule) and >= 1 cross-difficulty (task 0: cpi, recovery; task 1: cpi, recovery); every ladder >= 3 tiers stated in its rule, distinct outcomes, realistic conditions; every factor bears weight against an honest baseline and the baseline alone gives a definite number different from gold.
- Gates: coordinator round-4 snapshot 7/7 green on the final form (cited; not re-run by the auditor; check_traceability excluded by brief).
- All charter-wide REDs of revisions 1–3 (CW-1 … CW-9, N-1, N-2, N-3) closed. The difficulty passes the source-layer audit.

VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN
