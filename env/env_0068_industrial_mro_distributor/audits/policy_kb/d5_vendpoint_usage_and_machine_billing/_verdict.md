# KB doc-policy audit verdict — d5_vendpoint_usage_and_machine_billing (product vending)

## revision_1

Auditor: fresh KB auditor (not the renderer, not the policy auditor), 2026-10-17.

### Entry conditions (cited from the brief, not re-run)
- Policy-side: `VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN`.
- check_docs.py vending → DOCS OK (54 docs; tree prefix 6023d731d310f26b); check_traceability.py → 0.json 23 0 True / 1.json 28 0 True / TRACEABILITY OK; instantiate gates all OK.
- Runtime views verified by sha256: task0.runtime.json 3d912113…, task1.runtime.json f6e25dfc…, db_query.py b5df0dbd…. Corpus seen: docs/vending 54 docs (my `sha256sum *.json | sha256sum` = f8e77d1a…).
- Input limitation: the runtime view carries no run.sh system background, so the GT's `verify_caller_identity` step was not judged blind; it is outside the vending KB.

### Isolation
- Blind answers frozen before any source read: runtime_context/…/0.md (ff6904e4… at freeze), 1.md (0226961b… at freeze); gt_comparison appended afterwards, blind text untouched.
- Contamination: directory-name listing of audits/ and audits/policy_task/ only; no file content, no scored value. No recursive grep over tasks/ or the scenario root; plan.md and worklog.md never opened. No other scenario read.

### Per-task part verdicts
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 (start-up return ← start-up par review) | PASS (28; 6.00 × 2 = 12.00; blind = GT) | PASS | PASS |
| 1 (settling par ← placement ← retired-item credit) | PASS (10.43; 55; 46; blind = GT) | PASS | PASS |

### Closing checklist
- Audit files one per task in both directories; revision_1 only.
- All five extended rules carried sentence by sentence (two parameter renderings, equivalent); all 26 declared factors' ladders complete with figures, each in its own document, reachable from record words, naming its other product where it reads one.
- All three prerequisite sentences verbatim, state form, only in the blocked policy's hub; each hop resolvable from the depended-on hub's own words and the records.
- Retired surface: both superseded base clauses written as no longer in force, their replaced_by carried in the extended hubs; no undeclared retirement.
- No tool name, route or aggregated chain beyond the prerequisite sentences; no gold figure in examples or unlock schemas.

### Source-side items (src=)
- SRC-1 rule-vs-compute (latent, cross-product): list_price_step "when either line carries no list price, the share is one" vs compute treating a 0 substitute list price as ratio 0 → 1.2 (a 0 retired list price → 1). Pricing doc says protected substitute lines carry list price zero. Not triggered in task 1.
- SRC-2 rule wording: retired-item assembly sentence "…so that no credit exceeds what was billed for the units the vend did not dispense…" names a factor's quantity inside the baseline computation document (carried verbatim). Not a KB defect; fall-back still definite.
- SRC-3 rule vocabulary (latent): "highest quote reference" has no record field of that name (new-item lines carry change_reference SPQ-…); compute sorts by change_reference. Not triggered.

### Observations (placement, stop rule; not verdicts)
- O-1 generic assembly sentences in the five computation documents; O-2 "retired item's units" defined in the placement computation document though only factors use it.

KB-VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=SRC-1,SRC-2,SRC-3

## revision_2

Re-audit round 2 (same auditor, same access path; revision_1 text above untouched).

### Gate (checked before writing)
- `RENDER.log` → `RENDER round 3: DOCS OK`.
- `_difficulty.md` last VERDICT → `VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN`.

### Round-2 gate snapshot (run by this auditor)
- `.venv/bin/python skills/erl-kb-doc-render/scripts/check_docs.py env/env_0068_industrial_mro_distributor vending` → `DOCS gate product=vending profile=extended docs=54 roles={'facet': 8, 'policy': 10, 'factor': 26, 'baseline': 5, 'hub': 5}`; `required quantitative keys=109 task_tools=5 prerequisite edges=3`; `[PASS] mechanical gates: …`; `[MANUAL REQUIRED] …`; `DOCS OK`.
- `.venv/bin/python skills/erl-task-instantiate/scripts/check_traceability.py env/env_0068_industrial_mro_distributor/tasks/d5_vendpoint_usage_and_machine_billing` → `0.json 23 0 True` / `1.json 28 0 True` / `TRACEABILITY OK`.
- `__pycache__` created by the runs (blueprint/, tasks/d5_vendpoint_usage_and_machine_billing/) deleted; the two under skills/…/scripts pre-existed and were left.
- Hashes: docs/vending set (`sha256sum *.json | sha256sum`) 39722620…; vending.extended.yaml 8b0a7e3b…; task_tools.py 1dee5f0c… (unchanged); runtime views and db_query.py unchanged.

### Findings
- SRC-1 closed (rule and compute both give share 1 for a zero list price on either line; doc carries the new rule verbatim plus an entailed zero-price boundary row).
- SRC-3 closed ("highest change reference" in rule, compute_basis and doc; matches compute and the record field; "quote reference" gone from the corpus).
- SRC-2 unchanged and not routed (coordinator stop rule); still open on the source side, not a KB defect.
- Regression check: title+content diff of all 54 docs shows only substitute_list_price_step_e1ed2a58 changed; source diff confined to that one rule sentence and the `list_ratio` line; GT values unchanged (28, 6.00; 10.43, 55, 46); all rule sentences still verbatim (same two parameter renderings); prerequisite sentences still only on their blocked hubs; gold scan of examples and unlock schemas clean.
- New defects: none.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

KB-VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=SRC-2

## revision_3

Cross-product re-judge (round 3), all seven products published. Same auditor and access path; earlier revisions untouched.

### Gate snapshot (`/tmp/erl0068_coord/kb_snapshot.sh d5_vendpoint_usage_and_machine_billing vending`, execute only)
- `check_docs vending: DOCS OK (54 docs, tree 758b48699a710cd2)`
- `check_traceability: TRACEABILITY OK; non-unlock misses: 0`
- `gates: EXTENDED OK TASK TOOL CONTRACT OK REPLAY OK SOLVABILITY OK COMPUTE OK GROUNDING OK SCOPE OK`
- `hash 8b0a7e3be1a7ee56` (vending.extended.yaml) · `hash 1dee5f0cb4c3247b` (task_tools.py) — both as in revision_2. Vending docs title+content identical to revision_2.

### Conditionality
Nothing in the round-1/round-2 PASS rested on an unpublished product: the vending factor and hub documents read credit, order, pricing and StockSmart records in the record kinds and vocabulary those products now publish, and every cross-product row feeding a scored value (returned payments, shipped order lines per ship-to, removal/substitute/competitive-match contract lines, the 11.592 post-removal price, StockSmart bins) is consistent with its product's rules. Scored values unchanged: task 0 28, 6.00; task 1 10.43, 55, 46.

### Source-side items
- SRC-2 (rule wording, retired-item assembly sentence) — still open, not routed (stop rule).
- SRC-4 (task 0; vmi/credit) — three monthly vmi_replenishment invoices (9214.60 / 8876.35 / 9402.10) on a Weekly Service program that bills per visit, unbacked by any vmi_activity row and beyond what its bins can bill.
- SRC-5 (both; vmi) — Weekly Service programs with 2 bins (gate 300), never-replenished bins not removed at par reviews, absent 400.00 monthly minimum fees (task 1: no program activity at all since 2024-03-04).
- SRC-6 (task 1; credit) — Net 30 Standard account with credit_limit 60000.00 above the tier ceiling 49999.00.
- SRC-7 (both; pricing) — commitments 250000.00 (Category Contract, tier 75000.00) and 500000.00 (Net-Price, tier 250000.00); task 0 expiration 2027-10-31 vs a first term ending 2026-10-31; task 1 auto_renew True on a non-auto-renewing tier; 3 contract items against tier minimums of 25 / 50.
- SRC-8 (task 0; order) — SO-5520117 booked before the Standard Ship-To cutoff on 2026-09-08 but shipped 2026-09-10.
- SRC-9 (both; order) — ship-to anniversary reviews not recorded after later handling (ST-51842, ST-51843, ST-52614); ST-52611's 2026-10-01 anniversary falls due on task 1's own call; last_order_date taken from ship dates in task 1, booking dates in task 0.
None of SRC-4..SRC-9 moves a scored value; SRC-9 (ST-52611) is the one with a runtime realism risk (an out-of-closure order-product write a careful agent may think owed today).

### Per-task part verdicts
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

KB-VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=SRC-2,SRC-4,SRC-5,SRC-6,SRC-7,SRC-8,SRC-9

## revision_4

Re-audit round 4 after the seed-only rework of SRC-4..SRC-9. Same auditor and access path; earlier revisions untouched.

### Gate
- `_difficulty.md` last VERDICT → `VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN`.
- Runtime view refreshed with the coordinator's command; task0.runtime.json 3d912113…, task1.runtime.json f6e25dfc… (unchanged).
- `/tmp/erl0068_coord/kb_snapshot.sh d5_vendpoint_usage_and_machine_billing vending` → `check_docs vending: DOCS OK (54 docs, tree 758b48699a710cd2)`; `check_traceability: TRACEABILITY OK; non-unlock misses: 0`; `gates: EXTENDED OK TASK TOOL CONTRACT OK REPLAY OK SOLVABILITY OK COMPUTE OK GROUNDING OK SCOPE OK`; `hash 8b0a7e3be1a7ee56`; `hash 1dee5f0cb4c3247b`. Docs tree and source hashes unchanged from round 3; vending document text unchanged.

### Findings
- Closed (verified on the reworked records against the owning product's published rules): SRC-4 (StockSmart replenishment invoices now one per self-scan order, backed by deliveries), SRC-5 (Self-Scan programs with 26 bins, setup and bin-add fees, no minimum fee or par review owed), SRC-6 (credit limit 45000.00 within the Net 30 Standard band), SRC-7 (tier commitments, terms, auto-renew and contract item counts), SRC-8 (SO-5520117 ships on its booking day), SRC-9 (ship-to anniversary reviews current, last order dates = booking dates; no review due on either call day).
- Still open: SRC-2 (retired-item assembly sentence names a factor quantity in the computation document) — not routed under the stop rule; not a KB defect.
- Re-judge: both scored solutions are still uniquely entailed from the docs and records (task 0: 28, then 2 × 6.00; task 1: 10.43, 55, 46), every factor tier unchanged; no write of any product is due on either call day outside the closure; no new defect; no regression.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

KB-VERDICT revision_4: task0=PASS task1=PASS kb=CLEAN src=SRC-2
