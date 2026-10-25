# KB-doc policy audit — d3_ship_to_orders_backorders_and_returns (product `order`, M=2)

## revision_1 (2026-10-17, fresh KB auditor)

### Entry conditions (cited from the coordinator brief; not re-run by this auditor)
- Policy side: `VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN`.
- check_docs.py env/env_0068_industrial_mro_distributor order → DOCS OK (45 docs; docs tree sha256 prefix 19bd1526d8fe00e4 — recomputed at close over the concatenated sorted docs: 19bd1526d8fe00e4, unchanged).
- check_traceability.py tasks/d3_ship_to_orders_backorders_and_returns → 0.json 21 0 True / 1.json 18 0 True / TRACEABILITY OK.
- Instantiate gates EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; task_tools.py aa4a300d… (re-checked).
- Runtime view and DB access path supplied (db_query.py b5df0dbd…); DB side of the blind audit was tool-shaped (not initial_state). The share write tool verify_caller_identity was read from its docstring only.
- contamination_disclosure: none for either task.

### Per-task part verdicts
| Task | Root ← prerequisite (form) | Runtime blind audit | Two-way scan | Dependency form |
|---|---|---|---|---|
| 0 | stock-rotation return ← anniversary review (action) | PASS (28 units, review → Corbett Priority Ship-To; fall-back 23) | PASS | PASS |
| 1 | requested move up ← reactivation level (state) | PASS (reactivate at Corbett Standard Ship-To, elect Corbett Priority Ship-To; fall-back Route Delivery, no move) | PASS | PASS |

### Closing checklist
- Audit files one-to-one: runtime_context/…/0.md, 1.md; policy_kb/…/0.md, 1.md; each with blind_answer frozen before reveal and gt_comparison appended.
- Every normative atom of the four extended policies (rules, baselines, 20 factor ladders, 5 overwrites with retired surfaces), the nine base policies and the six variant rows has an entailment-equal home; no addition found.
- Both prerequisite sentences verbatim, declared form, on the blocked hub only; each hop resolvable from the sentence, the depended-on hub and the records; no other problem's tool, route or aggregated chain anywhere.
- Every factor ladder complete in its own document, findable from record words; no factor document references another or a computation document.

### Source-side items (src=)
- SRC-1 rule-vs-compute (latent, task-0 sensitive): rotation rule leaves the order of the two non-commuting base adjustments (Category/Net-Price/Cost-Plus narrowing vs StockSmart addition) unstated; compute narrows then adds (28; reverse order 17). KB wording keeps the GT reading.
- SRC-2 parameter descriptions restating retired / excepted clauses: `downgrade_spend_pct` description = retired lifecycle downgrade clause; `return_window_days` description without the rotation exception; rendered verbatim as schedule column definitions.
- SRC-3 base order_ship_to_setup cites "the portfolio allowance in order_agg_ship_to_portfolio", a clause retired by the move-up overwrite (carried on in its replaced_by); KB faithfully points setup readers to a text written retired.

### Observations (placement; stop rule, not verdicts)
- O-1 generic assembly sentences carried in the four computation documents (rotation §C.8, spend test §2.4, ranking clause 4, move-up rule 7), verbatim from the rules.
- O-2 cap document "a higher cap" and tenure-basis "as counted for the review" lean on computation-document quantities without pointing at them.
- O-3 "20000.00" appears in two unrelated hypotheticals; equals task 0's StockSmart 12-month sum by coincidence (not a scored value).

Superseded final line of revision_1: `KB-VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=SRC-1,SRC-2,SRC-3`

## revision_2 (2026-10-17, same auditor; delta re-audit, round 2)

### Gate snapshot (run by this auditor)
- `cat audits/render_source/d3_ship_to_orders_backorders_and_returns/RENDER.log` gives `RENDER round 5: DOCS OK`.
- `grep '^VERDICT' audits/policy_task/d3_ship_to_orders_backorders_and_returns/_difficulty.md | tail -1` gives `VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN`.
- `.venv/bin/python skills/erl-kb-doc-render/scripts/check_docs.py env/env_0068_industrial_mro_distributor order`:
  - `DOCS gate  product=order profile=extended docs=45 roles={'facet': 8, 'factor': 20, 'baseline': 4, 'hub': 4, 'policy': 9}`
  - `[PASS] mechanical gates: …`
  - `DOCS OK`
- `.venv/bin/python skills/erl-task-instantiate/scripts/check_traceability.py env/env_0068_industrial_mro_distributor/tasks/d3_ship_to_orders_backorders_and_returns`:
  - `0.json 21 0 True`
  - `1.json 18 0 True`
  - `TRACEABILITY OK`
- The __pycache__ directories the gates and db_query.py created under env/env_0068_industrial_mro_distributor were deleted.
- Hashes: docs tree (sorted concatenation) 214c6315a52b585e…; order.extended.yaml e78daed4…; task_tools.py aa4a300d… (unchanged); runtime views dd05b4c4… / 9725e9d9… and db_query.py b5df0dbd… unchanged.

### Round-1 items
- SRC-1: **closed**. The source rule and its compute_basis now order narrowing before addition. compute agrees. The KB §C.8 carries the clause verbatim, and the contrary-leaning hypothetical wording was replaced. Task 0 still uniquely gives 28 units.
- SRC-2 and SRC-3: carried as notes (BLUEPRINT-KNOWN; base text rendered verbatim). Not open items.
- O-3 (the "20000.00" coincidence): gone. O-1 and O-2: still placement observations only; the new §C.8 clause is generic.

### Regression check
- Document text diff over all 45 documents: 4 sentences changed, all verified. No title or id change. No new normative claim.
- Gold sweep and unlock schemas: clean.
- Task GT and the task worlds are unchanged.

| Task | Runtime | Two-way scan | Dependency form |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

Superseded final line of revision_2: `KB-VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=NONE`

## revision_3 (2026-10-17, same auditor; cross-product re-judge, all seven products published)

### Gate snapshot (`/tmp/erl0068_coord/kb_snapshot.sh d3_ship_to_orders_backorders_and_returns order`, execute only; check_traceability not run by me)
- `check_docs order: DOCS OK (45 docs, tree 214c6315a52b585e)` (order docs text-identical to revision_2)
- `check_traceability: TRACEABILITY OK; non-unlock misses: 0`
- `gates: EXTENDED OK TASK TOOL CONTRACT OK REPLAY OK SOLVABILITY OK COMPUTE OK GROUNDING OK SCOPE OK`
- Source hashes e78daed4f2c2787a / aa4a300d258f6336.
- The __pycache__ directories my db_query.py runs created under env/env_0068_industrial_mro_distributor were deleted.

### Conditionality
Nothing in the revision_1/2 PASS rested on an unpublished product. The credit and vmi docs (unpublished at round 1) carry the record words the order factors read with the same meaning and enumerations, and no published sentence of another product contradicts an order rule either task applies.

### Seed re-judge (rows of other products in both worlds; details in 0.md / 1.md revision_3)
- **SRC-R3-1 (task 1, gold-moving):** the credit account still shows Net 30 Preferred with last review 2025-04-14. The published 12-month periodic terms review was due 2026-04-14 and would have downgraded the account to Net 30 Standard (on-time 0 % < 90 %). The terms share would then be "in full", the gate 21208.75 is above the measure 20296.53, and the move up fails, against the seeded gold of Corbett Priority Ship-To.
- **SRC-R3-2 (task 1):** the VMI-sourced credit invoices VSO-352002/352056/352128 have no VMI replenishment record. The live Self-Scan program has no monthly minimum fees and no bins. Not gold-moving.
- **SRC-R3-3 (task 1):** CPA-32214's current term (from 2026-04-01) cannot follow from its 2025-02-24 proposal under the 30-day signature window and 12-month term. Not gold-moving.
- **SRC-R3-4 (both):** the Self-Scan programs went live 15 business days after enrollment; the tier allows 10. Not gold-moving.
- **SRC-R3-5 (task 0):** order lines shipped before the Category Contract's first term (2024-12-03 BR-31406 71.28; 2025-06-10 BR-31122 130.24) carry the Category 12 % price, where the Account Price Schedule gives 76.95 / 140.60. They lie outside every scored window. Not gold-moving.
- Clean: every credit invoice, payment, returned payment, fee and finance charge amount and date in both worlds; the BR-31406 competitive-match repricing (61.6000); CPA-31206's dates and commitment.
- Unverifiable (no list-price record): non-contract order-line prices, including the Twinsburg lines behind task 1's measure.
- Round-2 notes SRC-2 / SRC-3 remain BLUEPRINT-KNOWN (not open).

| Task | Runtime | Two-way scan | Dependency form | Seed (src) |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | SRC-R3-4, SRC-R3-5 |
| 1 | PASS | PASS | PASS | SRC-R3-1 (gold-moving), SRC-R3-2, SRC-R3-3, SRC-R3-4 |

Superseded final line of revision_3: `KB-VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=SRC-R3-1,SRC-R3-2,SRC-R3-3,SRC-R3-4,SRC-R3-5`

## revision_4 (2026-10-18, same auditor; re-judge after seed-only reworks, policy rounds 8–10)

### Gate snapshot
- `VERDICT revision_10: task0=PASS task1=PASS charter=CLEAN`.
- Runtime view refreshed with the coordinator's command; both runtime files are byte-identical to before (dd05b4c4… / 9725e9d9…).
- `/tmp/erl0068_coord/kb_snapshot.sh` (execute only):
  - `check_docs order: DOCS OK (45 docs, tree 214c6315a52b585e)`
  - `check_traceability: TRACEABILITY OK; non-unlock misses: 0`
  - all seven gates OK
  - hashes e78daed4f2c2787a / aa4a300d258f6336, unchanged
- Other products' doc trees are unchanged since revision_3.
- The __pycache__ directories my db_query.py runs created were deleted.

### Scored solutions
Re-derived from the docs and the reseeded records. They are uniquely entailed and equal the GT, which is unchanged in value:
- task 0: review → Corbett Priority Ship-To; rotation 28 units at 64.8000 on SO-3104417 / 2 / BR-31406.
- task 1: reactivate → Corbett Standard Ship-To; elect Corbett Priority Ship-To.
No doc or unlock schema carries a scored value.

### Round-3 items
- SRC-R3-1: **closed**. Periodic review recorded 2026-04-14; on-time 95 %, so the tier is kept; the terms share stays 94 %.
- SRC-R3-2: **closed**. 36 VSO billings each invoiced; every month at or above 500.00; 25 bins.
- SRC-R3-3: **closed**. Proposal 2025-03-18, current term 2026-04-01; R8-1 / R9-1 anniversary spend 70163.05 ≥ 56250, so the agreement stays.
- SRC-R3-4: **closed**. Go-live 9 business days after enrollment in both worlds; setup fees on the go-live date.
- SRC-R3-5: **closed for the two named rows** (76.95 / 140.60). Residual SRC-R4-1.
- Also reproducible: task 0's CPA-31206 anniversary 2026-07-01 (104149.45 ≥ 56250, stays), its 2024-11-03 and 2025-11-03 credit reviews (100 %), and every invoice, payment, credit memo, returned payment and finance charge in both worlds (amount, date and due date; ar_balance equals the ledger sum).

### New source-side items (seed; none moves gold)
- **SRC-R4-1 (task 0):** FS-30219 is priced 1.84 both under the Account Price Schedule (2025-03-11, implied list 1.9368) and under the Category 20 % fasteners discount (2026-09-09, implied list 2.30). This is a residual of R3-5.
- **SRC-R4-2 (task 0, order product; present since revision_1, missed there):** Euclid's two Route Delivery drop-ship lines carry no 10.00 drop-ship fee rows or invoices.
- **SRC-R4-3 (task 0):** VMI-31477's go-live month 2023-02 has no program spend and carries no 75.00 monthly minimum fee.
- **SRC-R4-4 (task 1):** setup fee VPF-352900 (250.00) has no vmi_program_fee invoice.

| Task | Runtime | Two-way scan | Dependency form | Seed (src) |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | SRC-R4-1, SRC-R4-2, SRC-R4-3 |
| 1 | PASS | PASS | PASS | SRC-R4-4 |

Superseded final line of revision_4: `KB-VERDICT revision_4: task0=PASS task1=PASS kb=CLEAN src=SRC-R4-1,SRC-R4-2,SRC-R4-3,SRC-R4-4`

## revision_5 (2026-10-18, same auditor; one exhaustive cross-product pass after seed reworks, policy rounds 11–12)

### Gate snapshot
- `VERDICT revision_12: task0=PASS task1=PASS charter=CLEAN`.
- Runtime view refreshed; unchanged at dd05b4c4… / 9725e9d9….
- `kb_snapshot.sh`:
  - `check_docs order: DOCS OK (45 docs, tree 214c6315a52b585e)`
  - `check_traceability: TRACEABILITY OK; non-unlock misses: 0`
  - all seven gates OK
  - hashes e78daed4f2c2787a / aa4a300d258f6336, unchanged
- All seven products' doc trees are unchanged.
- The __pycache__ directories under the scenario were removed.

### Scored solutions
Re-derived, uniquely entailed, equal to the GT:
- task 0: Corbett Priority Ship-To; 28 at 64.8000 on SO-3104417 / 2 / BR-31406.
- task 1: Corbett Standard Ship-To, then Corbett Priority Ship-To.
No doc or unlock schema carries a scored value.

### Exhaustive other-product pass (revision_5, both worlds, one pass)

Method: a scripted check of every other-product row in both worlds against the published rules, plus a hand reading of each rule family.

**Credit, checked row by row:**
- every invoice against its source record (order shipment by order, date and shipment; order service fee; StockSmart scan order; StockSmart fee), and every source record against an invoice;
- due date = invoice date + net days; invoice totals; freight;
- payment application; the prompt-payment discount window; the certified-funds period;
- returned payments and their fees;
- a finance charge recomputed at every month-end (grace, waiver, rate, minimum);
- a credit memo for every received return;
- ar_balance against the ledger;
- past-due hold at the frozen date;
- every periodic terms review back to opening (on-time %).

**Pricing:**
- agreement proposal window, first term, renewal, entry gate and anniversary shortfall review;
- contract item lines, price match, list size;
- order-line unit prices per SKU against the price basis in force on the ship date (Account Price Schedule flat 5 % before the agreement's first term; contract price or Category discount after);
- extended amounts.

**VMI:**
- enrollment, go-live and setup fee; bins; monthly minimum per month; additional-bin, bin-add and par fees;
- go-live-anniversary tier reviews; replenishment freight and invoicing.

**Order:** the ship-to's own fee rows (freight, small order, drop ship, expedite) were rechecked as well.

Closed from revision_4:
- **SRC-R4-1:** FS-30219 2025-03-11 is now 2.1850 = 2.30 × 0.95, the same list as the 2026-09-09 Category price 1.84 = 2.30 × 0.80.
- **SRC-R4-2:** two dropship_fee rows of 10.00 on 2025-10-29 / 2026-05-12, invoiced as order_service_fee (due + 45), paid.
- **SRC-R4-3:** VPF-340901 monthly_minimum_fee 75.00 for 2023-02, invoiced.
- **SRC-R4-4:** INV-3380900 250.00 for VPF-352900, paid.

Clean in both worlds:
- Every invoice ↔ source pair, every due date and total, freight 0.00 (every order at or above its level's threshold; Self-Scan freight under Route Delivery terms).
- No payment falls inside a discount window.
- Returned payment fee 30.00 in each world, and no checks in the certified-funds periods.
- Finance charges: task 1's 9.06 / 9.03 are exactly reproduced; task 0 has none due.
- Credit memos match the received returns.
- ar_balance equals the ledger in both worlds.
- No past-due hold.
- Periodic reviews at 100 / 100 / 100 % (task 0) and 100 / 100 / 95 % (task 1), so neither tier changes.
- Agreement dates, entry gates (61026.10; 95768.15) and anniversaries (104149.45; 70163.05 against 56250).
- Contract item prices and the 61.6000 match.
- Every SKU's implied list is single-valued under the regime in force.
- Go-live 9 business days after enrollment; setup fees; every month's program spend at or above 500.00 (or fee charged); 25 bins at or below 100 included.
- VMI anniversaries: task 0 19185.10 / 19623.50 / 19859.10; task 1 7459.90 / 7207.40 / 7589.80, all at or above 6000 with 25 bins, so both programs stay Self-Scan.
- No order fee due other than the drop-ship fees.

Remaining members (complete list; nothing held back):

| id | World | Rows | Owning rule | Can it move a scored value? |
|---|---|---|---|---|
| **SRC-R5-1** | both | 25 bins with change_type new_bin, all effective in the go-live month (2023-02-24; 2023-10-13). No bin_add_fee row and no fee invoice. | `program_fee_rules` 6: new bins beyond the tier's included adds in the calendar month carry the bin add fee, counted over the new-bin entries effective in the month. `bin_and_par_change_allowances`: Self-Scan includes 5 adds a month, then 4.50 per bin. So 20 × 4.50 = 90.00 for the month (rule 4: one fee of a type per month). The allowances table speaks of bins "the customer may ask to add"; rule 6 counts every new-bin entry, so the literal rule charges the opening bins. | **No.** No order factor reads VMI fees, and the extra invoice does not touch a returned-payment or finance-charge count if paid by its due date. |
| **SRC-R5-2** | both | 43 / 36 vmi_replenishment_billed rows with no vmi_replenishment_delivered row for the same scan order. | `bin_replenishment_and_billing` 1 and 4.2: replenishment is delivered into the bins (within 2 business days on Self-Scan), then billed per scan order. | **No.** The StockSmart factor reads billed lines only; the takeback reads the program's status and tier. |
| **SRC-R5-3** | both | The Category Contract carries 2 contract items (task 0) or 0 (task 1). | `contract_item_list_schedule` / `contract_item_list_rules` (d): a Category Contract carries at least 25 contract items. | **Task 0: only if added items are SKUs Euclid shipped in the scored windows**: their contract prices would replace the Category discount prices, changing review spend and rotation base. Adding items Euclid did not buy moves nothing. **Task 1: No**, because Twinsburg's lines predate the agreement. |
| **SRC-R5-4** | both | Payments that settle an invoice together with its fee or finance charge are applied entirely to the invoice: task 0 WIR-3306104 954.00 → INV-3381206 924.00 (+ CHG-3307710 30.00); task 1 WIR-3201930 1230.00 → INV-3290417 (+ CHG-3202240), ACH-3391402 613.16 → INV-3388052 (+ CHG-3390615 9.06), ACH-3392215 610.83 → INV-3389940 (+ CHG-3391877 9.03). Each invoice is over-applied and each charge shows no payment. | `payment_methods_and_cash_application` 5: a payment is applied to the documents its remittance names (or, without remittance, oldest due first). Neither path over-applies one invoice and leaves its charge open. Totals and ar_balance are correct. | **No.** No factor reads applications, and charges are excluded from finance-charge balances. The open-looking 30.00 / 9.06 / 9.03 are below every hold minimum. |

Notes (not members):
- CM-3305936 369.00 is held on account (its invoice was already paid), and the next payment ACH-3360077 2379.00 draws on it for INV-3340038 2748.00, as `credit_memo_application_and_courtesy_reversal` 2 provides.
- Twinsburg's and MO-30418's implied lists are non-round but single-valued. No list record exists, so these prices are consistent but not independently verifiable.

| Task | Runtime | Two-way scan | Dependency form | Seed members |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | SRC-R5-1, SRC-R5-2, SRC-R5-3 (conditional on fix choice), SRC-R5-4 |
| 1 | PASS | PASS | PASS | SRC-R5-1, SRC-R5-2, SRC-R5-3, SRC-R5-4 (none can move task-1 gold) |

Superseded final line of revision_5: `KB-VERDICT revision_5: task0=PASS task1=PASS kb=CLEAN src=SRC-R5-1,SRC-R5-2,SRC-R5-3,SRC-R5-4`

## revision_6 (2026-10-18, same auditor; closure check after the bounded seed rework, policy round 13)

### Gate snapshot
- `VERDICT revision_13: task0=PASS task1=PASS charter=CLEAN`.
- Runtime view refreshed; unchanged.
- `kb_snapshot.sh`:
  - `check_docs order: DOCS OK (45 docs, tree 214c6315a52b585e)`
  - `check_traceability: TRACEABILITY OK; non-unlock misses: 0`
  - all seven gates OK
  - hashes e78daed4f2c2787a / aa4a300d258f6336, unchanged
- All seven doc trees are unchanged.
- The __pycache__ directories under the scenario were removed.

### Scored solutions
Re-derived, uniquely entailed, equal to the unchanged GT:
- task 0: Corbett Priority Ship-To; 28 at 64.8000 on SO-3104417 / 2 / BR-31406.
- task 1: Corbett Standard Ship-To, then Corbett Priority Ship-To.

### Round-5 members (re-checked on the changed rows; revision_5 was exhaustive over the rest)

- **SRC-R5-1 closed.**
  - VPF-340902 (task 0, 2023-02-28) and VPF-352901 (task 1, 2023-10-31) are bin_add_fee rows: quantity 20, unit 4.50, 90.00, billing period of the go-live month.
  - That is 25 new-bin entries less 5 included adds (`program_fee_rules` 6, `bin_and_par_change_allowances`), one fee row per month (rule 4).
  - Each has its vmi_program_fee invoice, due at invoice date + net days, and is paid.
- **SRC-R5-2 closed.**
  - Every scan order (43 / 36) now has item-level vmi_replenishment_delivered rows on the billing date. Their extended amounts sum exactly to the billed total, and each row's quantity × unit price equals its amount.
  - Every delivered SKU is a set bin, with quantity no more than the bin's max level.
  - Every unit price is the price basis in force on the delivery date. Before the agreement's first term (2025-07-01 / 2025-04-01) it is the Account Price Schedule flat 5 % off list; from then on it is the item's contract unit price (`bin_replenishment_and_billing` 2.2, `price_basis_of_billed_lines`). No mismatch in either world.
- **SRC-R5-3 closed.**
  - Task 0 carries 27 contract items (25 new, all effective 2025-07-01, quoted 2025-06-10, plus BR-31406 / BR-31122); task 1 carries 25 (effective 2025-04-01, quoted 2025-03-18). Both are within the Category range of 25 to 100.
  - Each quote is accepted within the 30-day validity and added on the agreement's first-term start.
  - Each contract price is above supplier cost.
  - No new item is a SKU either ship-to bought, so no order-line price, review spend, rotation base or move-up measure changes.
- **SRC-R5-4 closed.** The payments are now split per document:
  - task 0: WIR-3306104 → INV-3381206 924.00 + CHG-3307710 30.00;
  - task 1: WIR-3201930 → INV-3290417 1200.00 + CHG-3202240 30.00; ACH-3391402 → 604.10 + CHG-3390615 9.06; ACH-3392215 → 601.80 + CHG-3391877 9.03.
  No invoice is over-applied and no charge is left open.

### New-defect check on the changed rows
- The scripted credit sweep from revision_5 was re-run: invoice ↔ source both ways, due dates, totals, finance charges at every month-end, discount windows, certified funds, returned-payment fees, memos, ar_balance (8705.70 / 5908.35 unchanged), holds, and periodic reviews.
  - Task 1: clean.
  - Task 0: one hit, the known on-account artifact. CM-3305936 369.00 is held on account and drawn by ACH-3360077 for INV-3340038, as `credit_memo_application_and_courtesy_reversal` 2 provides. The script does not model that draw, so it is not a defect, as revision_5 found.
- The VMI go-live-anniversary reviews and the monthly minimums are unaffected (delivered rows add no program spend beyond the billed totals).
- The bin count stays 25, at or below the 100 included.
- No new defect.
- Docs and unlock schemas are unchanged; the scored values are unchanged; the gold sweep holds.

| Task | Runtime | Two-way scan | Dependency form | Seed members |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | none |
| 1 | PASS | PASS | PASS | none |

KB-VERDICT revision_6: task0=PASS task1=PASS kb=CLEAN src=NONE
