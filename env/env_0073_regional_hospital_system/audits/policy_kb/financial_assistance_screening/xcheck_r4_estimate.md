# Seed-row legality cross-check: Good Faith & Price Estimates (env_0073)

Criterion: the 50 published docs in `env/env_0073_regional_hospital_system/docs/estimate/*.json` (title and content only). I used the published uninsured-discount schedule in `docs/encounter/uninsured_discount_schedule_a3f8644e.json` only to resolve the "uninsured discount of the account type" that the estimate docs name. Business days are Mon-Fri excluding federal holidays (2025: Jun 19, Sep 1, Oct 13, and so on).

Doc short names:
- TYPES = estimate_types_and_coverage_answers_1c9b00f6
- ISSUE = good_faith_estimate_issuance_fdb80d1c
- BD = estimate_business_day_deadlines_147803b2
- CONTENT = estimate_content_and_expected_charges_767a267c
- FORM = estimate_line_content_standards_5d0b0a95
- VALID = estimate_validity_and_variance_thresholds_1166b3ac
- PERPT = estimates_per_patient_and_versions_2116201a
- INS = insured_estimates_and_variance_review_71909aad
- PPDR = patient_provider_dispute_eligibility_e86e164e
- PPDRF = patient_provider_dispute_figures_3dbb5a7a
- PKG = self_pay_package_price_list_921930c6
- TERMS = self_pay_package_terms_359ad4b7
- DEP = package_deposit_and_cancellation_schedule_834bade2
- APPLY = deposit_application_at_final_bill_ebefffe4
- UDS = encounter/uninsured_discount_schedule_a3f8644e (figure only)

## (1) Every row

"Lead" is the business days from the scheduling date to the service date. "Issue BD" is the business days from the scheduling date (or request) to the issue date.

| # | Task | Id prefix | Row type | Date | Amount / key fields | Verdict | Docs |
|---|---|---|---|---|---|---|---|
| 1 | t0 | 03633924 | estimate | req/sched 2025-04-09, svc 04-21, issued 04-14, closed 09-05 | Recurring Course, UNINSURED, 93798, total 1386.00, initial bill 05-08 (= acct first statement 05-08), lead 8 BD, issue 3 BD after scheduling | **MISS** (late issue) | BD, ISSUE |
| 2 | t0 | 05b3f0db (est 03633924) | line | 2025-04-14 | CONVENING_FACILITY Neenah, 93798, 1386.00 = 12 x 210.00 x (1-0.45). Recurring Outpatient Therapy acct, 45% | OK | CONTENT, FORM, UDS |
| 3 | t0 | ad051669 | estimate | req/sched 2025-06-06, svc 06-24, issued 06-11 | Procedure w/ Co-Providers, UNINSURED, 93458, total 14440.00, in_dispute filed 10-14, initial bill 07-02 (= first stmt), lead 11 BD (Jun 19 holiday), issue 3 BD | OK | TYPES, BD, ISSUE, CONTENT, PPDR, PPDRF, VALID |
| 4 | t0 | ad0274cf (est ad051669) | line | 2025-06-11 | CONVENING_FACILITY Appleton, 93458, 12500.00 (gross 25000 less 50% Outpatient Surgery discount; gross of an expected charge isn't published, so it can't be recomputed) | OK | CONTENT, FORM |
| 5 | t0 | cec76499 (est ad051669) | line | 2025-06-11 | CONVENING_PROFESSIONAL RMG, 99152, 400.00 (= 800 x 0.50) | OK | CONTENT, FORM |
| 6 | t0 | 6efcc038 (est ad051669) | line | 2025-06-11 | CO_PROVIDER_ANESTHESIA, 01920, 1180.00 (role allowed on this type) | OK | FORM, CONTENT |
| 7 | t0 | 49cc3e7d (est ad051669) | line | 2025-06-11 | CO_PROVIDER_RADIOLOGY, 93458, 360.00 (role allowed; same code as the facility line but a different role, so it is a separate line) | OK | FORM, CONTENT |
| 8 | t0 | 36293d8e | estimate | req 2025-09-12 (unscheduled), sched 09-15, svc 10-18, issued 09-17 | Imaging package, SELF_PAY_ELECTED, 72148, total 895.00, deposit_held 895.00, service_completed, no initial bill (acct pending_billing), issue 2 BD after scheduling / 3 BD after request, validity 31 of 90 d | OK (status note in doubtful D3) | TYPES, BD, PKG, TERMS, DEP, VALID |
| 9 | t0 | 452c5ca1 (est 36293d8e) | line | 2025-09-17 | CONVENING_FACILITY Grand Chute, 72148, 895.00 = package price for 72148 | OK | PKG, CONTENT |
| 10 | t0 | edf620c8 (est 36293d8e) | deposit collected | 2025-09-15 | INITIAL_DEPOSIT 895.00 = 100% x 895.00 at scheduling date; not applied (no final bill yet), so held 895 | OK | TERMS Art.2, DEP, APPLY |
| 11 | t0 | bf4424a0 | estimate | req/sched 2025-09-22, svc 09-30, issued 09-24 | Insured OOP, INSURED, 93306, total 207.10, service_completed, no initial bill (acct insurance_pending), issued 2 BD after request, validity 6 of 30 d | OK (status note in doubtful D3) | TYPES, BD, ISSUE, VALID, INS |
| 12 | t0 | 894473bf (est bf4424a0) | line | 2025-09-24 | CONVENING_FACILITY Appleton, 93306, 207.10 (contracted rate on remaining benefits; contracted rates and benefits aren't published, so it can't be recomputed) | OK | CONTENT, FORM |
| 13 | t0 | 513bffcc | estimate | req/sched 2025-09-29, svc 10-06, issued 09-30 | Recurring Course, SELF_PAY_ELECTED, 93798, total 1386.00, issued (course in progress, 5 visits charged), lead 5 BD, issue 1 BD | OK (see doubtful D4) | BD, ISSUE, VALID, PERPT |
| 14 | t0 | eee79a47 (est 513bffcc) | line | 2025-09-30 | CONVENING_FACILITY Neenah, 93798, 1386.00 = 12 x 210 x 0.55 (45% Recurring Therapy discount) | OK | CONTENT, UDS |
| 15 | t0 | d73f8b40 | estimate | req/sched 2025-10-10 (portal), svc 11-04, issued 10-14 | Insured OOP, INSURED, 93351, total 386.00, issued, no encounter; issued 1 BD after request (Oct 13 holiday), validity 21 of 30 d | OK | BD, ISSUE, VALID |
| 16 | t0 | ae0fe8cc (est d73f8b40) | line | 2025-10-14 | CONVENING_FACILITY Appleton, 93351, 386.00 (contracted basis, can't be recomputed) | OK | CONTENT |
| 17 | t0 | e9dc397e | estimate | req/sched 2025-10-13, svc 10-20, issued 10-14 | Single Scheduled Service, SELF_PAY_ELECTED, 93224 (not on any package schedule), total 441.00, service_completed, no initial bill (acct pending_billing), lead 5 BD, issue 1 BD | OK (status note in doubtful D3) | TYPES, BD, VALID |
| 18 | t0 | 47da6dd1 (est e9dc397e) | line | 2025-10-14 | CONVENING_FACILITY Appleton, 93224, 441.00 = 980.00 x (1-0.55); Outpatient Diagnostic Imaging & Lab, medically necessary, 55% | OK | CONTENT, UDS |
| 19 | t1 | 6e5edc50 | estimate | req/sched 2025-09-02, svc 09-22, issued 09-04 | **Single Scheduled Service**, SELF_PAY_ELECTED, **72148**, total 1800.00, in_dispute filed 09-29, initial bill 09-26 (= acct final bill; acct has no first statement), lead 14 BD, issue 2 BD | **MISS** (estimate type) | TYPES, PKG, FORM |
| 20 | t1 | 481ab021 (est 6e5edc50) | line | 2025-09-04 | CONVENING_FACILITY Grand Chute, 72148, 1800.00 (gross-less-discount basis: 2400 x 0.75; package price for 72148 is 895.00) | **MISS** (follows from #19: wrong basis for a package-schedule code) | CONTENT, PKG, FORM |

Checks that pass on every estimate:
- Totals equal the sum of the current-version (v1) lines.
- Line counts are under the type maximum.
- Co-provider roles are allowed for the type.
- Non-package types collect no deposit.
- Every service falls inside its validity window.
- The convening-facility provider name matches the linked account's facility.

Dispute checks:
- **t0 ad051669:** Riverbend billed = 26800.00 - 13400.00 = 13400.00. Expected = 12500 + 400 = 12900.00. The excess of 500.00 meets the 400.00 threshold. The dispute was filed on day 104 of 120 after 07-02. Coverage is UNINSURED (eligible). The account holds GFE_DISPUTE_PENDING from 10-14, and the plan balance was withdrawn 10-14. OK.
- **t1 6e5edc50:** Billed = 3120.00 - 780.00 (25% elective discount) = 2340.00 against 1800.00 expected. The excess of 540.00 meets the threshold. Filed on day 3. Coverage is SELF_PAY_ELECTED (eligible). Hold GFE_DISPUTE_PENDING from 09-29. OK on its own terms.

## (2) MISS list

### M1. t0 estimate 03633924 (Recurring Course of Care) was issued late
- **Published rule (BD):** Under "Furnished within, after the scheduling date, when scheduled at least 3 but fewer than 10 business days ahead", the Recurring Course row reads **1**. A business day is "Monday through Friday, excluding federal holidays."
- **Published rule (ISSUE §3):** "within the type's furnishing period for services scheduled at least the minimum scheduling lead but fewer than 10 business days ahead, counted after the scheduling date".
- **What the row shows:** Scheduled Wed 2025-04-09 for Mon 2025-04-21, which is 8 business days ahead (12 calendar days). The estimate was due by Thu 04-10 but was issued Mon 04-14, 3 business days after scheduling. That timing fits the 10+ BD column, so the seed apparently counted calendar days.
- **Effect on an assistance figure:** No. The assistance computations don't read the issue date. Variant, status, account, lines, total and initial bill date are unaffected.

### M2. t1 estimate 6e5edc50 (and its line 481ab021) has the wrong estimate type for a package-schedule code
- **Published rule (TYPES):** "The type is fixed by the coverage answer the patient gives at the coverage inquiry and by the scope of the service being estimated." The Imaging & Diagnostics package scope is "a service code on the imaging package schedule", and it admits "uninsured; self-pay elected". The doc's worked example reads: "an uninsured patient booking a screening study whose code is on the imaging package schedule holds a Riverbend Self-Pay Package Price - Imaging & Diagnostics".
- **Published rule (PKG):** Package type Imaging & Diagnostics, service code **72148**, package price **895.00**.
- **Published rule (CONTENT):** "on package types, the package price for the service code from the package price schedule".
- **What the row shows:** A self-pay-elected patient booked 72148 (on the imaging schedule). The estimate is typed "Self-Pay Good Faith Estimate - Single Scheduled Service" with a gross-less-discount line of 1800.00. Under the published rules it would be an Imaging package at 895.00, with a 100% deposit at scheduling (DEP/TERMS Art.2). It would be binding (PKG: "Estimate limits what the patient may be billed: yes"), and the account would be priced by package adjustment rather than the 780.00 uninsured discount (TERMS Art.5).
- **Cross-check in the other world:** In t0 the same code 72148 under SELF_PAY_ELECTED on 2025-09-12 is correctly typed Imaging package at 895.00.
- **Effect on an assistance figure:** Yes, potentially. The assistance computations read the estimate variant, the convening facility line, the package price (facility + professional line carrying the principal code), the dispute status and the billed-vs-expected excess. Under the published type, the variant is a package and the expected/package price is 895.00 rather than 1800.00. The billed charge would be the package price (895.00), so the 540.00 excess and the in_dispute status would not arise as seeded.
- **Possible counter-reading:** The Single Scheduled Service scope ("one scheduled item or service furnished by Riverbend alone") also literally covers 72148. However, the doc's own example resolves that overlap in favour of the package type. This is why I list it as a MISS rather than doubtful.

## Doubtful (not a miss)

- **D1. t1 6e5edc50 initial_bill_date 2025-09-26 is the account's final_bill_date; the account has no first statement.** In t0 the convention is different: 03633924 and ad051669 carry the account's first statement date (05-08 and 07-02), not the final bill date (05-05 and 06-29). The estimate docs say only "the date on the initial bill" and "the initial bill date recorded on the estimate", and never define the initial bill as the first statement or the final bill. The encounter doc says the self-pay final bill "drops to the patient", which supports either reading.
  - If the first-statement reading is intended, t1 has no initial bill, and the in_dispute row has no dated initial bill to count from. Under the assistance supplement, "no initial bill date recorded" means nothing is taken off.
  - The two readings also move the t0 ad051669 120-day boundary from 10-27 (final bill) to 10-30 (first statement). That could change a figure only if a signing day falls between 10-28 and 10-30.
- **D2. t0 03633924 closed_date 2025-09-05.** INS says it "closes once the dispute initiation window in days has passed after the initial bill date". PPDR says day 120 (09-05, counted from 05-08) is itself timely. On a strict reading the window has passed only from 09-06, so the close is one day early. Read as "initial bill date + 120 days", 09-05 is right. This has no assistance effect: the estimate is closed at the frozen time either way.
- **D3. service_completed with no initial_bill_date on t0 36293d8e, bf4424a0 and e9dc397e.**
  - The linked accounts are pending_billing (two) or insurance_pending (one), with no final bill or statement.
  - The charter lifecycle says service_completed is reached when "the initial bill is dated". That lifecycle isn't stated in any published estimate doc, so this is not a published-rule miss.
  - Effect: the assistance computations read status and initial bill date. A reader holding the charter's lifecycle would expect these three still at "issued".
- **D4. t0 513bffcc is a second recurring-course estimate for 93798 opened while 03633924's 12-month span (issued 2025-04-14) had not run out.** The first course delivered 8 of the 12 visits it was estimated for (04-21 to 04-30). PERPT says "a change to an already estimated service is a new version of the same estimate, never a second estimate", and that a new estimate is opened when a course "runs past" twelve months.
  - The October course is a separate new booking under a different coverage answer (SELF_PAY_ELECTED vs UNINSURED), with a new account. 03633924 was already closed 09-05, so a new estimate is defensible.
  - Flagged only because the docs don't say whether a resumed course counts as a new course.
- **D5. Expected-charge bases that can be partly but not fully recomputed.**
  - **ad051669:** facility 12500.00 implies expected gross 25000 against billed 24860 (93458 21400 + C1769 3460). Professional 400.00 on code 99152 implies gross 800, which matches the account's 0960 professional charge of 800.00 posted under 93458, while the account's 99152 charge is 1140.00 (rev 0710).
  - **t1 6e5edc50:** 1800.00 implies expected gross 2400 against billed 3120.
  - Expected gross isn't published, and the docs anticipate billed differing from expected (that is what the dispute process is for), so neither is a miss.
  - Insured lines 207.10 and 386.00 rest on contracted rates and benefits that aren't published, so they can't be checked.

## Round 4 re-check

Inputs: t0_db_r4.json and t1_db_r4.json, each compared field by field with t0_db.json and t1_db.json. The criterion and hard rules are the same as above.

| Task | Row | Change | Verdict | Basis |
|---|---|---|---|---|
| t0 | estimate 03633924 (Recurring Course) | issued_date 04-14 → 2025-04-10 | OK (M1 cleared) | BD: the "at least 3 but fewer than 10 business days ahead" column reads **1** for the Recurring Course. The scheduling date is Wed 04-09 and the service is 04-21, 8 business days ahead, so the estimate was due by Thu 04-10. Issued 04-10 is 1 business day after scheduling. Validity holds: the service falls 11 of 365 days after issue. Total, closing date and initial bill are unchanged. |
| t0 | line 05b3f0db | posting_date → 2025-04-10 | OK | It now matches the issue date of version 1. Amount 1386.00 = 12 × 210 × (1 − 45%) is unchanged. |
| t1 | estimate 6e5edc50 | primary_service_code 72148 → 72141 | OK (M2 cleared) | PKG: 72141 is on no package schedule. The imaging codes are 70553, 72148, 74177, 77067 and 93306; the surgery and maternity codes differ too. No published doc mentions 72141. So TYPES assigns a self-pay-elected single service furnished by Riverbend alone to "Self-Pay Good Faith Estimate - Single Scheduled Service", as seeded. Timing: lead 14 BD, issued 2 BD after scheduling, within the limit of 3. Validity: 18 of 90 days. |
| t1 | line 481ab021 | service_code → 72141 | OK | CONTENT/FORM: the basis is gross less the uninsured discount of the account type. The account is Outpatient Diagnostic Imaging & Lab, elective non-covered, so the discount is 25% (UDS), the same rate the account's 780.00 = 25% × 3120 discount uses. 1800.00 equals 2400 expected gross × 0.75. Expected gross isn't published, so this is consistent but can't be recomputed exactly. One CONVENING_FACILITY line at Grand Chute, no co-provider lines, total = sum of lines. |
| t1 | linked account charge 25ea6449 | cdm 6100148 → 6100141, cpt 72148 → 72141, amount 3120.00 kept | OK | It now matches the estimate code. The final bill (3120.00), the uninsured discount (780.00), the 2340.00 balance and the GFE_DISPUTE_PENDING hold from 09-29 are all unchanged. |
| t1 | in_dispute status of 6e5edc50 | (re-tested) | OK | PPDR/PPDRF: billed is the self-pay final bill less the uninsured discount, 3120.00 − 780.00 = 2340.00. Expected is the facility + professional lines, 1800.00. The excess of 540.00 is at least 400.00. Initiated 09-29, which is day 3 after the 09-26 initial bill (≤ 120). Coverage SELF_PAY_ELECTED is eligible. The dispute hold reason is present. |

**Collateral check.** No other estimate row or estimate transaction changed in either world. The linked accounts of all other estimates are unchanged, and so is the plan withdrawal of 13400.00 for fa2bc102.

The other r4 changes all sit on accounts that no estimate links to:
- t0: 8bdb031d, b55d0d0a and c88c4cb6 got new discount postings, date shifts and balance changes.
- t1: 15c52208, bd2c77fb and 85898edb got new discounts and balance changes.
- The plan installment amounts in both worlds also changed.

None of these touch an estimate rule, so the rework broke nothing in the estimate rows.

**Doubtful items after round 4.**
- D1 still stands. The t1 initial_bill_date of 09-26 is the final bill date, and the account still has no first statement date, while t0 uses first-statement dates.
- D2 to D4 are unchanged.
- In D5, the t1 figure now reads 72141: 1800.00 implies a 2400 expected gross against 3120 billed. It is still not determinable.
- No new MISS.
