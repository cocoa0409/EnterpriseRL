# KB-doc policy audit — gap_waiver_claims (product gap), closing checklist

## revision_1 (2026-10-22)

Inputs and entry gates (snapshot `/tmp/erl0075_coord/kb_snapshot.sh gap_waiver_claims gap`, 2026-10-22T10:49:19):
- `check_docs.py gap => DOCS OK`.
- Coordinator's post-publication `check_traceability.py gap_waiver_claims => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)`. Not re-run by the auditor, per the brief.
- Instantiation gates 7/7 OK.
- docs/gap: 68 files.
- Runtime views: 0 `997f30a6dc0e6321`, 1 `861f91d0e15a75ad`.
- Policy-side verdict: `VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN`.
- Published at audit time: gap, purchase, service, maintenance, warranty, loaner. vsc is unpublished.

| Task | Blind frozen (sha256 head) | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Task |
|---|---|---|---|---|---|
| 0 | `e05ffbfe8d6df671` | PASS (all 3 writes and values equal GT) | PASS | PASS | PASS |
| 1 | `f0d31c4ee8e6fd57` | PASS (all 4 writes and values equal GT) | PASS | PASS | PASS |

Checklist:
- Audit files correspond one-to-one with the tasks: `runtime_context/gap_waiver_claims/{0,1}.md` and `policy_kb/gap_waiver_claims/{0,1}.md`. This is the first revision.
- All seven extended policies are carried losslessly. That includes every baseline, the full ladder of all 37 declared factors (one document each, findable from record words, none cross-referencing), every overwrite (retired-for-scope with remainder), and every base clause in force.
- All five prerequisite sentences are verbatim, in state form, and single-homed in the blocked hub. Every hop was state-derived in the blind audit, and none was pre-solved.
- No foreign tool name, route, aggregated chain, task-mirroring title, or GT figure appears in any doc.
- KB defects: **none**.

Source-side items (instantiator's):
- **S1** (task 1): the seeded Kessler Care refund on KC-5308126 (339.15, paid to the lienholder 2026-08-27) is the maintenance baseline. The published maintenance retail-cancellation docs give 409.06 for this plan:
  - financed -> pro rata 498.04;
  - plan fee 75.00;
  - bundle discount recapture 13.98.
- S1 moves two scored values: the reversal (332.73 -> 402.64) and the credit (1912.27 -> 1842.36).

Cross-product conditionals:
- The Kessler Shield refund 1741.49 (task 1) reproduces under the vsc charter base and matches the restated 1758.67 recorded on the paid line.
- It is **CONDITIONAL** on the vsc docs. A re-judge is due after vsc is published.
- Task 0 reads only vsc status and has no conditional figure.

"Owed at once" (recipe 16) check against published maintenance docs: no other-product refund or request is owed at either opening.
- The maintenance and vsc refunds in task 1 were both paid within the 30-day period.
- Refund due balances are 0.00 and requests are completed.
- Task 0 has no maintenance plan, and its vsc contract is active with no request.

KB-VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=S1

## revision_2 (2026-10-22, re-audit after the seed-only S1 fix; all products published)

Entry snapshot (`kb_snapshot.sh gap_waiver_claims gap`, 2026-10-22T12:30:02):
- `check_docs.py gap => DOCS OK`.
- `check_traceability.py gap_waiver_claims => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)`.
- EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK.
- docs/gap 68 files.
- sha256 heads `8a7e2433a8ce 01f56d007e10` (yaml, tools: unchanged), `dc454e000826 ecc8a9bed338` (task JSONs: seed-only change).
- Runtime views unchanged (`997f30a6dc0e6321`, `861f91d0e15a75ad`).
- Policy-side verdict per brief: revision_9 CLEAN.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Gold | Task |
|---|---|---|---|---|---|
| 0 | PASS | PASS | PASS | unchanged (549.84 / 2970.75 / 579.84) | PASS |
| 1 | PASS | PASS | PASS | moved: reversal 402.64, credit 1842.36; termination 331.96 and release 367.31 unchanged | PASS |

Closing:
- **S1 closed.** The KC-5308126 refund is now 409.06, calculated and paid. That equals the published maintenance retail-cancellation figure. GT reversal and credit equal the re-derivation.
- **The round-1 CONDITIONAL is lifted.** The Kessler Shield KS-5602873 refund 1741.49 is re-judged against published `docs/vsc` (total-loss refund under clauses 6–7, Exclusionary Wrap time alone, fee waived on total loss) and **agrees**.
- **Exhaustive other-product re-price** (both tasks):
  - Kessler Care plan record and ledger: agree.
  - Kessler Shield contracts KS-5730284, KS-5602873, KS-5491607 (terms, prices, statuses, refund): agree.
  - Purchase deals and vehicle-price charges: agree.
  - No other-product write is owed at either opening.
- **No regression.** docs/gap is byte-identical to round 1; charter and tools are unchanged. No scored figure (old or new) appears in docs or unlock schemas.
- KB defects: none.
- New source items: none.
- Observation only: purchase documentary-fee and title charges are unseeded. No GAP figure reads them.

KB-VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=NONE
