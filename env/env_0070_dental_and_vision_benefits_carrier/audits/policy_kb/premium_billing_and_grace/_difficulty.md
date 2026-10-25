# KB-policy audit — premium_billing_and_grace (product: Premium Billing Accounts, docs/billing)

## revision_1 (2026-10-19)

### Entry conditions (Step 0)
- Policy-side verdict: `VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN` (audits/policy_task/premium_billing_and_grace/_difficulty.md, read after the blind freeze).
- Gate snapshot supplied by the coordinator (2026-10-19T09:28:55): `check_docs.py … billing` → DOCS OK; `check_traceability.py …/premium_billing_and_grace` → 0.json 14 0 True / 1.json 15 0 True / TRACEABILITY OK (non-unlock misses: 0); instantiate gates EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK. Source sha prefixes 11a9b88f97da1991 / b19f12afdf2130ae — re-verified equal at reveal.
- Runtime view and DB access path: `.audit_views/runtime/premium_billing_and_grace/{0,1}.runtime.json` + `db_query.py` (tool-shaped). Both blind audits are DB-blind; no contamination.
- Gates not re-run by this auditor (coordinator instruction: the snapshot is authoritative; running them leaks tool names). Docs unchanged since the snapshot (no edits in this audit).

### Per-task verdicts
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Task |
|---|---|---|---|---|
| 0 | RED (R0-1) | RED (KB-B0-1) | PASS | RED |
| 1 | PASS (conditional) | PASS | PASS | PASS |

### KB-side defects
- **KB-B0-1 / R0-1** — docs/billing/vision_early_cancellation_benefit_offset_3eeae95a.json, opening Rule sentence: "…and the Vision Plans benefits paid on it outran the premium". "on it" scopes the vision-benefits population to the unit, which vision_termination_credit_calculation_a2347af9 defines as "the subscriber's Vision Plans enrollment"; the source rule carries no such scope and its compute (ben_unit, customer-scoped XSUM) counts every vision claim of the customer in the coverage window. On task 0 the narrow reading gives credit 154.32 / grace-cure 187.86 instead of 74.56 / 267.62 (subscriber enrollment 45.00 vs household 370.00 against 8 x 36.28 = 290.24). The semantics the visible materials fail to carry: which vision claims count toward "vision benefits paid" in the offset, at the source's breadth.

### Source-side notes (do not change the KB verdicts)
- **SRC-1** (genuine ambiguity, low severity) — billing_ext_vision_term_credit rule/compute_basis for ben_unit/vtc_offset: "the vision benefits paid are the plan payments on vision services remarked as …" never says whose vision services count (the unit's subscriber enrollment, the other enrollments on the same family-tier plan, or every vision enrollment of the customer, on any account); compute sums every vision claim of the customer. With the unit defined as one enrollment record, the rule itself invites the narrow reading KB-B0-1 adopted.

### Conditional items (not RED; re-check after the Orthodontic Benefit Riders and Vision Plans corpora publish)
- Task 0: Cascade Vision Select 130 family monthly premium (36.28) — named by plan/tier in vision_termination_credit_calculation, stated in no published doc.
- Task 1: Cascade Vision Select 150 member_spouse (27.97) and Cascade Ortho Rider Family 1500 per-person premium (12.60) — named by plan/tier in the renewal/rider docs, stated in no published doc. Without them the renewal payment (337.15) cannot be completed from today's published surface.

### Closing checklist
- [x] One runtime_context and one policy_kb file per task, revision_1, blind answers frozen before reveal and not edited after.
- [x] Every prerequisite sentence (3 edges, all state form) verbatim in its blocked hub only, with same-form restatements; every hop state-derived from depended-on docs + records; no other problem's tool, route or aggregated chain anywhere.
- [x] Every declared factor ladder (vision 6, grace 5, dental 5, rider 5, renewal 4) carried with all tiers and figures in its own factor doc; baselines carried complete in their computation docs; retired surfaces (5 overwrites) correctly marked.
- [ ] Every normative atom entailed without changed meaning — fails on KB-B0-1.
- [x] No doc example or tool schema equals a scored value.
- Difficulty does not pass this revision: task 0 RED.

KB-VERDICT revision_1: task0=RED task1=PASS kb=KB-B0-1 src=SRC-1

## revision_2 (2026-10-19, re-audit round 2)

### Entry (gate /tmp/erl0070_coord/kb_reaudit_gate.txt, k=2)
- Upstream: `VERDICT revision_10: task0=PASS task1=PASS charter=CLEAN` (18:37:58Z).
- docs/billing newest file 18:44:51Z, re-rendered after the verdict.
- Earlier brief rounds were BLOCKED (revisions 7–9 ended charter=C-rN-1); nothing was written then.
- `kb_snapshot.sh premium_billing_and_grace billing` (2026-10-19T18:45:12):
  - DOCS OK
  - TRACEABILITY OK — 0.json 14 0 True / 1.json 15 0 True; non-unlock misses 0
  - EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK
  - src sha256 50297dc0208bd324 b19f12afdf2130ae

### Previous items
| Item | Status | Evidence |
|---|---|---|
| KB-B0-1 / R0-1 | closed | vision_early_cancellation_benefit_offset_3eeae95a: "paid on it" removed. The unit is defined as the plan unit; benefits are "the vision services of the unit, that is of every enrollment in it". Blind re-derivation gives one population (370.00 → offset 79.76 → 74.56 / 267.62), equal to GT. |
| SRC-1 | closed | Revised rule names the population and the other-billing-account test; compute v_other / ben_unit match it. |
| Conditional ortho premium (Family 1500 12.60; also Child 1500 13.40) | closed | docs/ortho/rider_lineup_entry_and_premium_c066eddd |
| Conditional vision premiums (Select 130 family 36.28; Select 150 member_spouse 27.97) | still conditional | docs/vision not yet published — re-check when it renders |

### Regression / new-defect sweep
- Title/content diff r1 → r2 over all 52 billing docs: 24 changed lines. All are in the offset doc, the calculation doc's unit paragraph, and the five status-wording selections.
- Every changed sentence is faithful to the revised source.
- All other docs are unchanged.
- No tool name, route, chain or gold value was introduced.

### Notes (no id)
- Latent compute-vs-rule edge: ben_unit counts every in-window vision claim of the customer, including a hypothetical non-unit, non-cancelled vision enrollment on this same account. No task effect.
- The new illustration's 45.00 subscriber amount coincides with one task-0 claim. It is not a scored value or total.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Task |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

KB-VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=NONE

## revision_3 (2026-10-20, cross-product re-judge)

### Inputs
- `/tmp/erl0070_coord/rejudge_notes.txt` followed in full.
- Snapshot `kb_snapshot.sh premium_billing_and_grace billing` (2026-10-20T05:56:04):
  - DOCS OK
  - TRACEABILITY OK — 0.json 14 0 True / 1.json 15 0 True; non-unlock misses 0
  - EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK
  - src sha256 50297dc0208bd324 b19f12afdf2130ae
- docs/billing unchanged since revision_2 (27395fedcf3c7fe1).
- All products published, including docs/vision (64 docs) and docs/ortho.

### Previous items
- KB-B0-1 / R0-1 and SRC-1: still closed (no doc or source change since revision_2).
- Conditional premiums, all settled and equal to the figures used:
  - Vision Select 130 family 36.28
  - Vision Select 150 member_spouse 27.97
  - Ortho Rider Family 1500 12.60 (also Child 1500 13.40)

### Exhaustive other-product row pass
Re-derived from the published dental, vision and ortho docs as of each row's date (tables in policy_kb/…/0.md and 1.md, revision_3):
- Task-0 world: 4 dental plans, 5 vision plans, 2 vision requests, 10 vision claims, 2 ortho riders, and the premiums inside 16 invoices.
- Task-1 world: 3 dental plans, 2 vision plans, 2 ortho riders, and the premiums inside 3 invoices and 2 credits.
- No DHMO, group, savings, provider, dental-claim or ortho-case rows exist in either world.

| id | rows | docs give | scored effect |
|---|---|---|---|
| SRC-R3-1 | task 0 vision_claims 38308cc5 (Lucia frame, age 13) and d1840869 (Mateo frame, age 10): 65.00 | 90.00 each (childrens_out_of_network_frame_amount_2a99675d) | **moves**: vision credit 74.56 → 24.56; grace-cure 267.62 → 317.62 (one row only: 49.56 / 292.62) |
| SRC-R3-2 | task 1 vision_plans 08852f82, c1a26c05: coverage_effective_date 2027-01-01 (applied 2026-11-20) | 2026-12-01 (enrollment_eligibility_and_reenrollment_lockout_24bb84b4) | **moves**: renewal payment 337.15 → 14.94 (r_vbinder falls to "otherwise") |
| SRC-R3-3 | task 0 ortho_riders 99429870 (active), 1da95e2f (withdrawn): rider_effective_date 2025-06-01 | not a permitted occasion; producible 2026-01-01 (adding_a_rider_4944148a cond. 3) | none (rider stays active; invoice and payment rows move together) |

### KB side
No KB defect. The billing docs read the recorded rows, and the policy (source) consumes the same rows, so docs + records still entail GT. The misses are rows the other products' published docs would not produce.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Task |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

KB-VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=SRC-R3-1,SRC-R3-2,SRC-R3-3

## revision_4 (2026-10-20, seed-only re-audit)

### Inputs
- Upstream `VERDICT revision_11: task0=PASS task1=PASS charter=CLEAN`.
- Snapshot `kb_snapshot.sh premium_billing_and_grace billing` (2026-10-20T06:19:49):
  - DOCS OK
  - TRACEABILITY OK — 0.json 14 0 True / 1.json 15 0 True; non-unlock misses 0
  - EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK
  - src sha256 50297dc0208bd324 b19f12afdf2130ae
- docs/billing unchanged (27395fedcf3c7fe1).

### Re-derivation
Both tasks were re-derived blind from docs + db_query.py before the GT was read:

| Task | Blind | GT |
|---|---|---|
| 0 | vision credit 24.56 (2026-10, 3); grace-cure 317.62 | same |
| 1 | dental 684.53, rider 175.37 (2027-01, 12 each); renewal 334.17 | same |

### Previous items
| id | Status | Evidence |
|---|---|---|
| SRC-R3-1 | closed | Lucia's and Mateo's frame rows now 90.00 |
| SRC-R3-2 | closed | Vision applied 2026-12-02, effective 2027-01-01; frozen_time 2026-12-04 |
| SRC-R3-3 | closed | Child 1500 riders effective 2026-01-01; invoices re-priced to match |

- Every other-product row of both worlds re-prices from the published dental, vision and ortho docs.
- No new defect; nothing regressed.
- No gold value appears in any published doc.

### Note for the coordinator (no id)
`.audit_views/runtime/premium_billing_and_grace/1.runtime.json` is stale. It still shows frozen_time 2026-11-24 and the 20 November persona; refresh it before any later round.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Task |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

KB-VERDICT revision_4: task0=PASS task1=PASS kb=CLEAN src=NONE
