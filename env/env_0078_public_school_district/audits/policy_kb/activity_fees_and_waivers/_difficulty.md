# KB-layer audit — activity_fees_and_waivers (product activity) — difficulty close-out

## revision_1

### Entry conditions (cited from /tmp/erl0078_coord/kb_snapshot.sh, 2026-10-25T01:25:46; re-run 01:37:19, identical)
- `check_docs.py activity => DOCS OK`
- `check_traceability.py activity_fees_and_waivers => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)`. This is the coordinator's run; I did not run it myself.
- The 7 instantiation gates are OK: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE.
- Source hashes: dab248c303c4 / 0040d1ba3cee / a62b2741bfad / 47ac381004cd. 58 files in docs/activity.
- Runtime views: 0.runtime.json 6944d8668ef6f5b2; 1.runtime.json 6af7a75aa1f3cdce.
- Policy-side verdict: `VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN`.
- DB access was blind: tool-shaped db_query.py finders and unlock_* only, with no initial_state read before the freeze.

### Per-task part verdicts
| Task | KB-RUNTIME (blind vs GT) | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS: 16.25 / 50.00, one state-derived hop, identical to GT | PASS | PASS |
| 1 | PASS: 75.00 / 107.00 / 62.00 / 225.25, five state-derived hops, identical to GT | PASS | PASS |

### KB defects (renderer's to fix)
None.

### Source-side items (instantiator's to fix)
- **S1** (seed realism, XF E1; task 1): the seeded music row instrument_checkouts d7032204-11c9-4802-98ac-56973f025ef0 (Large Instrument Usage (Tuba, Cello, String Bass), checkout 2027-01-14) has due_back_date `2027-05-27`. The owning product's published rule is music/due_back_dates_and_late_return_charges: "Large Instrument Usage (Tuba, Cello, String Bass) | May 21" and "The five school-year usage types share the due-back date of May 21". The music charter says due_back_date "05-21", so the produced value is 2027-05-21. No gold step reads this field, so no scored value moves.
This is the only member found in one exhaustive pass over every other-category seeded row of both tasks: enroll ×3, transfer requests ×2, meal accounts ×2, music checkout ×1.

### Observations (not RED)
- R6-WAIVED (policy layer): booking_lead_tier, late_booking_tier, instrument_haul_tier. I checked their documents for KB defects and found none.
- Concert attire grouping: the source signals the inside-floor vs further-amount split only by "is added" vs "is added to the total". The KB carries the same wording, which suffices.
- Number of installments: for a first installment after 2027-03-31, the "due dates through 2027-03-31" count is 0 literally, while compute gives 1. Month-end "same day" due dates are a carried policy-layer observation. Neither is engaged in this suite.
- Base rendering is verbatim (BLUEPRINT-KNOWN): the base credit text says a uniform package is "ordered ... at clearance", while the attire schedule orders it on the packet's received date (carried from the policy layer).
- Students table (shared, not a product row): task 1 zoned_campus Hollis for an out-of-district residence (carried).
- Accepted residue (no gold step reads these rows): enrollment records-log documents, the music usage-fee ledger row and the checkout condition report.

### Closing checklist
- One runtime_context file and one policy_kb file per task, each with revision_1. The blind answers were frozen before the reveal.
- Every normative atom of the six extended policies and their base domain is carried. That covers every tier of all 29 declared factors' ladders and both retired evt_fees clauses plus the retired installment clause, marked out of force. The 6 prerequisite sentences are verbatim, in state form, in the blocked hubs only.
- No other problem's tool, route or aggregated chain appears anywhere.
- check_docs and check_traceability on the final form: lines above (re-run 01:37:19).

KB-VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=S1

## revision_2

### Entry snapshot (/tmp/erl0078_coord/kb_snapshot.sh, 2026-10-25T01:45:46, run by me)
- `check_docs.py activity => DOCS OK`.
- `check_traceability.py activity_fees_and_waivers => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)`. This is the coordinator's line; I did not run it.
- The 7 gates are OK: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE.
- Source sha: dab248c303c4 / 0040d1ba3cee (unchanged) / b9127d0bcbe3 / 5deb4dd827d6 (task JSONs re-seeded).
- docs/activity: 58 files, concat 5be011ce29f4554e, unchanged since r1.
- Runtime views 6944d8668ef6f5b2 / 6af7a75aa1f3cdce, unchanged.
- Policy layer: `VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN`.

### Round-1 items
- **S1: closed.** The seeded checkout due_back_date is now 2027-05-21, as the published music rule requires (May 21 for Large Instrument Usage).
- KB defects: none in r1, none now.

### Regression / new-defect check
- The finder returns of both tasks' opening DBs were diffed against the frozen r1 returns. Task 0 is identical. Task 1's only difference is the S1 field.
- GT writes, owners, values and trees are unchanged.
- The corpus, charter and tools are byte-identical, so no re-render was needed and none was done.
- r1 observations carry over unchanged. No new defect.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

KB-VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=NONE
