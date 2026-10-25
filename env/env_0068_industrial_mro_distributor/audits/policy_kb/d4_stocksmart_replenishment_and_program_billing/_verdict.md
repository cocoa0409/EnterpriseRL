# KB doc-policy audit verdict — d4_stocksmart_replenishment_and_program_billing (product vmi)

## revision_1

**Auditor.** A fresh erl-kb-doc-policy-audit auditor, 2026-10-17. It is independent of the renderer and of the policy auditor.

**Inputs verified.**
- Docs tree sha256 `c01bdb6a68f28a05…`, equal to the gate snapshot.
- vmi.extended.yaml `aa920acb…` and task_tools.py `805a54d8…` match the brief.
- Runtime views task0 `64d956a6…` and task1 `a072a743…` match.
- db_query.py `b5df0dbd…` matches.

**Gate snapshot.** These are the coordinator's lines on the final form, not re-run by the auditor:
- check_docs vmi: DOCS OK (62 docs);
- check_traceability: 0.json 28 0 True / 1.json 26 0 True / TRACEABILITY OK;
- instantiate gates: EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK.

**Blind isolation.**
- Both blind answers were frozen before the reveal (runtime_context 0.md blind part `f0b785fb…`, 1.md `7be671ed…`).
- contamination_disclosure: none.
- The DB was read only through db_query.py.
- No other env/ scenario was read.
- No recursive grep was run over tasks/ or the scenario root.

| Task | Runtime blind | Two-way scan | Dependency form |
|---|---|---|---|
| 0 | KB-RUNTIME RED (K1) | KB-BIJECTION RED (K1) | PASS |
| 1 | PASS | PASS | PASS |

## KB-side finding

**K1.** `docs/vmi/annual_usage_value_share_4f2d4b12.json` (the abc_share factor of vmi_ext_vended_item_fill_level) carries its ladder in full. It never says that its value-class share enters the **fill-to level's** carried share.

- Its only scope wording is: "A new consigned bin … carries less Corbett-owned stock when the item is of high annual value" / "Value-class share put into the carried share".
- The opening-stock standard (opening_consigned_stock_quantity_cb598980 Section 3) defines a second "carried share, which is the product of every share that applies".
- Every sibling share doc names its target ("carried share of that bin's fill-to level"; "Applies to: opening consigned stock"). This one alone does not.
- The blind reader placed it on opening stock and got request / reorder-point-entry `max_qty` 28 against gold 26. The opening quantity of 13 coincides under both placements.

The semantics that are missing: the result that this share modifies.

## Source-side items

**S1 (rule-vs-compute wording).** vmi_ext_opening_consignment and vmi_ext_hold_converted_fill carry the param `open_ended_months: 1200`, which their compute uses to bound price lines. Their rule text says only "in effect today" / "takes effect after today". The KB renders the bound as a parenthetical:
- opening_consigned_stock_quantity_cb598980 Section 4;
- credit_hold_first_fill_quantity_2f14ad7e §3.

It has no scored effect on either task. I do not judge it a KB defect; it is listed here as required.

## Difficulty closing checklist

- [x] One runtime_context file and one policy_kb file per task (0.md, 1.md), each with blind_answer / gt_comparison and source_to_kb / kb_to_source / bijection_verdict / dependency_form.
- [ ] Every normative atom entailed. Fails on K1: the abc_share target is not entailed. All other atoms, factor ladders and retired surfaces of the six policies are entailed.
- [x] Every prerequisite sentence (R1, O1, O2, C1, H1, H2) is verbatim, in state form, on its blocked hub only, and resolvable from the depended-on docs and records.
- [x] No other problem's tool name, route or aggregated chain anywhere. Titles are general.
- [x] No gold value in unlock schemas or doc examples. No world state written as policy.
- [ ] Difficulty passes: **no**. Task 0 is RED on K1.

KB-VERDICT revision_1: task0=RED(KB-RUNTIME,KB-BIJECTION) task1=PASS kb=K1 src=S1

## revision_2

**Round-2 re-audit, 2026-10-17.**

**Gate.**
- RENDER.log reads `RENDER round 6: DOCS OK`.
- check_docs run by this auditor: `DOCS OK` (62 docs; mechanical gates PASS).
- check_traceability: `0.json 28 0 True / 1.json 26 0 True / TRACEABILITY OK`.
- The `__pycache__` dirs the gates created under env/ were deleted.
- Docs tree sha256 is `51b37d9a…`. Source hashes are unchanged.

**Contamination.** Gold was seen in revision_1, so round 2 checks the changed text against it after the reveal. This is disclosed in the runtime files.

| Task | Runtime | Two-way scan | Dependency form |
|---|---|---|---|
| 0 | PASS (K1 closed) | PASS | PASS |
| 1 | PASS | PASS | PASS |

**K1: closed.**
- `annual_usage_value_share_4f2d4b12.json` now places the value-class share in "the carried share of that bin's fill-to level", in its title, scope sentence and table header. The ladder is unchanged.
- Task 0 is now uniquely entailed: 26 / 19 / 13 / 6.85 / VV-417530, which is gold.
- In the sweep of all 32 factor docs, each names exactly one target computation. No factor doc has the same omission.

**Regression.**
- Only two docs changed: K1's doc, and billed_month_count's scope line, which now names the converted fill-to and is faithful to the source.
- The other 60 docs are identical in title+content to round 1.
- No new defect was found. The gold-leak scan is clean, and the unlock schemas are unchanged.

**Source-side note.** S1 (the 1200-month sentinel bound, rule-vs-compute wording) is not routed (coordinator DECISION, unreachable on any producible world). It is carried as a note.

KB-VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=S1

## revision_3

**Cross-product re-judge, 2026-10-18.** All seven products are published.

**Gate snapshot** (kb_snapshot.sh, executed only): `DOCS OK (62 docs, tree 51b37d9af0dbf19a)`; `TRACEABILITY OK; non-unlock misses: 0`; all seven instantiate gates OK; hashes aa920acb… / 805a54d8…. I did not run check_traceability myself, and I edited nothing outside my audit directories.

**Conditionality.** Nothing in the round-2 PASS rested on an unpublished product. Each credit reading — receivable ratio, returned-payment count by date, hold reason, payments received by date — matches the now-published credit docs, and both ledgers reconcile to `ar_balance`.

| Task | Runtime | Two-way scan | Dependency form |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

**Source-side items.** These are seed rows another product's rules would not produce. None moves a scored value or a factor tier.
- **S1:** the 1200-month bound. Carried as a note, not routed (coordinator DECISION).
- **S2 (pricing, both tasks).** `annual_spend_commitment` is not the tier's figure: CPA-41207 has 500000.0 against Net-Price's 250000.00, and CPA-44120 has 1500000.0 against Strategic Supply's 3000000.00.
- **S3 (vending, task 0).** VendPoint Locker 24 VP-418377 was installed 19 business days after its request, beyond the 10-business-day lead.
- **S4 (vending, task 0).** Scheduled restock rows are taken at stock far above the low-stock trigger (20% / 30% of par), and several overfill above par. S1 restocks only selections at or below the trigger, and only back to par.
- **S5 (order × credit, both tasks).**
  - Booked order lines never ship, backorder, cancel or invoice.
  - Shipped backorder fills carry no invoice (task 0).
  - order_shipment invoices reference sales orders with no order lines.

**Notes (missing rows, not src, no gold movement).**
- **N1:** VendPoint usage invoices, shortfall, installation and emergency-restock fees (task 0).
- **N2:** the 2025-09 finance charge (task 0).
- **N3:** the 2026-Q3 Net-Price rebate accrual (task 0).
- **N4:** unrecorded anniversary and periodic reviews (both tasks).
- **Band check.** Task 0's credit-room share would need +12369.60 of receivable to move. Task 1's ratio of 1.12 sits deep in its band.

KB-VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=S1,S2,S3,S4,S5

## revision_4

**Seed-rework re-judge, 2026-10-18.**

**Gates.**
- Policy gate: `VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN`.
- kb_snapshot: `DOCS OK (62 docs, tree 51b37d9af0dbf19a)`; `TRACEABILITY OK; non-unlock misses: 0`; all seven gates OK; hashes aa920acb… / 805a54d8… (unchanged).
- The runtime views were refreshed and are byte-identical (64d956a6… / a072a743…).

| Task | Runtime | Two-way scan | Dependency form |
|---|---|---|---|
| 0 | PASS (26 / 19 / 13 / 6.85 / VV-417530) | PASS | PASS |
| 1 | PASS (19 / 8 / 8 / 142.50 / VV-446110) | PASS | PASS |

**Closed.**
- **S2:** both commitments now equal their tier figures.
- **S3:** locker installation is 10 business days.
- **S4:** restocks fill at or below the trigger back to par, and stock reconciles.
- **S5:** every order line resolves, every shipment is invoiced on its ship date, and there are no orphan invoices.
- **N1–N4:** usage bills, shortfall / install / emergency fees, the 2025-09 finance charge, the 2026-Q3 rebate and the reviews are all present and producible.

**Still open.**
- **S1:** carried as a note.
- **S6 (new, order; source-side):** next-day-air shipments in both worlds post with freight 0.00. The published order rule says next day air is "always charged" but gives no amount, so the rule is silent and the seed is 0.00. No scored effect.

KB-VERDICT revision_4: task0=PASS task1=PASS kb=CLEAN src=S1,S6

## revision_5

**Round 5, 2026-10-18.**

**Gates.**
- Policy gate: `VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN`.
- kb_snapshot: `DOCS OK (62 docs, tree 51b37d9af0dbf19a)`; `TRACEABILITY OK; non-unlock misses: 0`; all seven gates OK; hashes aa920acb… / 805a54d8… (unchanged).
- The runtime views were refreshed and are byte-identical.

| Task | Runtime | Two-way scan | Dependency form |
|---|---|---|---|
| 0 | PASS (26 / 19 / 13 / 6.85 / VV-417530) | PASS | PASS |
| 1 | PASS (19 / 8 / 8 / 142.50 / VV-446110) | PASS | PASS |

**S6: closed.** Every next-day-air booking in both worlds is now backordered the next business day and filled by a free-freight method. The fill is freight-free at its level, so freight 0.00 is producible, and no expedite fee arises.

**No regression.**
- Lines all resolve, invoices match shipments, and both ledgers reconcile.
- Rebate, qualifying spend and hold timing are unchanged.
- Task 0's backorder ladders now sit at the stated equality boundary (3 opened, 3 closed), which still gives 1 day and 0.9.

**Open.** S1 is carried as a note (unrouted).

KB-VERDICT revision_5: task0=PASS task1=PASS kb=CLEAN src=S1
