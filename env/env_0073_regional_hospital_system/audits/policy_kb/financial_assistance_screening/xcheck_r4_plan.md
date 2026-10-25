# Patient Payment Plan seed-row legality cross-check (env_0073, tasks 0 and 1)

Criterion: published docs `env/env_0073_regional_hospital_system/docs/plan/*.json` (title + content). plan.yaml was consulted only to confirm that no record field carries the hardship income-loss figure. Context rows: encounter accounts and transactions, insurance claims, assistance cases and transactions, and price estimates from t0_db.json and t1_db.json.

Doc short names used below:
- BANDS = enrollment_bands_and_tier_entry_056d647d
- TIER = tier_assignment_and_schedule_terms_1f648bf7
- SIGN = agreement_signature_and_start_ca52ff85
- TERMS = term_installment_and_due_dates_5051e312
- REFIG = unsigned_offer_refigure_action_1a6e2cc2 ("what still holds at a plan's creation"; signed-plan reduction effect)
- COLLECT = installments_collected_with_down_payment_0cea8ccd
- ELIG = enrollable_balances_rule_aadd89d3 + enrollable_balance_conditions_208b119c
- ADDON = add_on_enrollment_rule_3430c7ff + add_on_balance_terms_eef6dd21
- RECOMP = recomputed_installment_remaining_schedule_eba7644d + installment_recompute_after_added_balances_4825a4d5 + installments_paid_count_for_recompute_2b5ff10f + recompute_term_screening_limit_ff4bc54c + recompute_installment_floor_c1f9173f + add_on_frequency_term_extension_5f20a66b + latest_added_care_installments_c391672e
- RED = enrolled_balance_reductions_ead6ff38
- PAY = payment_methods_and_posting_schedule_ee2082f3 + installment_payments_and_payoff_d440df70
- MISS = missed_installments_and_default_schedule_1725b747 + installments_moved_on_reage_fd2e4d00 (missed definition) + assistance_pause_account_action_269b2033
- ONE = one_open_plan_per_patient_08af4ec9
- CHG = charges_and_credit_protection_50b883a3 + missed_installments_and_default_rule_c7125506 cl.6

## (1) Every row

### Task 0 (frozen 2025-10-21): plan 3d0a5ecb, Riverbend Hardship Payment Plan

| # | Row type | Date | Amount / key fields | Check | Verdict | Docs |
|---|---|---|---|---|---|---|
| P0 | plan | offered 2025-03-12, signed 2025-03-14 | Hardship tier; term 60; due day 15; first due 2025-04-15; down 0.00; autopay ACH | Hardship min/max 25.00/50000.00: enrolled total 10427.88 is inside. The 25000.00 balance showing is not met, so entry rests on a documented ≥25% income loss, which no record carries (see doubtful D1). Signed 2 days after the offer, within the 21-day deadline. Term 60 equals the tier maximum (default when no term is stated). Down payment 0% gives 0.00. Due day 15 is an allowed option. First due date: the first 15th at least 30 days after 03-14 is 04-15 (32 days). 32 days is ≤45, so no installments are collected at signing. Autopay is not required and ACH is an offered method. This is the only open plan. | OK (D1 noted) | BANDS, TIER cl.2/6, SIGN cl.2, TERMS, REFIG, COLLECT, PAY, ONE |
| P0 | plan (monthly_payment_usd) | — | 501.11 | Equals the last recompute (row T0-9 below). The 10-14 dispute withdrawal leaves it unchanged, per REFIG: "on a signed plan a reduction still never changes the installment amount, it shortens the remaining schedule". | OK | RECOMP, REFIG |
| P0 | plan (plan_balance) | 2025-10-21 | 14161.33 | 29121.88 enrolled − 1560.55 paid − 13400.00 reduced = 14161.33. This also equals the sum of the five non-withdrawn accounts' patient balances (867.33 + 8000 + 420 + 3950 + 924). | OK | lowest_installment (ledger definition), RED |
| P0 | plan (next_due/missed/status) | 2025-10-21 | next 2025-09-15; missed 0; active | The 09-15 and 10-15 installments are unpaid. The 09-15 one is past the 30 grace days by 10-15. An FA case has been open in submitted status since 2025-08-26, so both fall due while the application is open: "not counted as missed ... until a pause is booked they stay paused for up to the tier's assistance pause days" (Hardship 90; 08-26 + 90 = 11-24). So missed 0, active and next due 09-15 are consistent. | OK | MISS, assistance_pause_account_action |
| P0 | plan (counters, fees) | — | reage/reinst/terms_change/skip 0; no default/closed date | No such events. No charges on any tier. | OK | CHG |
| T0-1 | plan_balance_enrolled b55d0d0a | 2025-03-12 | 2427.88 | Account: liability 2000 + 727.88 − payments 150 + 150 = 2427.88 on 03-12. Status patient_due, claim closed 2024-10-15, no hold, no agency placement. | OK | ELIG |
| T0-2 | plan_balance_enrolled 98c60690 | 2025-03-12 | 8000.00 | Liability 3000 + 5000 (claim adjudicated 02-20). Patient_due, no hold. | OK | ELIG |
| T0-3 | plan_balance_enrolled 8bdb031d (add-on 1) | 2025-04-10 | 420.00 | Claim denied 03-27 with 420.00 transferred to the patient. Patient_due on 04-10, so not insurance pending. Add-on dates before 04-10: 0 < 4 allowed. The plan is signed, so the installment is recomputed (T0-4). | OK | ELIG, ADDON cl.1 |
| T0-4 | plan_installment_paid #1 | 2025-04-15 (due 04-15) | 180.80, PMT-4404151, AUTOPAY_ACH | Recompute after 04-10: scheduled 60 + extension 12 = 72, capped at the longest recomputed schedule of 60 (no open application). Less 0 paid and 0 missed gives 60. 10847.88 / 60 = 180.798 → 180.80, above the 10.00 floor. The account shows a PAYMENT_PLAN_INSTALLMENT of 180.80 on 04-15 with the same reference on b55d0d0a, the oldest service start (2024-09-17). | OK | RECOMP, PAY |
| T0-5 | plan_installment_paid #2 | 2025-05-15 | 180.80, PMT-4405152 | Same installment. The matching account payment is on b55d0d0a. | OK | RECOMP, PAY |
| T0-6 | plan_balance_enrolled 8794d6ff (add-on 2) | 2025-05-20 | 924.00 | 1680 liability − 756 uninsured discount = 924 on 05-05. Patient_due. The GFE on this encounter is closed with no dispute. Add-on dates before: 1 (04-10) < 4. | OK | ELIG, ADDON |
| T0-7 | plan_installment_paid #3 | 2025-06-15 | 196.73, PMT-4406153 | Balance 10847.88 − 361.60 + 924 = 11410.28. Remaining schedule: min(72, 60) − 2 paid = 58. 11410.28 / 58 = 196.729 → 196.73. The matching account payment is on b55d0d0a. | OK | RECOMP, PAY |
| T0-8 | plan_balance_enrolled c88c4cb6 (add-on 3) | 2025-07-08 | 3950.00 | 7900 − 3950 uninsured discount on 07-01. Patient_due. Add-on dates before: 2 < 4. | OK | ELIG, ADDON |
| T0-9 | plan_balance_enrolled fa2bc102 (add-on 3, same date) | 2025-07-08 | 13400.00 | 26800 − 13400 on 06-29. Patient_due on 07-08; the GFE dispute hold only starts on 10-14. Same date as T0-8, so it is one add-on. The enrolled total of 29121.88 stays ≤ 50000.00, so there is no tier overflow. | OK | ELIG, ADDON cl.1/3 |
| T0-10 | plan_installment_paid #4 | 2025-07-15 | 501.11, PMT-4407154 | Balance 11410.28 − 196.73 + 17350 = 28563.55. Remaining schedule: min(72 (+2 for an Observation Stay latest add-on), 60) − 3 = 57. 28563.55 / 57 = 501.115 → 501.11. The matching account payment is on b55d0d0a. | OK | RECOMP, PAY |
| T0-11 | plan_installment_paid #5 | 2025-08-15 | 501.11, PMT-4408155 | Same installment. The matching account payment is on b55d0d0a. b55d0d0a's cumulative 1560.55 is less than its 2427.88 enrolled, so oldest-first allocation never spills over. | OK | PAY |
| T0-12 | plan_balance_reduced fa2bc102, BALANCE_WITHDRAWN_FOR_DISPUTE | 2025-10-14 | 13400.00 | Account went to billing_hold GFE_DISPUTE_PENDING on 10-14 (estimate ad051669 dispute filed 10-14). "whole remaining enrolled balance withdrawn, with the reason recorded as balance withdrawn for dispute". No installment was allocated to fa2bc102, so it still carried 13400.00, and the reduction does not exceed what the account carries. The installment is unchanged on a signed plan (REFIG). | OK | RED cl.2/4, REFIG |

### Task 1 (frozen 2025-11-18): plan 7496ef5b, Riverbend Assistance-Linked Payment Plan

| # | Row type | Date | Amount / key fields | Check | Verdict | Docs |
|---|---|---|---|---|---|---|
| P1 | plan | offered 2025-03-03, signed 2025-03-05 | Assistance-Linked; term 48; due day 15; first due 2025-04-15; down 0.00; autopay ACH | On 03-03 the patient held case 88445a3a, approved 2024-12-12, "Medical Hardship Assistance". Medical hardship is a listed partial-discount tier; the award ends 2025-12-12. Enrolled total 2212.40 is inside 25.00–50000.00. Hardship override not shown: balance < 25000 and no income-loss record. Signed 2 days after the offer, within the 21-day deadline. Term 48 equals the tier maximum. Down payment 0% gives 0.00. First due: the first 15th at least 30 days after 03-05 is 04-15 (41 days). 41 days is ≤45, so nothing is collected at signing. Autopay is not required and ACH is offered. This is the only plan. | OK | BANDS, TIER cl.2/6, SIGN, TERMS, REFIG, COLLECT, PAY, ONE |
| P1 | plan (monthly_payment_usd) | — | 145.87 | Equals the last recompute (T1-8). | OK | RECOMP |
| P1 | plan (plan_balance) | 2025-11-18 | 5980.71 | 6628.90 − 648.19 = 5980.71, which equals the sum of the three account balances (1564.21 + 1180 + 3236.50). | OK | ledger definition |
| P1 | plan (next_due/missed/status) | 2025-11-18 | next 2025-11-15; missed 0; active | Installment 8 (due 11-15) is unpaid 3 days later, inside the 20 grace days. FA case c89f7d28 has also been in submitted status since 11-14, which pauses it. Installments 1–7 are paid. | OK | MISS |
| P1 | plan (counters, fees) | — | all 0 | — | OK | CHG |
| T1-1 | plan_balance_enrolled 85898edb (creation) | 2025-03-03 | 2212.40 | Liability 2000 + 212.40 (claim adjudicated 02-05). The FA application of 02-08 left the liability at 2212.40, so no reduction was due. Patient_due, no hold. | OK | ELIG, RED cl.1 |
| T1-2 | plan_installment_paid #1 | 2025-04-15 | 46.09, PMT-4404152, AUTOPAY_ACH | Creation installment: 2212.40 / 48 = 46.0917 → 46.09, above the 20.00 floor. The matching account payment is on 85898edb (oldest service start, 2025-01-09). | OK | REFIG (creation), TERMS, PAY |
| T1-3 | plan_installment_paid #2 | 2025-05-15 | 46.09, PMT-4405153 | The matching account payment is on 85898edb. | OK | PAY |
| T1-4 | plan_installment_paid #3 | 2025-06-15 | 46.09, PMT-4406154 | The matching account payment is on 85898edb. | OK | PAY |
| T1-5 | plan_balance_enrolled 15c52208 (add-on 1) | 2025-07-01 | 1180.00 | Claim denied 06-13 with 1180.00 transferred to the patient. Patient_due on 07-01. Add-on dates before: 0 < 4. | OK | ELIG, ADDON |
| T1-6 | plan_installment_paid #4 | 2025-07-15 | 72.31, PMT-4407155 | Balance 2212.40 − 138.27 + 1180 = 3254.13. Remaining schedule: 48 + 12 = 60, capped at 48 (no open application on 07-01: the 2024 case is approved, the 2025 case is dated 11-14). Less 3 paid gives 45. 3254.13 / 45 = 72.314 → 72.31. The matching account payment is on 85898edb. | OK | RECOMP, PAY |
| T1-7 | plan_balance_enrolled 83759b05 (add-on 2) | 2025-07-20 | 3236.50 | Liability 2500 + 736.50 (claim adjudicated 07-08). The FA application of 07-11 left 3236.50. Patient_due. The claim appeal was filed 09-24, after enrollment. Add-on dates before: 1 < 4. | OK | ELIG, ADDON |
| T1-8 | plan_installment_paid #5 | 2025-08-15 | 145.87, PMT-4408156 | Balance 3254.13 − 72.31 + 3236.50 = 6418.32. Remaining schedule: min(60, 48) − 4 = 44. 6418.32 / 44 = 145.871 → 145.87. The matching account payment is on 85898edb. | OK | RECOMP, PAY |
| T1-9 | plan_installment_paid #6 | 2025-09-15 | 145.87, PMT-4409157 | The matching account payment is on 85898edb. | OK | PAY |
| T1-10 | plan_installment_paid #7 | 2025-10-15 | 145.87, PMT-4410158 | The matching account payment is on 85898edb. The cumulative 648.19 is less than 2212.40, so oldest-first allocation never spills over. | OK | PAY |

Other cross-checks with no findings:
- Every plan installment row has exactly one PAYMENT_PLAN_INSTALLMENT account payment with the same date, amount and reference, and there are no extra PAYMENT_PLAN_INSTALLMENT payments.
- No enrolled account received a final notice, agency placement or statement after enrollment.
- No encounter is enrolled twice.
- The t1 GFE-disputed account 6d6927ad was never enrolled, so no withdrawal was needed.

## (2) MISS list

None. Every row in both tasks is reproducible from the published rules:
- installments 180.80, 196.73, 501.11 (task 0) and 46.09, 72.31, 145.87 (task 1)
- plan balances 14161.33 and 5980.71
- due dates and next-due/missed status
- enrollment amounts and dates
- the dispute withdrawal and its unchanged installment
- the installment-to-account allocation

So nothing here can move a financial-assistance figure. The figures the FA computations read are consistent:
- Active-plan installment as a percent of one twelfth of income: 501.11 against 112800 / 12 in task 0, and 145.87 against 99600 / 12 in task 1.
- Patient payments in the 12 months before approval: the PAYMENT_PLAN_INSTALLMENT postings, plus the non-plan payments on b55d0d0a (150.00 on 2024-11-25 and 2025-01-10) and 3541c5fd (40.00 on 2025-09-09) in task 0.

## Doubtful (not a miss)

- **D1 (task 0, plan P0, tier entry).** The Hardship tier requires "a documented loss of household income of at least 25 percent in the last 6 months, or enrolled balances above 25000.00" (BANDS; TIER cl.2). The enrolled total at creation (2025-03-12) was 10427.88, so only the income-loss showing could qualify the plan, and no record (plan, assistance or account) carries an income-loss figure. Without it, the balance band would put 10427.88 on the Long-Term tier: 36 months max, 10% down payment, 100.00 minimum, autopay required. That would change every installment, but no record contradicts the hardship tier, so this is unverifiable rather than a miss. The task-0 FA case (2025-08-26, income 112800) postdates creation and states no prior income. If it were a miss, it would change the installment read by the FA plan-burden factor.
- **D2 (task 0, T0-12 effect on the installment).** RED cl.3 says the clause "A reduction never changes the installment amount; it shortens the remaining schedule ..." is "no longer in force". But REFIG still states, as current, "on a signed plan a reduction still never changes the installment amount, it shortens the remaining schedule". So 501.11 after the 10-14 withdrawal follows REFIG, and no published current basis recomputes it. The internal tension between the two docs is a KB-wording point, not a row miss.
- **D3 (task 0, initial installment not visible).** The creation installment (10427.88 / 60 = 173.80) never appears on any row because the 04-10 add-on was recomputed before installment 1. This is consistent with the rules, just not directly evidenced.

## Round 4 re-check

Inputs: t0_db_r4.json and t1_db_r4.json, diffed against t0_db.json and t1_db.json. Criterion: the same 60 docs in docs/plan. No plan doc was modified after the first pass (no file is newer than t0_db.json). Method and doc short names are the same as above.

Rows the rework changed: the plan record's monthly_payment and plan_balance, the enrollments listed below, every installment from #1 on in task 0 and from #4 on in task 1, and the matching account payments. Nothing else in the plan tables changed: dates, references, channels, installment numbers, the withdrawal and the plan header fields are identical to round 3.

### Task 0 (Hardship; recompute caps the schedule at 60, floor 10.00, no open FA application at any add-on date)

| Row | Date | Round 4 value | Check | Verdict |
|---|---|---|---|---|
| T0-3 enrollment e279f92f, 8bdb031d | 2025-04-10 | 252.00 | Account: 420.00 liability on 03-27 less the 168.00 uninsured discount on 03-27 gives 252.00 on 04-10. Patient_due, current balance 252.00. Add-on allowance unchanged (0 prior < 4). | OK |
| T0-4/T0-5 installments #1, #2 | 04-15, 05-15 | 178.00 each | 2427.88 + 8000 + 252 = 10679.88; min(60 + 12, 60) − 0 = 60; 10679.88 / 60 = 177.998 → 178.00. The b55d0d0a payments PMT-4404151 and PMT-4405152 are 178.00 on the same dates. | OK |
| T0-7 installment #3 | 06-15 | 193.93 | 10679.88 − 356.00 + 924 = 11247.88; 60 − 2 = 58; 11247.88 / 58 = 193.929 → 193.93. The b55d0d0a payment PMT-4406153 is 193.93. | OK |
| T0-8 enrollment 011087e2, c88c4cb6 | 2025-07-08 | 3030.00 | 7900 liability less the 3950 and 920 uninsured discounts, all posted 07-02, gives 3030.00. Statement on 07-05. Patient_due, current balance 3030.00. The liability, discounts and statement moved from 07-01/07-04 to 07-02/07-05; all are still before the 07-08 enrollment. | OK |
| T0-9 enrollment fa2bc102 | 2025-07-08 | 13400.00 (unchanged) | Unchanged. The enrolled total of 28033.88 is still ≤ 50000.00. | OK |
| T0-10/T0-11 installments #4, #5 | 07-15, 08-15 | 482.17 each | 11247.88 − 193.93 + 3030 + 13400 = 27483.95; 60 − 3 = 57; 27483.95 / 57 = 482.174 → 482.17. The b55d0d0a payments PMT-4407154 and PMT-4408155 are 482.17. | OK |
| T0-12 withdrawal fa2bc102 | 2025-10-14 | 13400.00 (unchanged) | No installment was allocated to fa2bc102, so the whole 13400.00 remained to withdraw. The installment stays 482.17 (REFIG). | OK |
| P0 monthly_payment_usd | — | 482.17 | Equals the last recompute. | OK |
| P0 plan_balance | 2025-10-21 | 13119.61 | 28033.88 enrolled − 1514.27 paid − 13400.00 withdrawn = 13119.61. Also equals the five remaining account balances (913.61 + 8000 + 252 + 3030 + 924). b55d0d0a: 2427.88 − 1514.27 = 913.61, matching the account's 913.61. | OK |
| P0 next_due/missed/status | 2025-10-21 | 09-15 / 0 / active | Unchanged; still covered by the open 08-26 FA case (pause up to 90 days). | OK |

### Task 1 (Assistance-Linked; recompute caps the schedule at 48, floor 20.00, no open FA application on 07-01 or 07-20)

| Row | Date | Round 4 value | Check | Verdict |
|---|---|---|---|---|
| T1-2..T1-4 installments #1–#3 | 04-15..06-15 | 46.09 (unchanged) | 2212.40 / 48. | OK |
| T1-5 enrollment e2de18b5, 15c52208 | 2025-07-01 | 944.00 | 1180.00 liability on 06-13 less the 236.00 uninsured discount on 06-13 gives 944.00 on 07-01. Patient_due, current balance 944.00. | OK |
| T1-6 installment #4 | 07-15 | 67.07 | 2212.40 − 138.27 + 944 = 3018.13; min(48 + 12, 48) − 3 = 45; 3018.13 / 45 = 67.069 → 67.07. The 85898edb payment PMT-4407155 is 67.07. | OK |
| T1-7 enrollment 83759b05 | 2025-07-20 | 3236.50 (unchanged) | Unchanged. | OK |
| T1-8..T1-10 installments #5–#7 | 08-15..10-15 | 140.63 each | 3018.13 − 67.07 + 3236.50 = 6187.56; 48 − 4 = 44; 6187.56 / 44 = 140.626 → 140.63. The 85898edb payments PMT-4408156, PMT-4409157 and PMT-4410158 are 140.63. | OK |
| P1 monthly_payment_usd | — | 140.63 | Equals the last recompute. | OK |
| P1 plan_balance | 2025-11-18 | 5765.67 | 6392.90 enrolled − 627.23 paid = 5765.67. Also equals 1585.17 + 944 + 3236.50. 85898edb: 2212.40 − 627.23 = 1585.17, matching the account. | OK |

Other round-4 changes outside the plan rows have no bearing on any plan rule:
- t0: GFE 03633924 was re-dated from 04-14 to 04-10, and the c88c4cb6 charges moved to 06-28.
- t1: a 352.75 uninsured discount was posted on the unenrolled account bd2c77fb on 11-17, and the 6d6927ad/GFE service code changed from 72148 to 72141.

Each plan installment still has exactly one PAYMENT_PLAN_INSTALLMENT account payment with the same date, amount and reference, all on the account with the oldest service start. No allocation exceeds that account's enrolled amount.

**Round 4 MISS list: none.** Doubtful items D1–D3 carry over unchanged. D1 (task 0 hardship entry rests on an unrecorded income loss) would now affect 482.17, the installment the FA plan-burden factor reads (482.17 against 112800 / 12 = 9400.00, 5.13%).
