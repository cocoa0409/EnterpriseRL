# KB-layer audit closing — vehicle_purchase_deals (product purchase), revision_1

## Entry conditions (cited, not re-run by the auditor)
- Policy verdict: `VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN`.
- kb_snapshot.sh (2026-10-22T10:20:27):
  - `check_docs.py purchase => DOCS OK`
  - `check_traceability.py vehicle_purchase_deals => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)`
  - EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK
  - 73 docs; docs sha256 c9d5d4252466 28698d49db86 233d1414491e 3ae5d6f76369
  - runtime views 0 = b8654886f319a1ce, 1 = 684931ab5aafb685
- Blind freeze (2026-10-22T10:25:28Z, before any source read):
  - runtime_context/vehicle_purchase_deals/0.md blind_answer sha256 7d9ab18cafa159350e1496e72f47916a9afb4d04a68158228168845b1bf1ebfe
  - 1.md 250de09f7cf4a08de0816b287106d258760a1700653f7aa18daea049a2cd8a0b
  - Both are first-written states. gt_comparison was appended after the reveal.
- The DB side was tool-shaped via db_query.py, so the audit was blind on the DB side. No contamination.
- Cross-product: every factor here reads Service Accounts and Repair Orders (published). None depends on vsc or gap (unpublished), so no CONDITIONAL figures.

## Per-task part verdicts
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Blind = GT |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | 26.33 / 2750.00 / 2026-10, 171.74 / 5066.79; tree order {fee check, incentive} → late fee → order deposit |
| 1 | PASS | PASS | PASS | 1940.49 → 7 days (new expiry 2026-11-01) |

## Closing checklist
- [x] One runtime_context file and one policy_kb file per task. Each is revision_1 with no older revisions.
- [x] Every prerequisite sentence (3 state-form, 1 action-form with fallback) is verbatim in its blocked hub only, and every hop resolves from the depended-on documents and the records.
- [x] All 31 declared factor ladders of the 6 extended policies are carried in full in their own documents, each findable by its record words. Each baseline has its defaults or named figures.
- [x] Retired surface: 5 overwritten clauses, each marked "no longer in force" in its bearing document, with sibling clauses still in force. The KB retires nothing undeclared.
- [x] No other problem's tool name, route, aggregated chain or task-mirroring title. No scored value, deal number or name in the docs.
- [x] Final-form gate lines: the coordinator snapshot above (DOCS OK; TRACEABILITY OK, 0 misses). The auditor does not run check_traceability, per the brief.

## KB defects (renderer)
None.

## Source-side items (instantiator)
- **S1. Cross-product seed realism, task 0, no gold movement.** The service early-payment discount credits 9.31 (2026-03-11) and 26.60 (2026-06-16), and the matching ACH payments 474.47 / 1333.67, follow the retired 2% service clause. The published service rules (tenure addition +0.5%, payment-standing share ×0.5 after the 2025-08-05 late fee) give 5.82 and 16.63. Details are in policy_kb/0.md S1.

## Policy-side notes (not routed by this audit)
- **N1.** Generic assembly sentences ("every add-on … each share …", "starting day") are carried in the computation documents of all six extended policies. They are source-verbatim, outside baseline.rule, and in the coordinator's placement-only class.
- **N2.** The fleet late fee replaced_by says "together with the base assessment timing" but sets no other timing for covered deals. This is wording only.
- **N3.** It is latent whether the 60% extension-deposit credit ceiling applies before or after the shares. The compute and the KB agree on "before"; no current task is affected.

KB-VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=S1

## revision_2 (confirm round after the seed-only S1 fix; policy VERDICT revision_7 CLEAN)
- Snapshot 2026-10-22T10:39:15:
  - `check_docs.py purchase => DOCS OK`
  - `check_traceability.py vehicle_purchase_deals => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)`
  - EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK
  - sha256 c9d5d4252466 28698d49db86 0acd2133fa91 1b573f9e91d8: charter and tools are identical; task JSONs only changed
  - runtime views unchanged
- Docs: no file is newer than revision_1, and none of the new seed values leaks into a doc.
- **S1 closed.** The task-0 early-payment credits are now 5.82 / 16.63, and the payments are 477.96 / 1343.64, booked on labor line A. These equal what the published service rules produce. Ledger and open_balance reconcile at 10724.70.
- No regression: every factor input and all six scored values reproduce. Task 1's records are identical.
- No new KB or source defect. Notes N1–N3 are unchanged and not routed.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

KB-VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=NONE

## revision_3 (cross-product re-judge; all seven products published)
- Snapshot 2026-10-22T12:20:21:
  - `check_docs.py purchase => DOCS OK`
  - `check_traceability.py vehicle_purchase_deals => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)`
  - gates 7/7 OK
  - sha256 c9d5d4252466 28698d49db86 0acd2133fa91 1b573f9e91d8 (unchanged since revision_2)
  - runtime views unchanged
- New since revision_1: only docs/vsc and docs/gap. docs/purchase and docs/service are unchanged.
- CONDITIONAL figures: none were graded in revision_1 or revision_2.
- Other-product rows in the two worlds: service accounts and ledgers only. Every finder of the other products returns nothing for both customers.
  - Task 0: all 23 service rows and the account fields re-price exactly, including the round-2 S1 fix.
  - Task 1: all 26 rows except the points class.
- **S2 (source, seed realism, no scored movement).** Task 1's four points-earned rows (376 / 1034 / 272 / 756) and rewards_points_balance 2438 follow the retired 2-per-dollar earning clause. The published rule gives 470 / 1292 / 590 / 1195 and 3547 (×1.25 tenure multiplier, +250 frequent-visit bonus from the 3rd payment in 12 months). Details are in policy_kb/1.md revision_3. None of these rows moves a scored value.
- Owed-at-once writes that could move scored reads mid-conversation: none in either world. Fleet invoices are not yet due or paid; no comeback, expiry, tier review or contract writes are owed.
- Accepted residue (not RED): unread warranty coverage rows for the delivered vehicles; unseeded service history before 2025.
- Task verdicts stand: task 0 PASS/PASS/PASS, task 1 PASS/PASS/PASS. No KB defect.

KB-VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=S2

## revision_4 (confirm round after the seed-only S2 fix; policy VERDICT revision_8 CLEAN)
- Snapshot 2026-10-22T12:37:54:
  - `check_docs.py purchase => DOCS OK`
  - `check_traceability.py vehicle_purchase_deals => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)`
  - gates 7/7 OK
  - sha256 c9d5d4252466 28698d49db86 4ffaacbd2b90 a7216ed75984: charter and tools identical
  - runtime views unchanged
- No doc changed.
- **S2 closed.** Task 1's points rows are 470 / 1292 / 590 / 1195 and the balance is 3547, matching the published service points rule. A field diff shows no other row changed in either world.
- Same-class neighbour: task 0 has no points.
- No scored value moved, nothing regressed, and there is no new defect.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

KB-VERDICT revision_4: task0=PASS task1=PASS kb=CLEAN src=NONE
