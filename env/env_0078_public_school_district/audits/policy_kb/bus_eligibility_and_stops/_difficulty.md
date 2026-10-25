# KB-layer audit — bus_eligibility_and_stops (product transport, M=2)

## revision_1

### Entry (snapshot by /tmp/erl0078_coord/kb_snapshot.sh, entry 2026-10-25T01:25:41, closing re-run 01:36:11, identical)
- Policy verdict on entry: `VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN` (audits/policy_task/bus_eligibility_and_stops/_difficulty.md).
- `check_docs.py transport => DOCS OK`; `check_traceability.py bus_eligibility_and_stops => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)` (coordinator's run; not re-run by this auditor, per the brief).
- Gates: EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK.
- Source sha256 prefixes: 41fa27e89d6f 4b689506ac3b a262f5f15a52 7d90625340be. docs/transport: 46 files.
- Runtime views: 0.runtime.json 1980524d5baddbd4; 1.runtime.json 0e5247632eb066bb. DB access: db_query.py, tool-shaped (blind on the DB side).
- Blind freeze hashes: runtime_context/…/0.md f76d1914bc512b8c6cdf00199b042dda7422281c8b0e704f38a9c9a9d4a53f5e; 1.md fe4a8c4b88868ca779ea4d70215d074044d4089e555b2febe33a48e45dea343e (both frozen before the reveal at 01:40). contamination_disclosure: none.

### Per-task verdicts
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Task |
|---|---|---|---|---|
| 0 | PASS (183.60 / 3.47 and tree match GT) | PASS | RED — KB-01 | RED |
| 1 | PASS (124.44 / 11.52 and tree match GT) | PASS | PASS | PASS |

### KB defects (renderer's to fix) — complete list
- **KB-01** (KB-EXPLICIT) — docs/transport/adjustment_waiver_share_by_meal_status_adaa36fc.json, the sentence after the tier table: "The tier is the one the meal account holds on the day the adjustment is figured, not the tier it held when the permit fee posted." The rule says only that the share is read from the meal account on the day the adjustment is figured. The "not the tier it held when the permit fee posted" clause contrasts a wrong reading with the correct one inside a factor document. Semantics and solution are unaffected. Fix scope: that clause only; the source's timing sentence must still stand.
- No other KB defect. Prerequisite sentences are verbatim and single-homed (12476623, 23ef23c5). Every ladder tier of the 21 declared factors is exact in its own document. All four retired base clauses are marked retired; in-force clauses are carried. No tool name, route or chain beyond the sentences. No computation-document hint. No scored value in any example or unlock schema.

### Source-side items (instantiator's) — complete list
- None.

### Renderer's note judged (not blocking)
- Note: "the meal-status adjustment's rule says a status 'rests on' whichever meal benefit application the meal account names, while compute also requires the status's source to be a household application" (counted_months and receipt_part test `CPARAM('meals','eligibility_source') == 'household_application'`; the rule's definition is "the meal benefit application the student's meal account names").
- **KB side: no defect.** e4c578d7 and 559b4e89 carry the rule's definition verbatim, which is the faithful side.
- **Source side: no divergence on any producible world**, so no src item:
  - The meals charter (blueprint/products/meals.yaml, meals_benefit_increase) defines meal_benefit_application_id as "Household application the determination rests on; empty for direct certification or a categorical designation". A named application therefore occurs only with a household-application status, Free (HA) or Reduced-Price.
  - The remaining edges are unreachable or owe nothing:
    - a carryover status takes effect before the first school day, so the first month-count row applies and the receipt part fails its "on or after the first school day" test;
    - a reverted Paid status has share 0, so nothing is owed.
  - Both seeded worlds agree under either reading: task 0 has Free (HA) naming a household_income application; task 1 names no application.
- Observation for the coordinator: A4 inline re-read; equivalent.

### Cross-product seeded rows — exhaustive pass (against the owning product's published docs as of each row's date)
- **T0 enroll 32d23f42** (Attendance Zone Enrollment, enrolled, grade 02, Alder Springs, registration 2026-07-13, residency verified 07-15, returning): consistent with enroll/registration_residency_and_required_documents_e1030dce (returning registration re-verifies residency; enrolled after verification). Minor realism observation: DOB 2018-04-19 puts a typical grade at 03 for 2026-27 (late KG entry implied by the meal account opened 2024-08-14). Plausible, and no rule is violated.
- **T0 meals account 4141af32** (Free Meal Status (Household Application), effective 2026-10-01, names 8907394b): consistent with meals/benefit_effective_dates_and_adverse_action_9730cd3f rule (a) (takes effect on the determination date).
- **T0 meals application 8907394b** (household_income, submitted 2026-09-18, approved_free 2026-10-01, not_selected): determined within 10 operating days (application_and_verification_calendar_548f40f7); sample-date consistent. OK.
- **T0 missing row (accepted residue):** rule (a) "an approval letter is sent the same day" implies an approval_letter meal notice dated 2026-10-01, and none is seeded. The persona mentions the letter. No gold step reads meal notices in task 0 (replay-closure residue per the coordinator ruling), and no scored figure depends on it.
- **T1 enroll eefaed10** (grade 04, Live Oak, registration 2026-07-21, enrolled): consistent; grade 04 matches DOB 2016-12-05.
- **T1 care b658886d** (After-School Care (5 Days), active 2026-27, Live Oak, start 2026-08-12, Workforce Solutions CCS):
  - consistent with care/registration_admission_and_waitlist_bf028cd6 (enrolled grade 04 at the campus) and workforce_solutions_child_care_funding_5dbd2112;
  - its billing rows (registration fee, tuition, remittances) are not seeded and no gold step reads them: accepted residue.
- **T1 care 2a2c6700** (After-School Care (3 Days), 2025-26, ended 2026-05-28): prior-year decoy, consistent.
- **T1 meals account 35af749a** (Free Meal Status (Prior-Year Carryover), effective 2026-07-01, no application named): consistent with the meals schedule (carryover rests on the prior-year status; through 2026-09-23). Frozen 2026-09-09 falls before the reversion date.
- **T1 meal notice 9e0ae825** (approval_letter 2025-08-29): prior-year determination letter; consistent (latest notice is not an adverse action, so the decoy holds).
- Transport-own seeded rows: the T0 fee of 231.00 posted 2026-09-04 is reproduced exactly by the published fee schedule and factors (216.00 × (0.9 + 0.1) + 15.00). The T0 payments settle it on 09-15, within 14 days; start_date 09-16. Consistent.

### Measured classes checked
- factor ladder text vs compute: all match.
- two-grouping sentences: none ambiguous; examples fix the held-seat denominator.
- worked examples / unlock schemas reproducing task values: none.
- "owed at once" in other products: no read of this difficulty affected.
- rule-vs-compute at absent-record and boundary edges: no meal account -> zero; no stop -> no held month; no start date -> share one; no received request -> nothing; 10th/20th day and 6/10/14-day boundaries all agree.

### Closing checklist
- Audit files are one-to-one with tasks (runtime_context 0.md and 1.md; policy_kb 0.md and 1.md). The blind answers are frozen, and the gt_comparison sections were appended after the reveal.
- Every normative atom of the four extended policies and the base surface is entailed. Both prerequisite sentences are verbatim on the blocked side only. All factor ladders are complete.
- Closing gates were re-run (snapshot 01:36:11): DOCS OK, TRACEABILITY OK (0 / 0).
- The difficulty does not pass yet: task 0 is held at KB-EXPLICIT RED by KB-01.

KB-VERDICT revision_1: task0=RED task1=PASS kb=KB-01 src=NONE

## revision_2
- Snapshot 2026-10-25T01:43:42 (run by this auditor): DOCS OK; TRACEABILITY OK (misses listed: 0; non-unlock misses: 0) (coordinator's line, not re-run). EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK. Source sha256 prefixes unchanged (41fa27e89d6f 4b689506ac3b a262f5f15a52 7d90625340be); 46 docs. RENDER.log: "RENDER round 3: DOCS OK".
- Change set since revision_1, from a title+content diff against the revision_1 read plus mtimes over all of docs/: 3 transport docs, adaa36fc, bcceb47f and 369c5b34, all inside the renderer's stated sweep. Nothing else changed in any product.
- **KB-01: closed.** The contrast clause was removed, and the timing sentence stays.
- No new defect, no regression: both other deletions keep their meaning by entailment (see 0.md and 1.md revision_2). Corpus re-scan for wrong-reading contrasts: clean.
- Source side: still none. Renderer's note: judgement unchanged (no divergence on any producible world). Cross-product row pass: unchanged (seeds untouched).
- Disclosure: there is no fresh blind answer. The auditor saw GT in revision_1, so revision_2 is a delta check of the revision_1 blind derivation against the changed sentences.
- Per task: task 0 RUNTIME PASS / BIJECTION PASS / EXPLICIT PASS; task 1 PASS / PASS / PASS. The difficulty closes.

KB-VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=NONE
