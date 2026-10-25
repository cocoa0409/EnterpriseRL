# KB-doc policy audit — good_faith_estimates_and_disputes (product estimate)

## revision_1 (2026-10-21)

Entry conditions: policy-side `VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN`; gate snapshot 20:39:42 supplied; fresh kb_snapshot 2026-10-21T21:08:52: check_docs estimate => DOCS OK; check_traceability => TRACEABILITY OK (0 misses); EXTENDED / TASK TOOL CONTRACT / REPLAY --check / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; sha256 d791707e1ecc cb2ea284a3af a2d97f3fc0e9 c3bdb2712628; runtime views 3f830c99d8fb77d3 / e0626fe82be3bd92. All present.

Blind audits frozen before reveal (runtime_context 0.md e100c1bcddb60817, 1.md a5d52bdefc5f17fc); no contamination. Both blind answers equal GT in every scored value, factor tier and problem-tree hop (all hops state-derived, none pre-solved).

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 (surgery: deposit 1825.20 → fee 19.01 → balance 1287.31) | PASS | PASS | RED kb-1 |
| 1 (maternity: deposit 4137.00 → balance 2951.75) | PASS | PASS | RED kb-1 |

**kb-1** — the two balance computation documents name the assistance factor's quantity in their assembly paragraph: surgery_pre_service_balance_computation_b1f92f20 §4 "the price owed before surgery comes first …"; maternity_pre_delivery_balance_computation_d6b3b293 "Figuring it" "the price owed before delivery comes first …". The source assembly is generic ("a figure they select takes the place of the … package price before the deposits held are taken off"); "price owed before surgery/delivery" is defined only in aid_price / delivery_aid_price and is the title phrase of exactly one factor doc each. Values unaffected; form only.

Coordinator items judged: (1) the two surgery-balance prerequisite sentences in computation doc §5 with the late-patient-move definition — the blocked policy's own document, verbatim, state form, the definition is the source rule's own sentence → acceptable, not a finding. (2) generic assembly lines in the initial-deposit (Clause 4), late-change-fee (Term 5) and enrollment-deposit ((c)) computation docs — the source's own generic assembly, no factor named → not findings; only the two balance docs go beyond it (kb-1). Unlock schemas and worked/FAQ figures contain no scored value.

**src-1** — task_tools.py: `amount` documented "positive magnitude" (and the retain tool's `source_estimate_txn_id` "the deposit collection on that booking") but no body validates; probe: retain_late_change_fee_0cd5c1f6(…, source "x", amount -5) → "Fee retained: … amount=-5.00, deposit_held_usd=5.00".

Conditional (cross-product, re-judge after the Financial Assistance Program (assist) KB publishes): aid_basis, aid_fee_share, aid_price, enrollment_aid_basis, delivery_aid_price and the seeded FAP rows (charge_basis = 34.6 % of gross; award periods). Encounter and visit seed rows checked against published KBs: consistent.

Coverage gap (stated): base-only tiers (imaging package, non-package estimates) are audited only as base atoms; claim product not published.

VERDICT revision_1: task0=RED task1=RED kb=kb-1 src=src-1

## revision_2 (2026-10-21)

Gate chain:
- RENDER.log tail: "RENDER round 3: DOCS OK 50 docs".
- Policy side: "VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN".
- kb_snapshot 2026-10-21T22:10:23:
  - check_docs estimate => DOCS OK
  - check_traceability good_faith_estimates_and_disputes => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)
  - EXTENDED / TASK TOOL CONTRACT / REPLAY --check / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK
  - sha256: d791707e1ecc, 96980f077dcc, a2d97f3fc0e9, c3bdb2712628
  - runtime views: 3f830c99d8fb77d3, e0626fe82be3bd92

| Item | Status | Evidence |
|---|---|---|
| kb-1 | closed | Only the two balance assembly lines changed (corpus diff). The new wording is generic and matches the source. "Price owed before …" now appears only in the two assistance factor docs. |
| src-1 | closed | retain tool probes: -5 and 0 are rejected ("amount must be a positive USD figure …"). Source "x" and a non-collection row are rejected ("… is not a deposit collection on estimate …"). User tool bodies reject non-positive amounts and unknown estimates. Docstrings are unchanged. |
| Regression | none | Every other document is byte-identical. Runtime records are byte-identical. Gold values are unchanged (1825.20 / 19.01 / 1287.31; 4137.00 / 2951.75). |
| Assist re-judge | PASS | The 40.0 percent tier figure is published. Award dates (Section 10) match. Seeded FAP rows (34.6 % AGB, Section 8) reproduce exactly. The five assistance factors are no longer conditional. |

- Claim is still unpublished. Neither task reads a claim figure.
- Cross-product observation for the assist audit: assist defines "package price" as the estimate's total in hardship documentation, while estimate defines it as the facility plus professional lines. They apply in different scopes, neither task reads the assist one, and this is not an estimate-KB defect.

VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=NONE

## revision_3 (2026-10-22) — cross-product seed re-judge

### Snapshot
kb_snapshot 2026-10-22T00:44:57:
- check_docs estimate => DOCS OK
- check_traceability good_faith_estimates_and_disputes => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)
- EXTENDED / TASK TOOL CONTRACT / REPLAY --check / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK
- sha256: d791707e1ecc, 96980f077dcc, a2d97f3fc0e9, c3bdb2712628 — unchanged since revision_2
- runtime views: 3f830c99d8fb77d3, e0626fe82be3bd92
- estimate corpus: a04129cebcce60a1, unchanged

kb-1 and src-1 stay closed. Nothing regressed.

### Members checked (one exhaustive pass, against the published owning-product rules)
- **Task 0:** ED account and its 7 rows (encounter); 40 % assistance case and its 6 rows (assist); 4 appointments and their 10 rows (visit). **No miss.**
- **Task 1:**
  - 2022 inpatient account and its 10 rows (encounter) — **one miss** (src-2).
  - 2026 ED account and its 11 rows (encounter) — no miss.
  - 40 % assistance case and its 6 rows (assist) — no miss.
  - 1 appointment and its 3 rows (visit) — no miss.
- Neither world seeds claim, plan or records rows. No figure depends on claim, so nothing remains conditional.

### src-2 (task 1)
The 2022 inpatient prompt-pay payoff seeds payment 6846.75 and discount 1208.25 (plain 15 %). The published encounter self-pay payoff rule, with gross-charges +3, ledger-band +1 and a 27-day × 2.00 window credit, gives payment 6470.55 and discount 1584.45. This does not move a scored value: cesarean_amount reads only the 59514 line and the account's net charge lines.

### Not checkable from published rules
FPL percents 340.0 and 332.6: the assist KB cites the HHS guideline but publishes no figures.

VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=src-2

## revision_4 (2026-10-22)
**Gates.**
- Policy side: "VERDICT revision_10: task0=PASS task1=PASS charter=CLEAN".
- kb_snapshot 01:09:28: DOCS OK; TRACEABILITY OK (0 misses); EXTENDED / TASK TOOL CONTRACT / REPLAY --check / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK.
- sha256: d791707e1ecc, 96980f077dcc (both unchanged, so no re-render needed), a2d97f3fc0e9, 49f17d4d4f77.

**src-2 closed.** The 2022 inpatient payoff rows now read payment 6470.55 and discount 1584.45. That is exactly what the published encounter self-pay payoff rule produces: 19 % plus a 54.00 window credit on 8055.00. Only those two rows changed. The task-1 re-derivation through db_query.py is unchanged (4137.00 / 2951.75 = gold). No new defect, and no regression.

VERDICT revision_4: task0=PASS task1=PASS kb=CLEAN src=NONE
