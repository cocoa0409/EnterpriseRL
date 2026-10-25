# KB-doc policy audit — marketplace_orders_and_guarantee (product market), closing checklist

## revision_1
Auditor: fresh KB auditor (brief /tmp/erl0080_coord/msgs/kb_d5.txt). This auditor is independent of the renderer and of the policy-side auditor.

### Entry conditions
- The policy-side verdict was taken from the last line of audits/policy_task/marketplace_orders_and_guarantee/_difficulty.md: `VERDICT revision_12: task0=PASS task1=PASS charter=CLEAN`.
- Gate snapshot: re-run by this auditor (execute only) at 04:51:15Z, and again at the close, 05:04:44Z. Results:
  - `DOCS OK`
  - post-publication `TRACEABILITY OK`: 0.json copied 18 / missing 0; 1.json copied 15 / missing 0
  - EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK
  - yaml 852bd672…, task_tools a114d891…, docs/market 63 files, tree d10a3de4960150c3; unchanged between the two runs
- The runtime view and the DB access path were provided: `.audit_views/runtime` and db_query.py, tool-shaped. Both blind audits are blind on the DB side.

### Per-task part verdicts

| Task | Runtime blind audit | Two-way scan | Dependency-form scan | Task verdict |
|---|---|---|---|---|
| 0 | PASS: all four scored figures, units, ids and the 3-hop tree matched GT | PASS | PASS | PASS |
| 1 | PASS: all three scored figures, units, ids and the 2-hop tree matched GT | PASS | KB-EXPLICIT RED (KB-EXPLICIT-1) | RED |

### Findings
**KB-EXPLICIT-1**, docs/market/restocking_topup_schedule_203d5336.json, paragraph "Return handled.", first sentence.
- The computation (baseline) document of the restocking top-up opens: "the refund Northgate books when a seller has refunded every unit of a returned request but withheld more restocking than Northgate's schedule allows for the request's reason".
- This tells the reader that a reason-keyed restocking allowance schedule varies the figure. The baseline the document states never applies such a schedule; the schedule is the s_restock_schedule factor, carried in restocking_topup_allowance_schedule_6b196a7a.
- The solution is unaffected, because the factor is also findable from the return refund's restocking fee and the request's reason and date.
- This is the renderer's flagged placement choice 2. The same subject in the hub (e121c04b) is not a finding.

### Renderer placement choices judged
1. The response-period sentence of the three reimbursement policies sits in each decision hub. **Accepted.** It is each decision policy's own rule sentence, not an edge between problems.
2. The top-up's opening subject sentence is carried verbatim in its computation document. **KB-EXPLICIT RED** (KB-EXPLICIT-1).

### Coordinator rulings: how the KB renders them
- **Promotional card earned on a non-FBN marketplace order.** Every promo-recovery factor document states it ("an order whose merchandise total reaches USD 1000.00 earns a Northgate Promotional Gift Card whose initial load names that order"). The card itself is governed by the gift docs (type, value 5–100, issue + 45-day expiry, activation on issue). Re-priced every seeded promo row in both worlds against the published gift docs, and all are consistent:
  - task 0: issued 09-14, expiry 10-29, 100.00, redemptions 63.27 + 36.73;
  - task 1: issued 09-22, expiry 11-06, 100.00, redemptions 58.40 + 41.60;
  - each redemption ≥ the 10.00 smallest purchase, so the promo card cannot have paid a marketplace order;
  - status depleted at balance 0.
- **Proportional recovery vs whole remaining value.** Carried verbatim, with three tiers and an explicit computable formula for "whole remaining spent value". Observation: the gift doc promotional_value_expiry_and_voids_558edfab says "value already spent is deducted from the return's refund" on return of the earning purchase, with no partial-return wording. The market factor documents are the specific rule for marketplace refunds and state proportionality explicitly, so the specific rule decides. Not a contradiction at the level of entailment; noted for awareness.
- **Zero-figure grants and the referred filing.** Each decision hub carries the zero-figure tiers (not covered at the maximum, otherwise referred). Each filing hub's prerequisite sentence carries "the filing is referred too and nothing is filed". Faithful.
- **Order-dependence under a large reservation.** Not reached in either world. Checked: task 0 rooms 2034.27 / 558.14 vs grants 1871.34 / 251.54; task 1 single undecided claim.

### Policy-side notes (no verdict impact; src=NONE)
- The base eligibility clause "the return delivered to the seller more than seller_refund_business_days business days earlier" has no record field (no return-delivery event).
- The scope-exit clause of four policies lives inside their promo-recovery factor (the *_settles bindings), so a factor document gates the whole policy's scope. Rendered faithfully; unreached.
- The generic assembly sentence in every computation document presupposes adjustments without naming any. This is the source's XF A.2 combination sentence, required to fix order before the cap; accepted.
- The blind tool sequences omitted verify_customer_identity because the audit view lists only read tools. The runtime schema states the identity requirement, so this is not a KB defect.

### Closing checklist
- [x] Audit files correspond one-to-one with the tasks: runtime_context/…/0.md, 1.md; policy_kb/…/0.md, 1.md. Each blind_answer was frozen before reveal (hashes recorded).
- [x] Every normative atom of the structured source is entailed by docs/market:
  - base policies, variants, 7 extended rules, 35 factors (every tier), 3 retired clauses (each marked retired, out-of-scope content restated), 5 prerequisite sentences (verbatim, declared form, blocked hub only, resolvable from the depended-on documents and the records), 7 tool contracts.
- [ ] No pre-solving beyond the prerequisite sentences: open on KB-EXPLICIT-1.
- [x] check_docs and the snapshot were re-run on the final form (05:04:44Z): DOCS OK, TRACEABILITY OK.
- The difficulty does **not** close: task 1 is RED on the dependency-form part.

KBVERDICT revision_1: task0=PASS task1=RED kb=KB-EXPLICIT-1 src=NONE

## revision_2
- Render round 2 confirmed: `RENDER round 2: DOCS OK` (RENDER.log tail).
- Snapshot re-run 05:07:43Z: DOCS OK, TRACEABILITY OK (0 missing in both tasks), all 7 instantiate gates OK, source hashes unchanged. docs/market tree hash b18ee2a85dc4f282.
- KB-EXPLICIT-1 is **closed**. restocking_topup_schedule_203d5336 no longer says the top-up turns on "Northgate's schedule" for "the request's reason". It is the only document that changed: one paragraph per the text diff, one file by mtime. Nothing it carried is lost (subject in hub e121c04b; conditions in "When a top-up is owed" and factor document 6b196a7a).
- No new defect, no regression. The revision_1 policy-side notes stand, with no verdict impact.
- revision_2 is a delta re-check by the revision_1 auditor (not blind; disclosed in runtime_context revision_2).

| Task | Runtime | Two-way scan | Dependency form | Verdict |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

Closing checklist: all items checked. The difficulty's rendering passes the audit.

KBVERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=NONE
