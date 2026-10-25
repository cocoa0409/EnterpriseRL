# KB audit — insurance_claims_and_denials (product `claim`) — difficulty close-out

## revision_1

### Entry conditions (cited, not re-run by the auditor except the coordinator's execute-only snapshot)
- Policy-side verdict: `VERDICT revision_12: task0=PASS task1=PASS charter=CLEAN`.
- Snapshot 2026-10-21T22:42:10 and again 22:56:17 (final form, unchanged): check_docs claim => DOCS OK; check_traceability => TRACEABILITY OK (0 misses); EXTENDED / TASK TOOL CONTRACT / REPLAY --check / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; sha256 e1af5953534e e48614b9837b 4e988804d476 b6a28533b8d1 (as briefed); runtime views 5bf245d29f6fbe70 / 7d96e32bc5f79b80.
- DB access: db_query.py (Engine.call("agent", …)); blind audits not contaminated (see runtime_context files).

### Per-task part verdicts
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Task |
|---|---|---|---|---|
| 0 | PASS (all 4 values, tree, order, owners equal GT) | PASS | RED kb-1, kb-2 | RED |
| 1 | PASS (all 4 values, tree, order, owners equal GT) | PASS | RED kb-3, kb-4 | RED |

### KB items
- **kb-1** `preoperative_laboratory_schedule_pricing_0cabe7c9` worked example reproduces task 0's lab rows (85025 2u, 80048 1u, 85610 1u; PPO; Grand Chute) and its value 35.3625.
- **kb-2** `surgery_ondansetron_unit_rate_9be73fc1` footnote "4 units on a Commercial PPO Claim with charges of 36.00 are valued at 7.60" = task 0's J2405 line and value.
- **kb-3** `observation_ondansetron_unit_rate_fa1ce404` "2 units on a Commercial HMO Claim, charges 18.00 → 3.30" = task 1's J2405 line and value.
- **kb-4** `self_administered_drug_dispensing_fee_c4a1fc9c` "4 lines of the three drug codes on an Observation Stay Account at Neenah → 2.00" = task 1's drug lines, account class, campus and fee.
(Semantics are correct in all four; the defect is that a factor document's example states one task's evidence rows and pre-derives that customer's tier and value. No scored value appears anywhere in the corpus or the unlock schemas.)

### Cross-product pass (ONE exhaustive pass; every member listed; judged against the owning product's published docs as of each row's posting date)
Other-category rows seeded for the two task customers: encounter only (plan, assist, estimate, visit/appointments, records: none — queried for both customers).
Task 0 (Gretchen Hallstrom):
1. Account 33a1a49e (ED, Appleton, svc 2025-11-03, final bill 11-07 = 4 bill-hold days per `patient_class_billing_schedule`, closed 12-20) — OK.
2–6. Five ED charge lines (2140/1018/38/64/152 = 3412 = claim billed) — OK.
7. DEDUCTIBLE liability 420.00 (2025-12-02, claim 14955304) = remit PR-1 420.00 (`final_bill_and_patient_liability`) — OK.
8. Summary statement cycle 1, PATIENT_PORTAL, 2025-12-08 — OK.
9. Payment 378.00 PORTAL_CARD 2025-12-20 — **MISS (src-1)**.
10. PROMPT_PAY_DISCOUNT 42.00 sourced to the payment, 2025-12-20 — **MISS (src-1)**.
11. Account 1e7eec41 (Outpatient Surgery, Grand Chute, svc 2026-05-12, final bill 05-17 = 5 bill-hold days, closed 06-17 with no patient liability) — OK.
12–37. 26 surgery charge lines (sum 19,727.00 = claim billed) — OK (observation: lines 19–26 carry CDM numbers of the 32xxxxx series used on the Appleton account, lines 1–18 the 41xxxxx series; no published rule governs CDM numbering).
Task 1 (Joyce Gerhardt):
38. Account 9f76f129 (Observation, Neenah, 2026-03-30..04-01 = 3-day span ≤ 3, final bill 04-05 = 4 bill-hold days, closed 05-28) — OK.
39–59. 21 observation charge lines (sum 10,839.00 = claim billed; G0378 46 h) — OK.
60. COPAY liability 150.00 (2026-05-07) = PR-3 150.00 — OK.
61. Summary statement 2026-05-12 PATIENT_PORTAL — OK.
62. Payment 150.00 PORTAL_CARD 2026-05-28, no discount — OK (Observation prompt-pay minimum 250.00 per `prompt_pay_terms`; `prompt_pay_discount_policy` §3 in force).
63. Account 9565d3b0 (Clinic, Neenah, 2026-02-10, final bill 02-13 = 3 bill-hold days, no statement, closed 03-09) — OK.
64. Charge 412.00 (99204/0510) — OK.
65. POINT_OF_SERVICE payment 40.00 on 2026-02-10 — OK (balance 40.00 < clinic minimum 50.00; no first statement).
66. COPAY liability 40.00 (2026-03-09) = PR-3 40.00 — OK.
Cross-product figures in the claim corpus:
67. `self_administered_drug_value` account-class rule (uninsured % and the insured-non-covered yes/no) — matches encounter `uninsured_discount_schedule` (figures stated "remain valid" by `uninsured_discount_policy`); Observation "no" → ×1 — OK.
68. `take_home_convenience_value` "The Outpatient Surgery Account class gives an insured patient's non-covered items no uninsured discount" — matches the schedule row — OK.
69. Waiver tests' liability source "non-covered service" — matches encounter liability sources in `final_bill_and_patient_liability` — OK.
70. Patient classes / campuses named in scopes — match encounter class schedule — OK.

### Source-side items
- **src-1** (cross-product seed, task 0 world; gold unaffected). The ED account's 2025-12-20 payoff is priced under the encounter base sentence that the published encounter KB marks "no longer in force" (`prompt_pay_discount_policy` §2): 10 % of 420.00 = 42.00, payment 378.00. The published current basis for an insured account paid in full inside the window (`insured_account_payoff_in_full`, `insured_payoff_amount_calculation`) adds the factor points the records support: days to pay 12 (first statement 12-08 → payment 12-20) → +2 (`insured_payoff_days_to_pay_schedule`); latest summary statement by patient portal → +1 (`insured_payoff_paperless_allowance`); liability total 420.00 → 0; non-covered share 0 → 0; no point-of-service payment → 0. 13 % of 420.00 = 54.60 discount, payment due 365.40. Rows 9–10 are not a state the published encounter charter produces.
- **src-2** (own-category seed realism, both tasks; gold unaffected). Each task's remittance leaves exactly the non-covered items' charges unaccounted and still "expected from the payer": task 0 claim ee1be581 billed 19,727.00 vs payment 11,175.84 + CO-45 7,928.16 → payer_balance 623.00 = E0218 590 + A9273 9 + A4467 24; task 1 claim c0bcf67a billed 10,839.00 vs 5,440.52 + CO-45 5,160.48 + PR-3 150.00 → payer_balance 88.00 = the four 0637 drug lines. A real 835 balances (charges = paid + adjustments + patient responsibility); the base remittance-posting rule posts only the lines the payer reports, and the claim's own KB says these items are covered by no payer class / excluded from the agreements — yet the seed shows them still expected from the payer with no remit line (no CO-96/PR-204). The ED and clinic claims of the same customers balance.
- **src-3** (source ladder wording). claim_ext_surgery_post_payment_refund factor blood_bank_typing_handling: tier "a Commercial PPO claim AND code 29882 is billed (the arthroscopy case rate is paid)" / rule "packaged into the arthroscopy case rate … (the procedure that case rate pays)" — a factor of the refund policy names a tier of another policy's factor (claim_ext_member_decision_closeout / surgical_pricing_method). The test itself is a record test (PPO + 29882 under 0360), but the rendered factor document `blood_bank_typing_value_on_surgery_refunds` must carry the name, so the refund corpus points a task-0 reader at the existence of the member-decision value's operating-room case rate. KB carriage faithful; reported source-side.

### Notes (policy-side, not counted)
- **N-1 generic assembly sentences.** Each extended rule carries the XF-3 generic assembly sentence ("Each adjustment below either replaces … or multiplies the total; replacements first, the multiplier after them, then the recovery limit …"); the renderer moved it, softened ("Each group of lines is valued first … a multiplier of the total applies after them"; refund: "any amount taken from the retained value comes after it"; drugs: "any dispensing fee is added to them"; "(… the lesser of the scheduled amount and the billed charges)"), into the six computation documents. Meaning unchanged at entailment; the order is needed (non-commuting multiplier / limit / deduction), the baseline must carry it, and any placement presupposes that adjustments exist. Findability was not pre-solved: in both blind audits every factor was reached from record words. Judged: not a KB defect; inherent to the mandated source form.
- **N-2** rule vs compute on the observation case rate with no hour billed: the rule's pharmacy sentence ("carries no value of its own only when the observation case rate that packages it is paid (the case-rate method with observation hours billed)") and compute (`pharmacy_value = 0 if case rate and hours > 0 else pharmacy × pct`) agree; KB carries it. No issue.
- **N-3** coincidental figure: `surgery_cefazolin_unit_rate` example charges "45.00" equal task 1's scored drug value numerically; unrelated quantity, not a leak.
- BLUEPRINT-KNOWN claim_takeback rows written by the two refund tools: logged by coordinator, not judged.

### Closing checklist
- [x] runtime_context 0.md / 1.md: blind_answer frozen before reveal, gt_comparison appended (both PASS).
- [x] policy_kb 0.md / 1.md: source_to_kb, kb_to_source, bijection_verdict (PASS), dependency_form (RED).
- [x] All 8 prerequisite sentences verbatim, state form, in the blocked policy's own hub (2) or computation document (6), nowhere else; every hop resolvable from depended-on documents + records.
- [x] Every factor ladder (42 factors across 8 policies) carried tier for tier in its own document.
- [x] Retired surface: 2 base clauses rendered retired; no undeclared retirement.
- [ ] KB-EXPLICIT clean — open: kb-1..kb-4.
- Final-form gate lines: snapshot 2026-10-21T22:56:17 (above).

VERDICT revision_1: task0=RED task1=RED kb=kb-1,kb-2,kb-3,kb-4 src=src-1,src-2,src-3

## revision_2

### Entry conditions
- `RENDER round 3: DOCS OK 76 docs` (RENDER.log tail); `VERDICT revision_13: task0=PASS task1=PASS charter=CLEAN`.
- Snapshot 2026-10-22T00:31:02: check_docs claim => DOCS OK; check_traceability => TRACEABILITY OK (0 misses; 0 non-unlock misses); EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (--check); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; sha256 b4b478fb4fbe (extended) e48614b9837b (task_tools) 6769ef6a9d7a (tasks/0) b6a28533b8d1 (tasks/1); runtime views unchanged (5bf245d29f6fbe70 / 7d96e32bc5f79b80). docs/claim corpus sha 99256b5a22dcfa5d.

### Per-task part verdicts
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Task |
|---|---|---|---|---|
| 0 | PASS (re-derived 11058.88 / 38.30 / 312.56 / 9111.77 = GT; gold unmoved) | PASS | PASS | PASS |
| 1 | PASS (re-derived 4121.86 / 12.33 / 45.00 / 2317.43 = GT; world and gold unchanged) | PASS | PASS | PASS |

### Round-1 items
- kb-1..kb-4: **closed** (each example now uses inputs no task row has; full example sweep for both tasks clean; no regression, no new mirror).
- src-1: **closed**. Re-run on the touched rows: ED account 33a1a49e payment 365.40 PORTAL_CARD and PROMPT_PAY_DISCOUNT 54.60 sourced to that payment (2025-12-20) = the published insured payoff (10 % class + 2 days-to-pay [12 days] + 1 paperless [portal] = 13 % of 420.00); account balance 420.00 − 365.40 − 54.60 = 0.00, closed 2025-12-20; claim 14955304 rows unchanged. No other row of either customer changed (task-0 surgery claim/account and every task-1 row identical to revision_1). Cross-product members 1–8, 11–70 of revision_1 re-confirmed unchanged and OK; members 9–10 now OK.
- src-3: **closed**. Rule sentence, its compute_basis copies and the ladder now state the PPO typing tier as a bundle of the 29882 procedure under the PPO agreements; no reference to another policy's factor remains; KB carries it verbatim.
- src-2: **not closed in the seed** (payer_balance 623.00 / 88.00 still equals the non-covered items with no remittance line). The reworker and the policy auditor show that the frozen claim_transactions model has no row for a reported-but-unposted PR-204 line: a PR-204 release would release the items to the patient against base routing (no waiver) and switch off the write-off rules; a CO-45/CO-96 adjustment would drive the payer balance negative after the write-off; a 0.00 row breaks the amount format. I verified that analysis against the base routing sentence and the write-off scopes and accept it: the seed is the closest one the frozen schema allows, and it reads as "an 835 whose PR-204 line awaits routing". No scored figure, edge or reading depends on the missing line. **Reclassified as blueprint-level BL-1** (needs a remittance-line event that does not move payer_balance, or remit fields on the write-off — outside this difficulty's write territory) and handed to the coordinator; not counted in this difficulty's src list.

### Notes carried
- N-1 (generic assembly sentences in computation documents) unchanged — source-mandated form, faithfully carried; not counted.
- BL-1 (above). BLUEPRINT-KNOWN claim_takeback rows: coordinator-logged.

### Closing checklist
- [x] revision_2 appended to runtime_context 0.md/1.md (re-derivation frozen before reading round-13 source, contamination disclosed, gt_comparison PASS) and policy_kb 0.md/1.md (bijection PASS, dependency_form PASS); revision_1 text untouched.
- [x] 8/8 prerequisite sentences verbatim, state form, blocked side only; 42 factor ladders complete; retirements unchanged.
- [x] Final-form gate lines: snapshot 2026-10-22T00:31:02 above.

VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=NONE
