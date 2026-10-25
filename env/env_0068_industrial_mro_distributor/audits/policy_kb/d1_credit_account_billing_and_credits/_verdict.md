# KB-doc policy audit — d1_credit_account_billing_and_credits (product credit) — closing

## revision_1

Auditor: a fresh KB auditor, not the renderer or the policy auditor. Entry conditions were supplied with the brief and confirmed:
- policy verdict `VERDICT revision_13: task0=PASS task1=PASS charter=CLEAN`
- the gate snapshot
- the runtime views (ac090162…, 079187c6…)
- db_query.py (b5df0dbd…)

Final-form snapshot, re-run through `/tmp/erl0068_coord/kb_snapshot.sh d1_credit_account_billing_and_credits credit`:
- `check_docs credit: DOCS OK (50 docs, tree 2971b6b5ce969a27)`
- `check_traceability: TRACEABILITY OK; non-unlock misses: 0`
- gates `EXTENDED OK TASK TOOL CONTRACT OK REPLAY OK SOLVABILITY OK COMPUTE OK GROUNDING OK SCOPE OK`
- hashes 96e73223486d52f3 (charter) and ab50360b67d22456 (task_tools)

contamination_disclosure: none. The blind answers were frozen before the reveal (task0.md 13da1232…, task1.md 01c642a5…).

| Task | Runtime blind audit | Two-way scan | Dependency form |
|---|---|---|---|
| 0 | PASS: every scored argument equals gold (128.08; 2550.42) | PASS | PASS |
| 1 | PASS: every scored argument equals gold (191236.72; approved_reduced 149087.00) | PASS | PASS |

Closing checklist:
- Each task has its own audit files.
- Every atom of the 4 extended policies (19 factor ladders, 4 baselines, 2 state-form prerequisites, 4 overwrites) is entailed by docs/credit.
- The retired surface is correct: 3 cash-discount clauses and 1 limit-review clause are marked retired, and their sibling clauses stay in force.
- Each prerequisite sentence stands verbatim only on its blocked hub.
- No tool name, route or chain appears beyond those sentences.

KB-side REDs: none.

## Source-side items (src=). None is a KB defect; all are listed as the brief requires.

- **SRC-1 (placement, assembly sentences):** All four extended rules contain a generic assembly sentence that announces modifying schedules:
  - backorder room: "Every amount a schedule in this rule adds is added to the receivable balance … every percentage point a schedule adds is added to the tolerance percentage used, and the tolerance percentage used never exceeds …"
  - request figure: "Every amount a schedule in this rule adds is added to the monthly purchase base, and every percentage a schedule sets multiplies the supported limit …"
  - grant: "Every percentage point a schedule in this rule adds to or takes from the step percentage used …"
  - catch-up: "Every share of the discount rate this rule sets multiplies the tier's percentage …"

  The renderer carried them verbatim in the computation docs: room_payment_amount §3, supported_limit_figure "Combination", granted_permanent_limit Grant 3 and catch_up_discount_amount §3.3. There a reader learns that variations exist, though none is named. The blind audit was not pre-solved by them, because every factor was reached from record words. This is the known placement-only class.

- **SRC-2 (seed, cross-product vmi, moves gold in task 1):** The seed has a StockSmart `par_change_fee` row on VMI-16408: 12.00, quantity 12, dated 2026-08-31.
  - Under the published vmi rules, a par change fee is charged only per par-change bin entry beyond the tier's included changes in the month (program_fee_rules §6). For StockSmart Weekly Service, bin_and_par_change_allowances sets 40 included changes and 1.00 per change beyond.
  - So the row implies 52 par-change entries in August 2026. find_vmi_bins returns no bins and no par-change entries for the program or the customer.
  - The row feeds stocksmart_program_allowance: 1212.00 instead of 1200.00, so the granted limit is 149087.00 instead of 149075.00.

- **SRC-3 (seed, cross-product order, moves gold in task 0):** Two return credit memos have no Ship-To return records:
  - CM-130418 (RMA-1530418, 1860.00 on INV-1488218)
  - CM-129966 (RMA-1529966, 742.15 on INV-1488081)

  find_order_returns returns nothing for the customer or ship-to ST-14082. Both credits equal the full shipped lines (3 x 620.00; 5 x 148.43). On a Corbett Route Delivery Ship-To, the published return terms produce a full credit only for a Corbett-error return. A customer-reason return carries a 10 percent restocking fee (minimum 5.00), per return_fee_credit_schedule. The return reason and receipt the order rules require are missing. CM-130418 feeds discountable_merchandise_deduction (59390.00).

- **SRC-4 (seed thinness, both tasks, not gold-moving):**
  - VendPoint usage bills exist with no vend rows. The vending rules derive a usage bill from net vends and test the shortfall fee on net vend value.
  - Usage bills and cellular data fees are missing for the months since installation:
    - VP-118204: installed 2025-11-03; bills and fees only from 2026-06.
    - VP-116052: installed 2025-05-12; bills only from 2026-08.
  - StockSmart monthly minimum fees are missing before 2026-07 (VMI-13306, live since 2024-02-05) and before 2026-06 (VMI-16408, live since 2025-03-03).
  - Monthly order_shipment invoices of 35k–66k stand behind few order lines (task 0) or none (task 1).
  - The credit factors read only the windows that are seeded, so no scored value moves.

- **SRC-5 (parameter descriptions vs overwrite):**
  - The `limit_increase_max_step_pct` description ("Largest permanent limit increase granted in one review, percent of the current permanent limit") is rendered in credit_limit_and_review_schedule (row and definition 5). It still reads as a cap, but under credit_ext_permanent_increase_grant the step room can exceed it (+10 / +5 points, allowances).
  - Similarly, the `cash_discount_partial_payment` and `cash_discount_pct` descriptions in terms_and_cash_discount_schedule restate the base pro-rata and merchandise-subtotal semantics. These are replaced for in-scope invoices.

  The docs carry the source verbatim, and the replacing sentences are explicit ("replaces the tier's flat step percentage for every permanent request"; "in place of …"). Neither task's numbers are affected.

- **SRC-6 (rule wording, catch-up out-of-scope record test):** The catch-up rule's out-of-scope branch narrows the base clause's "agreement … whose status is active on the invoice date" to a test on the current record. The phrase is "which the records show as the customer's live agreement recorded on such a tier with status active, the only agreement status and tier the records hold". It is rendered verbatim in catch_up_discount_amount §4. It is not triggered here (INV-1488218 is in scope).

KB-VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=SRC-1,SRC-2,SRC-3,SRC-4,SRC-5,SRC-6


## revision_2 (re-audit round 2; revision_1 above left untouched)

### Gate and snapshot
- `VERDICT revision_14: task0=PASS task1=PASS charter=CLEAN` confirmed.
- Runtime views refreshed; hashes unchanged.
- kb_snapshot:
  - `check_docs credit: DOCS OK (50 docs, tree 2971b6b5ce969a27)`
  - `check_traceability: TRACEABILITY OK; non-unlock misses: 0`
  - `gates: EXTENDED OK TASK TOOL CONTRACT OK REPLAY OK SOLVABILITY OK COMPUTE OK GROUNDING OK SCOPE OK`
  - hashes 96e73223486d52f3 / ab50360b67d22456
- Docs tree, charter and tools are unchanged.

contamination_disclosure: round 1 revealed GT, so revision_2 is a fresh re-derivation from docs and records, not a blind audit. The new task JSONs were read only after the figures were computed.

| Task | Fresh solution | Gold | Runtime | Bijection | Dependency form |
|---|---|---|---|---|---|
| 0 | discount 128.08; room payment 2619.61 (moved from 2550.42 by the reworked invoice tax: ratio 0.077529) | same | PASS | PASS | PASS |
| 0 | cross-product rows | — | returns, freight, StockSmart and VendPoint rows now produced by their published rules | — | — |
| 1 | request 191236.72; approved_reduced 149075.00 (moved from 149087.00 by removal of the unsupported par change fee) | same | PASS | PASS | PASS |

### Status of round-1 source items
- **SRC-2:** CLOSED. The par change fee row was removed. The StockSmart allowance is 1200.00 from 3 monthly minimum fees.
- **SRC-3:** CLOSED. Ship-To return records now back both credit memos. They are Corbett-error returns with route pickup, so full credit with no restocking or label fee, issued in 3 business days.
- **SRC-4:** CLOSED. Order lines, program fees, vends, usage bills and cellular fees are seeded across the full history. Every consolidated invoice now reconciles exactly to shipped lines + program bills.
- **SRC-1:** carried as a note, not routed. These are assembly sentences in the computation docs, a placement-only class; the docs are unchanged.
- **SRC-5:** carried as a note (BLUEPRINT-KNOWN). These are base parameter descriptions surviving the overwrites.
- **SRC-6:** carried as a note (BLUEPRINT-KNOWN). This is the base's own reading of agreement status in the catch-up out-of-scope branch.

### New or regressed
- No new KB defect and no regression.
- No document example or unlock schema equals a new scored value or intermediate.
- Every factor tier is unchanged except the moved inputs noted above.
- Policy-side note (not a KB item): in task 1, the StockSmart billed-fee-sum tier now gives the same 1200.00 as the commitment-projection tier would.
- Residual note: sales tax amounts and item prices are not fixed by any published rule, so they remain free seed inputs.

KB-VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=NONE
