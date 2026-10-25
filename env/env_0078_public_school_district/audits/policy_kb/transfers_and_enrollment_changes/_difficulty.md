# KB-layer audit — transfers_and_enrollment_changes (product enroll) — difficulty close-out

## revision_1 (2026-10-25)
Inputs: coordinator brief /tmp/erl0078_coord/kbaudit.md; entry snapshot `kb_snapshot.sh transfers_and_enrollment_changes enroll` (2026-10-25T01:25:44): `check_docs.py enroll => DOCS OK`; `check_traceability.py transfers_and_enrollment_changes => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)`; EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK; 64 docs; runtime views 0 = 261fce429dab28b7, 1 = b1b423cd1b763fa5. Policy-side verdict: `VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN`. Entry conditions complete. check_traceability not re-run by this auditor (brief); the gate lines above are the record.
Blind phase: frozen to disk before any source read; DB side blind (db_query.py tool-shaped returns only); contamination: none.

## Per-task verdicts
| task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | task |
|---|---|---|---|---|
| 0 (advance payment ← late fee, combined-program credit) | PASS (50.00 / 57.50 / 3,409.00 ach_bank_draft = gold) | PASS | PASS | PASS |
| 1 (first installment ← waiver ← reversal ← eligibility credit) | PASS (261.50 / 35.88 / 19.12 / 310.42 online_card = gold) | RED (K1) | PASS | RED |

## KB defects (renderer's to fix) — complete list
- **K1 — scope rewritten to the current enrollment type (task 1's whole tree).** `prek_tuition_payment_plan` states "The plan applies to a Pre-Kindergarten (Tuition-Based) enrollment of Student Enrollment, Transfers and Pre-Kindergarten Admissions.", a restriction the source rule ("A family may settle the open balance of a Pre-K tuition account …") does not have and that its own closing-account factor contradicts (a plan "on an enrollment whose move to Pre-Kindergarten (State-Eligible) took effect …"; KB `payment_plan_closing_account_down_payment` carries that correctly). The same "On a/a Pre-Kindergarten (Tuition-Based) enrollment/payment plan" label opens the plan's computation and five factor documents, the reversal hub, computation and four factor documents, the waiver hub, computation and four factor documents (source rules carry no type scope), and, more weakly, the five basis-month credit documents. Task 1's enrollment is on record as "Pre-Kindergarten (State-Eligible)" (transfer_effective_date 2027-01-01) when all four writes happen. Full member list and quotations: policy_kb/…/1.md kb_to_source. Not KB-RUNTIME: the blind pass resolved it from the closing-account schedule and the move rule and matched gold.

No other KB defect: every prerequisite sentence (5) verbatim, action form, blocked hub only; every ladder (33 factors) complete in its own document with figures; every baseline and assembly sentence in its computation document; three overwrites retired-and-borne with replaced_by verbatim; tool contracts equal to task_tools.py; no tool name outside its own hub; no scored value, name, campus-date combination or code of either task in any document or unlock schema.

## Source-side items (instantiator's to fix) — complete list from one exhaustive pass over every other-category row the two tasks seed
Rows checked against the owning product's published docs as of each row's date: task 0 — care_enrollments 6963ae45 (Lucia, Pre-K Wraparound, WS-funded, reg 12-09, start 12-16) and 522aa9da (Mateo, After-School 5 Days), care_ledger 15 rows (registration fees 40.00 ×2 with same-day ACH payments; Mateo's 248.00 standard full months Aug–Dec, each paid by the 10th; Lucia's 192.00 = 384.00 × 50 % half-month, standard rate under CCS terms, posted on seat confirmation 12-09); meal_accounts f7a006eb (Lucia, Paid, opened on registration date). Task 1 — meal_accounts cf8b7698 / e24002e7 (Reduced-Price effective 12-17), meal_benefit_applications c84b4e94 (submitted 12-08, approved_reduced 12-17, within 10 operating days, reach all household students), meal_notices ×2 (approval letters 12-17, same day as determination). Pricing, statuses, sibling positions (CCS seat left out of the count), registration-fee cap (80.00 ≤ 100.00) and dates all reproduce. Same-product history also re-derived: every seeded Pre-K late fee (task 0: Oct 40.00, Nov 55.00; task 1: Nov 50.00, Dec 55.00) equals what the published late-fee schedule gives on its posting day.
- **S1 (task 0, care seed / CCS terms).** Lucia's 2026-12 seat charge 192.00 posted 2026-12-09 has no payment and no Workforce Solutions remittance by the care due day (day 10). The care docs as published make a late payment fee due on 2026-12-11 ("When the amounts applied by the due day leave any part of that month's tuition unpaid, one late payment fee still posts the late-fee offset days after the due day"; CCS terms: the household's remainder "is billed, made late and suspended like any other balance"), and none is on the ledger at 2026-12-17. The CCS docs do not say how a not-yet-posted remittance is treated, so either the seed lacks the row or the care charter leaves the pending-remittance case open. No scored read moves (the cap reads only the seat's tuition and remittance rows), but the row would fall inside gold's find_care_ledger(customer_id) read, so the replay-closure residue does not cover it.
- **S2 (task 0, same-product seed).** Mateo's active Creek Kids Club enrollment 522aa9da (read by three scored factors: multi_program_household_cut, creek_kids_children_tier, creek_kids_household_reduction) rests on the care admission rule "Registration … is open to a student whose current district enrollment record is in status enrolled at a campus in the plan's offered campuses", but the household has no enrollment record for Mateo (find_enrollments by customer returns only Lucia's), although the persona calls him "a third grader at Alder Springs". Gold's find_enrollments(customer_id) would return such a row, so it is seedable.

Accepted residue (replay closure, not items): Mateo has no meal account (gold reads Lucia's only); Ivy (task 1) has no enrollment record (gold reads Rowan's by student_id); neither Pre-K enrollment has registration-document rows behind its enrolled status / residency_verified_date (find_enrollment_records_log is not a gold step).

## Observations (no verdict effect)
- O1 (E2 class, below bar): three factor-document examples describe a household shaped like task 0's (Pre-K child in Pre-K Wraparound plus an older child in After-School Care, two active → 10.00 / 5.00 / 10.00): `creek_kids_club_household_size_credit_addition`, `multi_program_household_late_fee_reduction`, `advance_payment_creek_kids_household_reduction`. No row, date, id or amount of the task; only ladder tier values. Coordinator may apply the "combos unlike any task world" bar.
- O2: base example in `prekindergarten_admission_and_eligibility_bases` ("1,150.00 | 50.00 owed") shows 50.00, equal to task 0's scored late fee, for an unrelated quantity (prior-year balance). Coincidental.
- O3: `prek_late_fee_amount_and_billing_month` step 2 reads "That month's due day is day (tuition due day) of the billing month" — placeholder-like wording; meaning intact, figure (5) in the fee schedule.
- O4: `payment_plan_length_schedule` says the count "is set by the open balance" without the "in place of" wording other replacing tiers use; its "less than 500.00 → 2" row restates the baseline, so the replacement reading is unique (source: "is divided into").
- O5 (policy-side, out of both tasks' domain): the source advance-payment rule has no type scope; on an enrollment that has moved to State-Eligible it would still price "months not yet posted" that will never post. The KB's Tuition-Based scoping of the advance happens to avoid that reading. Recorded per Step 4; no KB verdict.
- R6-WAIVED factors (21, per the policy layer): their documents were checked for KB defects; none found beyond K1's label on the task-1 ones.

## Closing checklist
- [x] audit files one-to-one with tasks: runtime_context/…/0.md, 1.md; policy_kb/…/0.md, 1.md (revision_1, no older revision overwritten)
- [x] blind answers frozen before reveal; gt_comparison appended
- [x] every prerequisite sentence verbatim in its blocked policy's documents only; every hop resolvable
- [x] every factor ladder carried in full, findable from record words
- [ ] all three parts PASS for every task — task 1 KB-BIJECTION RED (K1)
- [x] gate lines on record (snapshot above; check_traceability not run by this auditor per brief)

KB-VERDICT revision_1: task0=PASS task1=RED kb=K1 src=S1,S2

## revision_2 (2026-10-25) — re-audit after seed-only rework (round 8, policy revision_8 CLEAN) and RENDER round 4
Snapshot 2026-10-25T01:50:33: DOCS OK; TRACEABILITY OK (misses listed: 0; non-unlock misses: 0) — coordinator line, not re-run here; EXTENDED / TASK TOOL CONTRACT / REPLAY (0.json 34/34, 1.json 19/19) / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; 64 docs (sha256 0c3feb33baac f452cff1522d 728f1bf23a10 4b3110ee7d77); runtime views unchanged. Charter and tools unchanged since the revision_1 reveal (mtimes 01:06 / 23:36).

| round-1 item | status | evidence |
|---|---|---|
| K1 (Tuition-Based scope label on task 1's tree) | closed | plan hub restriction removed; all listed members now "Pre-K tuition account"; only the closing-account tier names the types; 1.md revision_2 |
| S1 (Lucia's 2026-12 seat owed a care late fee) | closed | care payment 192.00 ach 2026-12-10 settles the month by the care due day; nothing owed; cap unchanged |
| S2 (Mateo's care enrollment without a district enrollment) | closed | enrollment eb988618, Attendance Zone, Alder Springs, grade 03, enrolled; care admission rule holds |
| O1–O4 | closed by the re-render (examples, prior-balance figures, due-day wording, plan-length wording) | 0.md / 1.md revision_2 |
| O5 (policy-side, out of domain) | carried | unscoped source advance rule on a moved enrollment |

Task 0 re-derived from the runtime view and db_query.py on the changed seed: 50.00 / 57.50 / 3,409.00 ach_bank_draft = gold (non-blind to GT, disclosed). Task 1 seed unchanged; re-read on the re-rendered corpus: 261.50 / 35.88 / 19.12 / 310.42 online_card = gold. Exhaustive pass over the changed rows (care payment d10e6156; enrollment eb988618): both are states the owning product's published rules produce; the only consequence not seeded (Mateo's meal account from the new_to_district trigger) lies outside the replay closure and touches no scored read — accepted residue. No new defect, no regression (full 64-document diff read; prerequisite sentences, tool-name placement, ladders, baselines, overwrites and tool contracts re-checked).

| task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | task |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

Closing checklist: audit files one-to-one, revision_1 text untouched, revision_2 appended in all four files; every prerequisite sentence verbatim in its blocked hub only; every ladder complete and findable; all three parts PASS for both tasks; gate lines on record.

KB-VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=NONE
