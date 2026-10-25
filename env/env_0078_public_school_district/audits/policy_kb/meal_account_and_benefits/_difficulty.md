# KB-layer audit — meal_account_and_benefits (product meals) — difficulty close-out

## revision_1 (2026-10-25)

### Entry conditions (cited from `/tmp/erl0078_coord/kb_snapshot.sh meal_account_and_benefits meals`, run 2026-10-25T00:02:55)
- Policy-side verdict: `VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN` (audits/policy_task/meal_account_and_benefits/_difficulty.md).
- `check_docs.py meals => DOCS OK`
- `check_traceability.py meal_account_and_benefits => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)` (the coordinator's post-publication run; not re-run by this auditor, per brief).
- Instantiation gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (0.json 143/143, 1.json 271/271), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK — 7/7.
- Corpus: 74 files in docs/meals (concatenated sha256 a13323b0351e73d3); runtime views 0.runtime.json ae38b758180d28ff, 1.runtime.json 18aaf513afb02295.
- DB access path: `.audit_views/runtime/db_query.py` (tool-shaped finders only); both blind audits are blind on the DB side.

### Per-task verdicts
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 (prepayment ← inactive repayment; prepayment ← cover ← netting) | PASS | PASS | PASS |
| 1 (CEP refund ← departure rollover ← graduate rollover ← active repayment; CEP refund ← active repayment, ← graduate rollover) | PASS | PASS | PASS |

Blind answers reproduced every gold write without reading the source: task 0 22.45 / 6.15 / 85.45 / 88.80, task 1 17.64 / 76.96 / 88.80 / 20.40. Every computation's fall-back is definite and different (task 0: 29.80, 0.00, 56.35, 17.40; task 1: 48.45, 46.31, 22.85, 97.85). In each task the order is load-bearing: in task 0 the cover is not owed without the netting first (91.60 > 88.55); in task 1 the graduate rollover is not owed without the payment first (94.60 > 84.80).

### Closing checklist
- Audit files one-to-one with tasks: runtime_context/meal_account_and_benefits/{0,1}.md (blind_answer frozen before reveal, gt_comparison appended), policy_kb/meal_account_and_benefits/{0,1}.md (source_to_kb, kb_to_source, bijection_verdict, dependency_form). First revision; there are no older revisions.
- All 8 prerequisite sentences are verbatim on their blocked side only, in their declared form. No other problem's tool name appears, and there are no routes and no aggregated chains.
- All 42 declared factors have their own document with the full ladder, every tier exact, findable by the record words. All 8 baselines are complete in their computation documents and none hints at a variation.
- Overwrite surface (2 clauses of meals_refunds_and_transfers): retired in the base doc, replaced text in force in the CEP hub, other clauses intact.
- No worked example, docstring or unlock schema carries a task's row, date or scored value. A grep of 22 scored and intermediate figures over docs/meals returned 0 hits. The unlock returns of the refund, active-payment and both rollover tools carry only the contracts.
- Gates on the final form: the snapshot above. No document changed during this audit.

### KB defects (renderer's)
none.

### Source-side items (instantiator's)
none.

### Observations (not RED)
- K-O1: these documents state the negative of the enrolled-campus key: the lunch-charge factor docs (prepayment, netting keep, cover, graduate rollover) and active_plan_campus_level ("Does the meal account's own campus decide this? No …"). This is entailed by the ladder. It names neither the baseline reading nor a customer's tier.
- K-O2: active_plan_school_year_months and inactive_plan_school_year_months each close with "This governs repayment payments on every School Nutrition Services Meal Account". The two ladders are identical, so entailment is unchanged.
- P-N1 (policy-side): two depended-on rules name their dependents in their own scope sentences, and the KB renders them as the source wrote them:
  - netting: "only as part of working out a departed-balance cover";
  - cover: "When a prepayment is quoted for a student".
  The blind audit still had to reason each hop.
- C-1 (cross-product, CONDITIONAL): several tiers rest on enrollment records (enroll product, not yet published): the lunch-charge tiers, the household enrolled-record count, the campus-level installments, and the departed/graduate/out-of-state classification. The seeded records conform to blueprint/products/enroll.yaml:
  - 2026-27 records enrolled or withdrawn, with the withdrawal date on the last day of attendance and the leaver reason as stated;
  - 2025-26 records `year_completed`, with `graduated` only for the grade-12 student.
  A re-judge is due once the enroll corpus is published.
- S-1 (seed, non-scored): Samuel's `charge_limit_reached` notice is dated 2026-10-13. The balance first passed −10.00 on 10-12, through the returned check, and the first charged meal past the limit was on 10-13. The notice is defensible under "reached through charged reimbursable meals", and no gold step reads it.
- Out of scope: the `verify_household_identity` gold step is a scenario-level share step, not part of the meals corpus. It was not judged here.

KB-VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=NONE

## revision_2 (2026-10-25, round 2 — cross-product re-judge)

### Entry conditions (`/tmp/erl0078_coord/kb_snapshot.sh meal_account_and_benefits meals`, run 2026-10-25T01:26:02)
- `check_docs.py meals => DOCS OK`
- `check_traceability.py meal_account_and_benefits => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)` (coordinator's run; not re-run here)
- 7/7 instantiation gates OK (EXTENDED, TASK TOOL CONTRACT, REPLAY 143/143 and 271/271, SOLVABILITY, COMPUTE, GROUNDING, SCOPE)
- Source hashes d1df998776a5 e0d10ca58005 c35522aede33 f44af508a274, docs/meals sha256 a13323b0351e73d3, runtime views ae38b758180d28ff / 18aaf513afb02295 — all identical to revision_1.
- Published corpora now on disk: activity, care, device, enroll, meals, music, transport.

### Round-1 items
- REDs to close: none (revision_1 was PASS/PASS, kb=CLEAN, src=NONE).
- Regression: none possible; docs and sources are byte-identical.
- C-1 (CONDITIONAL, enrollment-record tiers): **settled — conforms**. Every other-category row seeded in both worlds was swept in one pass through db_query.py.
  - The only such rows are enrollment records: 4 in task 0 and 7 in task 1.
  - Care, transport, activity, device, instrument, transfer-request, enrollment-ledger, registration-document, verification and handoff finders all return nothing for both households.
  - Each enrollment record was checked against the published enroll docs as of its date. The docs used were enrollment_type_admission_schedule, one_open_enrollment_per_student_per_year, registration_residency_and_required_documents, registration_document_deadlines and withdrawal_from_the_district_and_year_end.
  - Each record conforms on type, zoned campus, grade versus date of birth, entry type, the 30-day residency deadline, withdrawal date = last day of attendance (with the meal account's inactive_date on the same day), leaver reason, and year-end completion (graduated only for grade 12).
  - Member lists are in policy_kb/meal_account_and_benefits/0.md and 1.md under revision_2.
- Accepted residue (E1, replay closure; not a source item): neither household has registration-document log rows behind its "enrolled" / "residency verified" states. No gold step reads them, so they cannot be seeded.
- Cross-product contradiction scan: every sentence in care, device, enroll and transport that reads a School Nutrition Services Meal Account (status, tier, active/inactive, campus) is consistent with the meals rules. None restates a meals rule differently.
- Observations K-O1, K-O2, P-N1 and S-1 are carried forward unchanged (not RED).

### Per-task verdicts (revision_2)
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

KB defects: none. Source-side items: none.

KB-VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=NONE
