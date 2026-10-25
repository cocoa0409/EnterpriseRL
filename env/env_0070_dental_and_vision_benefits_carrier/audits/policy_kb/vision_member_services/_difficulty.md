# KB-doc policy audit — vision_member_services (product: Vision Plans, docs/vision/)

## revision_1 (2026-10-20)

### Entry conditions (from the coordinator brief; not re-run by the auditor, per binding coordinator notes)
- Policy-side verdict: `VERDICT revision_13: task0=PASS task1=PASS charter=CLEAN`.
- `check_docs.py ... vision` -> `DOCS OK`; `check_traceability.py .../tasks/vision_member_services` -> `0.json 24 0 True / 1.json 14 0 True / TRACEABILITY OK (non-unlock misses: 0)`; instantiate gates EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK.
- Source sha256 prefixes match the brief: extended.yaml `3bff9ec767dbe5e9`, task_tools.py `2e073251237d9310`.
- Runtime view and DB path: `.audit_views/runtime/vision_member_services/{0,1}.runtime.json` + `db_query.py` (tool-shaped only). Blind audit was DB-blind; no contamination.

### Per-task verdicts
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS (blind = GT on all four writes) | PASS | PASS |
| 1 | PASS (blind = GT on both writes) | PASS | PASS |

### Closing checklist
- Audit files one per task: runtime_context/vision_member_services/{0,1}.md (blind_answer frozen before reveal; sha256 0.md `07bc19626984e2b8`, 1.md `7125bd92317707ad` at freeze) and policy_kb/vision_member_services/{0,1}.md.
- Every prerequisite sentence (6 edges over the two tasks, all `form: state`) stands verbatim in its blocked policy's hub (8de12d5a x2, 5675e894 x2, 266c1985, c3294f88) and in no other document; each hop is resolvable from the depended-on hub and the records.
- Every declared factor ladder (exam visit 6, eyeglasses 6, contacts order 6, OON glasses 5, OON contacts 4, refit 4) is carried in full in its own document; baselines carry the base rule and name every product figure; no factor document points at the baseline or another factor.
- Retired surface: 4 frequency clauses (2834b4d4), 2 in-network clauses (fbb6bf5d), 1 OON clause (8d80cc07) written as no longer in force; in-force remainders carried.
- No task tool named outside its own hub; no route, chain or task-mirroring title; no scored value in any example or unlock return.
- Gate re-run on the final form: not performed by this auditor (coordinator notes forbid running gates); the brief's snapshot above is the record.

### KB-side defects
None.

### Source-side findings (src)
- **S1 vision_oon_side_overlap (material, task 0)**: the glasses-part rule (children's frame amount 90.00, `g_famt`) and the contact-lens-part rule (`c_famt = P('oon_frame_reimbursement')`, 70.00) both claim Ivy's out-of-network claim V73-261211-4502 (140.00 >= 135.00 vs 135.00 > 120.00); neither tool refuses; the alternative side yields 135.00 / 423.00 / 202.50 instead of GT 140.00 / 457.00 / 262.50. Docs render both rules faithfully, so the ambiguity is source-born.
- **S2 provider_recred_due_dates (low, seed realism, both tasks)**: Vision Network agreements 1abff9cf (decision 2017-10-24, due 2029-11-01), ac3ca85f (2016-03-22, due 2028-05-01), aa5feab4 (2015-04-20, due 2028-05-01) contradict the provider docs' "due date = decision date + 36 months" with refreshed decision dates. No scored value depends on them.
- Policy-side notes (no id): n1 baselines announce extra parts ("every ... that applies"); n2 the contacts-order in-lieu sentence's "(the eyeglasses order of the same claim being settled first)" is an ordering clause outside the declared prerequisite edges (untriggered here).
- Other-product priced rows (billing invoices, binder and regular payments, premiums, paid-through dates, balances) re-priced against the Premium Billing Accounts docs and the Vision rate sheet: no miss.

KB-VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=S1_vision_oon_side_overlap,S2_provider_recred_due_dates

## revision_2 (2026-10-20, re-audit round 2)
- Upstream: `VERDICT revision_15: task0=PASS task1=PASS charter=CLEAN` (06:32:53); docs/vision re-rendered after it (newest 06:34:32).
- `kb_snapshot.sh vision_member_services vision` (06:34:56): DOCS OK; TRACEABILITY OK (0.json 24 0 True, 1.json 14 0 True, non-unlock misses 0); EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; src sha256 `5cfe619416ed9f73 649138cb8694eda2`.
- Correction: docs/vision holds 64 documents (revision_1 said 66; its dump also held 64).
- Changed documents: ea443559, 266c1985, 55dc911f, a8bc66f4 only. Blind re-derivation from them + db_query.py was frozen before reveal; it equals GT on all six scored writes.
- S1 closed (receipts-only, complementary side test in both OON rules and both docs; both filing tools refuse the other side; frame amounts aligned; task 0 single answer). S2 closed (all three agreements: due = refreshed decision + 36 months). No KB defect, no regression, no new src item; other-product rows re-price.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

KB-VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=NONE
