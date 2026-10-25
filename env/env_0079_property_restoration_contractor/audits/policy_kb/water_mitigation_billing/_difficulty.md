# KB-doc policy audit — water_mitigation_billing (product: water) — closing checklist

## revision_1 (2026-10-25)
Auditor: independent KB auditor. Inputs: kb_audit_notes.txt brief; runtime views 0/1.runtime.json (hashes match brief); docs/water (65 files, sha256 46eadd81…); db_query.py (tool-shaped, blind on DB side for both tasks); source revealed only after both blind answers were frozen.

Entry conditions: policy-side `VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN`; kb_snapshot_r1.txt `check_docs: DOCS OK`, `check_traceability: TRACEABILITY OK` (1 miss line / 0 mentioning unlock), other gates OK. Not re-run by this auditor (brief: check_traceability names hidden tool names).

| Task | Runtime blind audit | Two-way scan | Dependency form |
|---|---|---|---|
| 0 | PASS (debris 5 x 367.22 = 1836.10; antimicrobial 5199.00 x 0.47 = 2443.53; deposit 14273.16, all equal to GT) | PASS | PASS |
| 1 | PASS (HEPA 7448.00 x 0.31 = 2308.88; share 3504.43, equal to GT) | PASS | PASS |

Checklist:
- One runtime_context and one policy_kb file per task; no older revisions to preserve.
- Every normative atom of the five extended policies (rules, baselines, 28 factor ladders, 3 prerequisite edges, 5 overwrites over 3 base clauses) and the governing base policies is entailed by docs/water. Nothing unborne, nothing changed, nothing added.
- Each prerequisite sentence is verbatim and in state form in the blocked policy's hub only. Every hop can be worked out from the depended-on computation docs and the records.
- Every factor ladder is complete in its own document, every tier is exact, and each can be found from the record words its tier rests on (mold: "Mold Remediation job in invoiced status"; claims: "Insurance Claim Services file ... code-upgrade supplement requests ... carrier approvals").
- No tool name outside its own hub, no route, no aggregated chain, no task-mirroring title. No gold value or world state in any document.
- XF_recipe A–D sweep of the factor docs: boundaries stated with inclusive/exclusive wording and fall-through tiers (A8); no two-grouping arithmetic (A9); absent-record outcomes stated (no invoiced mold job; file without an ordinance or law limit; no code-upgrade request) (B1); latest-request ties routed to a human representative (B3); calendar-day counts stated (B4); rounding text matches compute (B5); overwrites retired and replaced correctly, with siblings named (C1–C3); tool docstrings carry no example values (D1). No member found.
- Conditional (not RED): the Insurance Claim Services corpus is unpublished. The water worksheet's billability sentence already matches blueprint claims.yaml (false only for AOB and Carrier Program).
- Notes for the coordinator (not defects at this layer): N-1 the generic assembly sentences in the baselines are source form under XF A2; N-2 the seeded mold signing payment of 150.00 matches the base Spot deposit, but the published mold signing-deposit rule would give 350.00 (this does not move the 1.25 tier); N-3 the claims rows are base-producible; N-4 the task-1 persona says "the rest of your part", which hints at netting the rule does not do.
- Coverage gap (by design): the account and fire corpora and other unclaimed surfaces are outside this audit.

KBVERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=NONE

## revision_2 (2026-10-25, cross-product re-judge)
- Snapshot run by this auditor: `.audit_views/runtime/water_mitigation_billing/kb_snapshot_r2.txt`: `check_docs: DOCS OK`, `check_traceability: TRACEABILITY OK` (1 / 0), and extended, task-tool, replay, solvability, compute, grounding and cross_fire OK. Source hashes are unchanged and docs/water is unchanged (65 files, sha256 46eadd81…). No regression in any of the three parts for either task.
- Round-1 conditional (claims billability on Direction to Pay): RESOLVED by the published `writeoff_and_appraisal_limits_d5434400` and `receivable_writeoffs_e63f67d9`. These match the water worksheet and the gold.
- Gold-read other-product rows repriced against the published docs. Task 1 claims rows: all match (the estimate figure has no record formula and is not scored; residue). Task 0 mold rows: two mismatches, neither of which moves gold (the mold balance stays above zero and the due date 2026-07-25 is unchanged, so 51 days still gives 1.25 and gold 14273.16 stands):
  - SRC-1 (settles round-1 N-2 as a src item): the mold signing-deposit payment is seeded at 150.00. The published `signing_deposit_amount_cb00dee0` and `short_notice_deposit_raise_5e3fb1a8` give 150.00 + 200.00 (1-day notice) = 350.00; no other raise, credit or prepayment applies.
  - SRC-2: the published `debris_haul_off_charge_c2b63a41` and `haul_off_line_amount_8173b50e` require a bagged debris haul-off line of 214.00 dated 2026-06-04 (8 sq ft drywall -> 1 load at the tier fee; no trip charge; no linked water job). The line is absent, so the seeded final_invoice_amount is 464.50 instead of 678.50 and the balance is 364.50 instead of 378.50 (with SRC-1).
  Both rows match the base mold charter. They count as mismatches only against the published mold docs.
- E5: PASS in both tasks. The SRC-2 line cannot be booked on an invoiced mold job, and even booked it could not move the credit tier. No claims write is owed at once on the Direction to Pay file.
- Rebuild corpus still pending: neither task reads rebuild rows, so nothing is conditional on it.

KBVERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=SRC-1,SRC-2

## revision_3 (2026-10-25, seed-only confirm)
- Entry check: the policy_task last line reads `VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN` ✓.
- runtime_views.sh re-run (runtime views unchanged: 571815b8… / 212e04a2…). kb_snapshot_r3.txt: DOCS OK, TRACEABILITY OK (1 / 0), all other gates OK. Charter f8752b18… and tools 8ab9323c… are unchanged. docs/water is unchanged (46eadd81…, 65 files).
- SRC-1 CLOSED: the mold signing payment is now 350.00 (150.00 + 200.00 short-notice raise), as the published mold docs give.
- SRC-2 CLOSED: the mold bagged debris haul-off line, 214.00 dated 2026-06-04, is present. The figures it moves (final invoice 678.50, late fees 25.00 each, balance 378.50, due 2026-07-25) all match the published mold docs.
- Gold is unchanged in both tasks: the multiplier stays 1.25 at 51 days past due. E5 PASS.
- Own-category seeded history rows the gold reads were checked against this difficulty's published extended docs in both tasks: task-1 debris_haul 1530.10 and antimicrobial 1500.24 reprice exactly, and every base-priced row matches. No mismatch.
- No new defect, no regression.

KBVERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=NONE
