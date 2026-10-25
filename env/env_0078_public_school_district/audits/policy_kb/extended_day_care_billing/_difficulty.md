# KB-layer audit — extended_day_care_billing (product care), env_0078

## revision_1 (2026-10-25)

### Entry conditions (cited from /tmp/erl0078_coord/kb_snapshot.sh, run at entry and again at close; output identical)
- Policy-side verdict: `VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN` (audits/policy_task/extended_day_care_billing/_difficulty.md, last line).
- `$ check_docs.py care => DOCS OK`
- `$ check_traceability.py extended_day_care_billing => TRACEABILITY OK  (misses listed: 0; non-unlock misses: 0)` (the coordinator's run; I did not run it).
- Instantiation gates 7/7: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Source hashes `68b91fbd6987 388049485508 c2efb33741a0 a1f4401d7994`. Runtime views 0 `fc0b9522d83f4bd9`, 1 `bfb87a3078de517d`. docs/care has 51 files (concatenated sha 4cd1528c3ccaeffd).
- DB access: tool-shaped only (db_query.py). Both blind audits are blind on the DB side. Contamination: none.

### Per-task verdicts
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Scored values (blind = GT) |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | 137.50 / 26.88 / 32.50 / 171.28 |
| 1 | PASS | PASS | PASS | 24.00 / 27.00 |

### Open question judged: the 12-month returned-payment look-back, "counted back to the same day of the month"
Where it is used: three factors (returned_payment_late_addition, plan_returned_payment_rule, arrangement_returned_payment_term) and the base measure care_msr_returned_payments_lookback (certified funds).
- **Rule:** "in the returned_months months before the day of the payment" (or "before the day the fee posts"), "counted back to the same day of the month". The base measure reads "calendar months ending on the payment date, counted back to the same day of the month".
- **Docs:** the same words, verbatim, in payment_plan_returned_payment_rule, installment_returned_payment_term, returned_payment_late_fee_addition and payment_methods_and_returned_payments. The examples settle only interior points ("March 19 of the previous year" inside for a March 18 posting; February of the previous year outside; 13 months back outside). Neither boundary day is closed.
- **Compute:** check_compute `_within` is `0 <= MONTHS(posted_date, NOW) < 12`. It handles the two boundary days as follows:
  - **Start day: excluded.** For NOW 2026-11-12, a return posted 2025-11-12 gives MONTHS 12, so it is outside. 2025-11-13 is inside.
  - **Payment or posting day: included.** A return posted on NOW gives MONTHS 0, so it is counted.
- **Judgement:** rule, docs and compute do not settle the boundary day the same way.
  - The rule and docs agree with each other: they are word for word the same, and both leave the start day undetermined. A natural reading of "counted back to the same day" counts 2025-11-12, which compute excludes.
  - On the end day, compute counts what the extended rules' "before the day of the payment / the day the fee posts" literally excludes. The base measure's "ending on the payment date" does match compute.
  - The end-day case can happen in practice for the late-fee addition. A draft returned on the 11th, the same day a late fee posts under the base offset (due day 10 + 1), would be counted by compute and excluded by the rule.
  - This is a source-side rule-vs-compute edge (XF B1/B3), not a KB defect. The renderer must not close what the source leaves open. Once the source settles it, the settled sentence must be carried.
  - Neither task world reaches it. Task 0's return (2026-10-09) lies 34 days before 2026-11-12. Task 1's return (2025-11-10) lies about 9 months before 2026-08-04. No scored value moves.

### KB defects (renderer's to fix)
None.

### Source-side items (instantiator's to fix)
- **SRC-1 (XF B1/B3, boundary-day edge; three factors in three policies):** see above. The rule sentences and ladders of returned_payment_late_addition, plan_returned_payment_rule and arrangement_returned_payment_term do not state whether a return dated on the same day of the month 12 months back is inside the window. Their "before the day of the payment / the day the fee posts" contradicts compute, which counts a return posted on that day itself. The rule must state both ends, and compute must match. The base measure wording is BLUEPRINT-KNOWN base text: it matches compute on the end day, but it too leaves the start day open.

### Cross-product rows
- meals (published): task 0 has two active Reduced-Price Meal Status accounts, effective 2026-07-15 = the application determination date ("takes effect on its determination date"). Task 1 has Free Meal Status (Prior-Year Carryover), effective 2026-07-01, read on 2026-08-04, before the last carryover operating day 2026-09-23. The meal_status_schedule gives benefit levels reduced / free. No conflict with the published meals docs.
- enroll (Student Enrollment, Transfers and Pre-Kindergarten Admissions; not published in docs/): **CONDITIONAL**, to be re-judged once enroll is published. Affected:
  - Task 0: Chidi's 2026-27 Attendance Zone record, KG, enrolled, read by grade_band_minute_rate and grade_band_day_supplement.
  - Task 1: Elias's 2025-26 record, year_completed with withdrawal_date 2026-05-28, read by withdrawal_proration_convention. Elias's 2026-27 Non-Resident Transfer record, enrolled, read by arrangement_residence_term.
- care rows themselves reproduce under the care base rules:
  - Chidi's tuition is 176.00 x 0.75 x 0.90 = 118.80 at sibling position 2. Amara's is 248.00 x 0.75 = 186.00.
  - Prior fees reproduce: late pickup 36.25 (2026-10-07), late payment fees 11.88 (2026-09) and 21.88 (2026-10), day fees 23.50.
  - Task 1: the late fees of 15.00 and the 93.00 payment allocation reproduce.

### Observations (not RED)
- O-1: booked_day_fee_posting "Booking conditions" drops the 2026-27 apposition ("which ... is the day rate the schedule starts from") of the three day-fee replaced_by sentences. It is entailed via booked_day_rate (fee = day rate; the rate part acts on the day rate first).
- O-2: late_pickup_repeat_rate example "The written warning is issued on that date" dates the warning in a hypothetical, which the base leaves undated. No scored effect.
- O-3: late_pickup_minute_billing boundary row 46 -> 60 coincides with task 0's minutes. It is a natural boundary in a full rule table.
- O-4 (source, unreached): care_ext_booked_day_fee_schedule compute does not re-test the base booking gates (active status, holiday_camp_access, drop_in_days_allowed). care_ext_late_payment_fee_schedule `earlier_fees` counts all late-fee rows, not only "earlier billing months". Neither is engaged in any priced world of this suite.
- R6-WAIVED (policy layer): returned_payment_late_addition. I checked its document for KB defects and found none.

### Closing checklist
- Audit files: runtime_context/extended_day_care_billing/{0,1}.md and policy_kb/extended_day_care_billing/{0,1}.md, one per task. Blind answers were frozen before the reveal. Every comparison section carries PASS.
- Every extended-policy atom of the six policies (rules, 10 overwrites, 23 factor ladders, 6 baselines, 6 tool contracts) is entailed by docs/care, and the retired surface is correctly marked. The 4 prerequisite sentences stand verbatim, in their declared form, in the blocked hub only. No tool, route or aggregated chain appears beyond them.
- check_docs and check_traceability lines were re-cited from the closing snapshot run: DOCS OK; TRACEABILITY OK (0 misses).
- Coverage gap stated: cross-product contradictions with the unpublished enroll corpus are outside this audit (CONDITIONAL above).

KB-VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=SRC-1

## revision_2 (2026-10-25) — re-audit after REWORK round 6 (policy revision_6 CLEAN) and RENDER round 3

### Entry snapshot (kb_snapshot.sh run by me; scratch /tmp/kbaudit_extended_day_care_billing_0078/snapshot_r2.txt)
- `$ check_docs.py care => DOCS OK`
- `$ check_traceability.py extended_day_care_billing => TRACEABILITY OK  (misses listed: 0; non-unlock misses: 0)` (the coordinator's run; I did not run it).
- Gates 7/7: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK.
- Source sha: revision_1 had `68b91fbd6987 388049485508 c2efb33741a0 a1f4401d7994`; now `8e283b9ed3a5 388049485508 e06178ffb3b3 334e091e1ac4`. The yaml and both task JSONs changed. task_tools is unchanged.
- Runtime views unchanged: 0 `fc0b9522d83f4bd9`, 1 `bfb87a3078de517d`. docs/care has 51 files (concatenated sha 6605c68d47748c45).
- Published products now: care, device, enroll, meals, music, transport.

### SRC-1 closure check: closed, and consistent across rule, compute and docs
- **Rule.** All three factor rules, their compute_basis quotes and their ladder `when` text now read: "the return posting after the same day of the month returned_months months before the day the fee posts / of the payment (the last day of that month when it has no such day) and on or before that day".
- **Compute.** Unchanged, `0 <= MONTHS(posted_date, NOW) < 12`. Probes:
  - start day out, next day in;
  - the payment or posting day itself in, the next day out;
  - 29 Feb 2028 against 28 Feb 2027 out, 1 Mar 2027 in;
  - month-ends 03-31 and 02-28 behave the same way.
  This is exactly the stated window.
- **Docs.** The three factor documents carry the new sentence equivalently. Their boundary examples (same day prior year: no; next day: yes; posting or payment day: yes; leap-day fallback) all agree with compute.
- Scored values and worlds are unchanged: GT 137.50 / 26.88 / 32.50 / 171.28 and 24.00 / 27.00, same baselines, DB returns identical.
- The base certified-funds measure (care_msr_returned_payments_lookback, rendered in payment_methods_and_returned_payments) keeps "ending on the payment date, counted back to the same day of the month". This is base text, rendered verbatim and unchanged; it is BLUEPRINT-KNOWN and not part of SRC-1.

### Regression check
- Docs: 48 of 51 documents are byte-identical in title and content. The three changed documents changed only in their look-back sentences and examples.
- Source: the six extended rules, params, overwrites and the 4 prerequisite sentences are identical to revision_1 apart from the SRC-1 phrases. The base prefix still equals the blueprint.
- No new KB defect and no regression. Observations O-1 to O-4 are unchanged; the source chose to keep them, as recorded in the round-6 worklog claims.

### CONDITIONAL items re-judged (enroll now published)
- Task 0, Chidi's 2026-27 Attendance Zone KG record and 2025-26 PK4 year_completed record: consistent with the enroll docs (admission, residency, close of year). Closed.
- Task 1, Elias's 2025-26 Attendance Zone record (year_completed, closing date 2026-05-28): consistent. Closed.
- Task 1, Elias's 2026-27 Non-Resident Transfer record: consistent with its type's admission and document rules. **But the approved non-resident transfer request it rests on is not producible** under the published enroll rules → **SRC-2**.

### KB defects (renderer's to fix)
None.

### Source-side items (instantiator's to fix)
- SRC-1: **closed** (see above).
- **SRC-2 (XF E1 / F3, cross-product seed realism; task 1; factor arrangement_residence_term):** the seeded request does not fit the published Non-Resident Transfer calendar.
  - Seeded request 3599d17c…: non_resident, for 2026-27, created_at 2026-05-04, decision_date 2026-06-18, status approved.
  - transfer_request_calendar_and_placement_terms: Non-Resident Transfer window 01-11 to 02-26, decisions issued by 04-16, outside-window requests not considered ("no").
  - transfer_and_choice_requests_and_placement_acceptance: "A request filed outside the window is considered for the current school year only when the type accepts mid-year requests".
  - The approved request, and the 2026-27 Non-Resident Transfer enrollment that rests on it, is therefore a history the owning product's published rules do not produce.
  - The scored first installment depends on it: the record gives -1 installment and 27.00, while no enrolled record would give -2, count 1 and 39.00.

KB-VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=SRC-2

## revision_3 (2026-10-25) — seed-only re-audit after REWORK round 7 (policy revision_7 CLEAN)

### Entry snapshot (kb_snapshot.sh run by me; /tmp/kbaudit_extended_day_care_billing_0078/snapshot_r3.txt)
- `$ check_docs.py care => DOCS OK`
- `$ check_traceability.py extended_day_care_billing => TRACEABILITY OK  (misses listed: 0; non-unlock misses: 0)` (the coordinator's run; I did not run it).
- Gates 7/7 OK.
- Source sha `8e283b9ed3a5 388049485508 aa2d94ded9c7 2394261b6c88`. The yaml and task_tools are identical to revision_2; only the two task JSONs changed.
- Seeds: task 0 initial_state sha unchanged (be631c8da4dd); task 1 changed (1ad4cef7f5d4 -> 9054015da8a1).
- Runtime views: 0 unchanged, 1 `64a42e271c56b464` (persona only). docs/care unchanged (6605c68d47748c45).
- Published products: activity, care, device, enroll, meals, music, transport.

### SRC-2 closure: closed
The task 1 transfer request 3599d17c… (non_resident, 2026-27, Cypress Hollow) is now created 2026-01-20 and decided (approved) 2026-04-14. Checked against the published docs/enroll:
- **Window:** transfer_request_calendar_and_placement_terms puts the Non-Resident Transfer window at 01-11 to 02-26, closing day included. 2026-01-20 is inside.
- **Decision date:** decisions on window requests are issued by 04-16. 2026-04-14 meets that.
- **Acceptance:** the acceptance period is 10 days with the decision date as day 0. The 2026-27 record's registration_date 2026-04-20 is day 6.
- **Campus:** enrollment_type_admission_schedule closes only Live Oak Elementary and Calloway Creek High School to non-resident placements, so Cypress Hollow is open.
- **Admission:** the type admits a household with no in-district residence and an approved non-resident request on file. The profile has in_district_residence False.
- **Record:** the campus equals the requested campus, approved_transfer_request_id is recorded, and transfer_effective_date 2026-08-12 is the first day of school. No residency proof is required for this type (registration_document_deadlines), so an empty residency_verified_date is right, and a returning student needs no birth certificate.
- **Single-year term:** the placement must be renewed for every school year, which fits a request for 2026-27 alone.
- **Persona:** "moved ... in January ... applied for a transfer that winter" is consistent and states nothing a rule decides.
- **Score:** the residence-term tier (Non-Resident Transfer, -1) now rests on a producible history. The scored 27.00 is unchanged.

### Exhaustive cross-product pass (every other-category row both tasks seed; all products published)
Seeded tables:
- Task 0: customers 1, students 2, enrollments 3, meal_accounts 2, meal_benefit_applications 1, care_* rows.
- Task 1: customers 1, students 1, transfer_requests 1, enrollments 2, meal_accounts 1, meal_benefit_applications 1, care_* rows.
- Neither task seeds any row of transport, device, music or activity.

| # | Task | Row | Owning docs checked | Result |
|---|---|---|---|---|
| 1 | 0 | enrollment Chidi 2025-26 Pre-Kindergarten (State-Eligible), PK4, Live Oak, year_completed, closing 2026-05-28, basis free_or_reduced_meals | prekindergarten_admission_and_eligibility_bases, prekindergarten_age_and_eligibility_schedule, withdrawal_from_the_district_and_year_end | consistent (DOB 2021-05-14 -> 4 on 1 Sept 2025; year-end completion carries the closing date and no leaver reason) |
| 2 | 0 | enrollment Chidi 2026-27 Attendance Zone, KG, Live Oak, enrolled, registered 2026-04-15, residency verified 2026-04-20, returning | enrollment_type_admission_schedule, registration_residency_and_required_documents, registration_document_deadlines | consistent (zoned campus Live Oak, in-district profile, residency re-verified each year) |
| 3 | 0 | enrollment Amara 2026-27 Attendance Zone, 04, Live Oak, enrolled | same | consistent |
| 4 | 0 | meal application 2026-27 household_income, submitted 2026-07-09, approved_reduced 2026-07-15, not_selected | meal_status_schedule, application_and_verification_calendar | consistent (determined within 10 operating days; verification sample not before 10-01) |
| 5 | 0 | meal accounts Chidi + Amara, Reduced-Price Meal Status, active, effective 2026-07-15, same application | meal_status_schedule (§1 benefit level reduced; §2 a household application reaches all students; §3 effective on the determination date) | consistent |
| 6 | 1 | transfer request 3599d17c… (re-seeded) | transfer calendar, placement acceptance, type schedule | consistent (SRC-2 closed) |
| 7 | 1 | enrollment Elias 2025-26 Attendance Zone, KG, Cypress Hollow, year_completed, closing 2026-05-28, new_to_district | type schedule, registration docs, year-end | consistent. A move out of the district mid-year does not end the record under any published clause, and year-end completion is right. |
| 8 | 1 | enrollment Elias 2026-27 Non-Resident Transfer, 01, Cypress Hollow, enrolled, registered 2026-04-20 | type schedule, transfer calendar, registration docs | consistent |
| 9 | 1 | meal application 2025-26 household_income, submitted 2025-09-05, approved_free 2025-09-15, not_selected | meal_status_schedule, verification calendar | consistent (6 operating days) |
| 10 | 1 | meal account Elias Free Meal Status (Prior-Year Carryover), active, effective 2026-07-01, Cypress Hollow | meal_status_schedule §1/§3 (carryover of a prior-year free status; lasts through 2026-09-23; school year July 1 to June 30) | consistent on 2026-08-04 |

Accepted residue, not members: the coordinator ruling says rows no gold step reads cannot be seeded under the replay closure.
- No registration-document log rows (enrollment_records_log) exist for rows 2, 3, 7 and 8, although the published rule makes enrolled status rest on logged documents. Task 1's finder returns "No registration document entry found".
- No 2025-26 meal determination exists behind Chidi's PK4 basis free_or_reduced_meals.
- Amara's earlier-year records are not seeded.

Observation, not a member: students.zoned_campus is still "Cypress Hollow Elementary" for task 1's out-of-district household. It is a shared table, and no computation or gold decision reads it.

Members found: **none**.

### KB defects (renderer's to fix)
None. The docs are unchanged, so no regression is possible.

### Source-side items (instantiator's to fix)
- SRC-1: closed (revision_2).
- SRC-2: closed (above).
- No new item.

KB-VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=NONE
