# Runtime-context blind audit — d1_credit_account_billing_and_credits / task 0

## revision_1

## blind_answer

- Freeze declaration: this section was written to disk before any source-layer artifact (extended yaml, task JSON, plan.md, worklog.md, task_tools.py, blueprint/products, audits/) was opened. It is not edited after the reveal.
- Freeze time: 2026-10-17T23:2xZ (UTC). Auditor: fresh KB auditor (not the renderer, not the policy auditor).
- Visible materials used: docs/credit/*.json title+content (50 docs; sha256 of `sha256sum *.json` listing = e6336789…; coordinator check_docs prefix 2971b6b5ce969a27); runtime view task0.runtime.json (sha256 ac090162…; frozen_time 2026-10-14 09:35:00 EDT + user_scenario); blueprint.yaml `company`/`background` text only (system background); share-tool docstrings of verify_caller_identity / transfer_to_human_agent (extracted with ast, docstrings only, no bodies); db_query.py (sha256 b5df0dbd…) share read tools, KB_search and unlock_* on a fresh engine of task 0; cross-product docs read for seed realism only: docs/vmi monthly fee schedule, statement of program charges, bin/par allowances; docs/vending minimum usage, placement terms, program fees, usage invoicing; a KB_search hit of docs/order returns terms.
- Forbidden and not opened: *.extended.yaml, tasks/*/tasks/*.json, plan.md, worklog.md, task_tools.py, initial_state, docs meta, blueprint/products charters, share_tools.py function bodies, audits/*. No recursive grep over tasks/ or the scenario root was run (only a grep restricted to docs/ for candidate gold figures, after computing them).
- contamination_disclosure: none. The brief carried no scored value.

### 1. User expression and simulator role
The caller (Theresa Caldwell, account C-152846, ZIP 43123) wants to make a payment today by bank debit so that, once the SO-1826504 backorders ship and the month-end program bills land, the credit account "stays inside what Corbett allows and nothing gets held". She does not know the amount ("whatever amount Corbett says keeps you clear"), authorizes anything that must be "booked or corrected on the account first", and will run the payment herself when handed over. The simulator is passive: conveys need, gives credentials, executes the user tool with the stated amount.

### 2. Act / wait / refuse at the frozen moment
Act now. Grounds: verify_caller_identity docstring ("verification must pass before any account record is discussed"; at least 2 credentials match; account number + ZIP suffice). Account status `active`, hold_reason none. The room-payment doc (backorder_room_payment_by_bank_debit_2c6d0a0a) defines exactly this request: "A customer who wants room on the credit line for backordered goods still to ship pays a room payment by bank debit ... the amount that keeps the account within its room ceiling once those goods ship and the month-end program billing posts."

### 3. Objects and correlation keys
- Customer f26d79fa…; credit account c8e9f8b6-5c50-455e-9574-22d5be504456, Corbett Net 45 Business Account, limit 90000.00, ar_balance 81620.75, monthly_consolidated, opened 2009-06-02.
- Most recent payment entry: ACHTR-1608314, received 2026-10-08, 40000.00, applied to INV-1488218 (dated 2026-09-30, merchandise 61250.00, freight 318.60, tax 4455.94, total 66024.54). No other payment entry on 2026-10-08. No discount line exists anywhere on the account.
- INV-1488218 also carries CM-130418 (return_credit, RMA-1530418) 1860.00 dated 2026-10-02. No dispute on the account.
- Live CPA: CPA-15204 Corbett Category Contract, active, 2025-07-01..2027-06-30, commitment 75000.00 (invoice date inside the term).
- Finance charges: FC-1250930 2025-09-30 (12 whole months before 2026-10-14 -> not "less than twelve") and FC-1260430 2026-04-30 (5 whole months -> counted): exactly one.
- Returned payment RTN-1260320 2026-03-20 (6 whole months -> inside the 12-month lookback). Account age 208 whole months (>=120).
- Backorders on ST-14082: BO-160881 10624.80 open, BO-160882 3854.00 open, BO-160883 2240.00 filled 2026-10-06, BO-160884 735.00 customer-cancelled -> open 14478.80 (matches ship-to open_backorder_value). ST-14097 none.
- StockSmart VMI-13306 (Weekly Service, active): monthly_minimum_fee 400.00 dated 2026-07-31, 08-31, 09-30 (2, 1, 0 whole months).
- VendPoint VP-118204 (Coil 40, cellular, active): usage bills 06-30 1318.40 (3 whole months, excluded), 07-31 1412.60, 08-31 1288.35, 09-30 1530.90; cellular data fees 15.00 each month; fee dated <1 whole month: 09-30 15.00.
- Sales tax: latest invoice date 2026-09-30, one invoice that day (INV-1488218): ratio 4455.94/61250.00.

### 4. Scored parameters
(a) Catch-up discount line (book before the room payment, see item 6):
- Scope: INV-1488218 dated inside the live Category Contract term -> catch_up_discount_amount §3 applies.
- Discount rate = tier 1% x contract share (Category Contract: three quarters, contract_pricing_tier_and_discount_rate) x payment-record share (exactly one finance charge in <12 whole months: one half, finance_charge_record_and_discount_rate) = 0.375%.
- Merchandise the payment pays for (short_payment_merchandise_allocation): left open = 66024.54 - 40000.00 - 1860.00 = 24164.54 > 1% x 61250.00 = 612.50; Net 45 allows partial-payment discounts -> 40000.00 - 318.60 - 4455.94 = 35225.46.
- Discountable merchandise (disputed_and_returned_merchandise_in_discounts): no open goods dispute; return credit 1860.00 applied -> 61250.00 - 1860.00 = 59390.00.
- Figure = 0.00375 x 35225.46 x 59390.00/61250.00 = 128.0840... -> **128.08** (rounded only on the final figure).
- Booking args: credit_account_id c8e9f8b6…, applied_invoice_number INV-1488218, payment_reference ACHTR-1608314, payment_date 2026-10-08, discount_amount 128.08. Receivable after booking 81492.67.
(b) Room payment:
- Receivable balance 81492.67 (after the discount line).
- Open backorder value counted = 14478.80 x (1 + 4455.94/61250.00) = 15532.1333 (sales_tax_on_open_backorders: monthly consolidated, tax billed in last 12 whole months -> latest-invoice-date ratio).
- StockSmart billing still to post = whole of recurring fees <1 whole month = 400.00 (fees in all three months; stocksmart_fees_in_room_payment).
- VendPoint billing still to post = (1412.60 + 1288.35 + 1530.90)/3 + 15.00 = 1425.6167 (usage billed two whole months before today, not rising in all three: 1412.60 > 1288.35; vendpoint_billing_in_room_payment).
- Tolerance used = 10% x one half (exactly one of: opened <120 months [no], returned payment in lookback [yes]; tenure_and_returned_payments_tolerance) = 5 + 2 points (commitment 75000.00 in 25000..249999.99; committed_spend_tolerance_points) = 7% (never above tier 10%). Room ceiling = 90000.00 x 1.07 = 96300.00.
- Room payment = 81492.67 + 15532.1333 + 400.00 + 1425.6167 - 96300.00 = 2550.41996 -> **2550.42**.
- Tiers rest on: CPA record (pricing product), ship-to backorder entries (order product), StockSmart fee rows (vmi product), VendPoint usage/fee rows (vending product), credit transactions.

### 5. Tool sequence
1. find_customers(account_number C-152846) -> verify_caller_identity(customer_id, account_number C-152846, billing_zip 43123) [agent, share write].
2. Read tools: find_credit_accounts, find_credit_transactions, find_pricing_agreements, find_ship_to_accounts, find_order_lines, find_vmi_programs, find_vmi_activity, find_vending_machines, find_vending_transactions, find_credit_disputes.
3. unlock_agent_discoverable_tool(book_cash_discount_2280b564) -> call with the args in 4(a) [agent].
4. unlock_user_discoverable_tool(pay_by_bank_debit_4d9f44ce) -> tell customer credit_account_id c8e9f8b6… and payment_amount 2550.42; customer runs it [user]. Terminal: payment received (ACH-…), ar_balance 78942.25.

### 6. Problem tree from the visible materials
- Root (customer's write): room payment by bank debit.
- Hop 1 (state-derived): backorder_room_payment doc: "The room payment is worked out only after the account's most recent payment carries a discount line on the invoice it is applied to, wherever a catch-up discount above nothing is owed for that payment under the prompt-payment discount rule". Records: latest payment ACHTR-1608314 on INV-1488218 received day 8 after the invoice date (Net 45 window 10 days, terms_and_cash_discount_schedule), no discount line on the account -> state does not hold and a discount above nothing (128.08) is owed. Searching "discount line" / "most recent payment" finds catch_up_cash_discount_booking ("Corbett books that discount as a catch-up discount line when the account's most recent payment earned it and the invoice that payment is applied to carries no discount line"), whose own tool books it; amount from catch_up_discount_amount + factor docs. Not named on the room side; reasoning combined the state sentence + the booking doc + records.
- Hop 2: identity verification (share docstring, precondition of any business).
- Order: verify -> book discount line -> compute room payment on the post-discount balance -> hand pay tool to customer.
- Counter-proof "do only what was asked": paying without the discount line is excluded by the room-side sentence (the figure rests on an account whose records show the discount line); the amount would also differ (2678.50 on the pre-discount balance).

### Two-way counter-proof and fall-backs
- Closest alternatives excluded: base cash-discount rule (outside-scope §4: 612.50 x 40000/66024.54 = 371.07) excluded by §2.1/§2.2 (invoice inside live CPA term). FC-1250930 excluded by "less than twelve whole months" (doc example: 15 June previous year, 12 months, not counted). 06-30 VendPoint usage excluded (3 whole months). Filled/cancelled backorders excluded by room_payment_amount §2. Tolerance points capped at tier 10% (not reached).
- Fall-back of the room payment computation doc alone: 81620.75 + 14478.80 - 99000.00 < 0 -> 0.00 (also 0.00 with the baseline discount); differs from 2550.42. Fall-back of the catch-up discount doc alone (§3 defaults: rate 1%, discountable = paid-for = whole merchandise): 612.50; differs from 128.08.
- Factor findability (records' words -> doc): return_credit memo on the invoice -> "Disputed Shortages and Returned Goods in the Discountable Merchandise"; partial payment leaving 24164.54 open -> "Short and Partial Payments: Merchandise Paid For"; Corbett Category Contract record -> "Contract Pricing Agreement Tier and ... Discount Rate"; finance_charge rows -> "Finance Charge History and the Prompt-Payment Discount Rate"; credit_payment_returned row + opened_date -> "Account Age, Returned Payments and ... Room Tolerance"; annual_spend_commitment -> "Committed Annual Spend and Room Tolerance Points"; tax_amount on invoices -> "Sales Tax Gross-Up of Open Backorders"; StockSmart monthly_minimum_fee rows -> "StockSmart Recurring Program Fees Still to Post"; VendPoint usage/cellular rows -> "VendPoint Usage Billing Still to Post". All titles name the official product and the record kind.
- Pre-solving observations for Step 3b: the computation docs carry generic assembly sentences that announce modifying schedules (room_payment_amount §3 "Every amount a schedule in this rule adds…"; catch_up_discount_amount §3.3 "Every share of the discount rate this rule sets multiplies the tier's percentage"). They did not name any factor or tell me which applies, but they do tell the reader that variations exist. Judged after reveal.
- Policy-side/seed observations (not used to change the answer): CM-129966 / CM-130418 return credits reference RMA-1529966 / RMA-1530418 but find_order_returns returns no record; VendPoint usage bills exist with no vend rows and cellular fees only from 2026-06 although installed 2025-11-03; StockSmart fees only from 2026-07 though live since 2024-02-05; invoice merchandise of ~50k/month with only a handful of order lines.

## gt_comparison
(appended after reveal; see below)

### revision_1 gt_comparison (appended after the reveal; blind_answer above untouched)
- Freeze record: blind files written 2026-10-17 ~23:17Z (the "23:2xZ" in the header is a typo for the actual disk time); sha256 at freeze task0.md 13da1232…, task1.md 01c642a5…. Reveal at 2026-10-17T23:18:46Z: credit.extended.yaml, task_tools.py (ab50360b…), tasks/0.json read.
- Write actions, gold vs blind:
  - verify_caller_identity(f26d79fa…, C-152846, 43123): SAME.
  - book_cash_discount_2280b564(c8e9f8b6…, INV-1488218, ACHTR-1608314, 2026-10-08, 128.08): SAME (gold 128.08, raw 128.0841).
  - pay_by_bank_debit_4d9f44ce(c8e9f8b6…, 2550.42), user-owned: SAME (gold 2550.42).
- Factor tiers, gold factor_trace vs blind: payment allocation tier 1 (35225.46) SAME; record share one half SAME (FC-1250930 excluded at exactly 12 whole months SAME); contract share three quarters SAME; discountable merchandise 59390.00 SAME; tolerance share one half SAME; sales-tax ratio latest-invoice-date SAME (15532.13); StockSmart whole share 400.00 SAME; contract points 2 SAME (7 percent, ceiling 96300.00); VendPoint three-month average + 15.00 = 1425.62 SAME; receivable after discount 81492.67 SAME.
- Fall-backs: gold baseline_result 612.50 (discount) and 0 (room payment) = blind fall-backs.
- Problem tree: gold prerequisite_closure root credit_ext_backorder_room_payment -> credit_ext_window_discount_catchup (state form, value_input) = blind tree (hop state-derived). No hop was pre-solved.
- Verdict: KB-RUNTIME PASS.


## revision_2 (re-audit after the seed-only rework; revision_1 above is left untouched)

### contamination_disclosure
Round 1 revealed the source layer and GT, including the old gold of 2550.42 / 149087.00. So this is not a blind audit. It is a fresh re-derivation from the docs and from records re-queried through db_query.py on fresh engines. The new tasks/0.json was opened only after the new figures below had been computed.

### Gate and views
- `VERDICT revision_14: task0=PASS task1=PASS charter=CLEAN`.
- Runtime views refreshed from the task JSON: hashes unchanged (ac090162…, 079187c6…). frozen_time and user_scenario are unchanged.
- kb_snapshot:
  - `DOCS OK (50 docs, tree 2971b6b5ce969a27)`
  - `TRACEABILITY OK; non-unlock misses: 0`
  - all 7 gates OK
  - charter 96e73223486d52f3 and task_tools ab50360b67d22456 unchanged
- docs/credit listing hash e6336789… unchanged.

### What the seed rework changed (record diff against round-1 query dumps)
- **credit_transactions:** 9 invoices got new freight/tax splits with unchanged totals and merchandise. Freight is now 12.95 per Standard Ship-To shipment month (INV-1488218: 25.90; tax 4748.64). Nothing else changed.
- **Order lines:** 12 -> 192 rows: booked / shipped / standard_freight fee rows for every month. For every consolidated invoice, merchandise = shipped lines + StockSmart fee + VendPoint usage + cellular fee, exactly. The four SO-1826504 backorders are unchanged.
- **order_returns:** 0 -> 4 rows: RMA-1529966 and RMA-1530418, both authorized and received, reason wrong_item_shipped, route_pickup, restocking 0.00, label 0.00, credits 742.15 / 1860.00.
- **vmi_activity:** 3 -> 32 monthly minimum fees, 2024-02 .. 2026-09.
- **vending_transactions:** 63 vend rows; 11 usage bills and 11 cellular fees, 2025-11 .. 2026-09. Bills are per cost center CC-1140 and equal the month's vends.

### Fresh working
- **Catch-up line:** INV-1488218 left open = 66024.54 - 40000.00 - 1860.00 = 24164.54 > 612.50.
  - Paid-for merchandise = 40000.00 - 25.90 - 4748.64 = 35225.46 (freight + tax total unchanged at 4774.54).
  - Rate 1% x 0.75 x 0.5; discountable 59390.00.
  - **128.08** (unchanged). Arguments: INV-1488218 / ACHTR-1608314 / 2026-10-08.
- **Room payment:**
  - Receivable 81620.75 - 128.08 = 81492.67.
  - Open backorders 14478.80 x (1 + 4748.64/61250.00) = 15601.3242. The sales-tax ratio is 0.077529, and this moved the figure.
  - StockSmart billing still to post 400.00; VendPoint billing still to post (1412.60 + 1288.35 + 1530.90)/3 + 15.00 = 1425.6167.
  - Ceiling 90000.00 x 1.07 = 96300.00.
  - Result **2619.61** (raw 2619.6109).
- **Fall-backs:** 612.50 / 0.00. Paying without the discount line would give 2747.69.
- **Factor tiers:** all unchanged from revision_1. The only moved input is the tax amount behind the sales-tax ratio.

### gt_comparison (revision_2)
- Gold book_cash_discount (…, INV-1488218, ACHTR-1608314, 2026-10-08, 128.08): SAME.
- Gold pay_by_bank_debit (…, 2619.61): SAME.
- Gold baseline 0 and factor sensitivities (backorder_sales_tax_ratio baseline 1497.09; the others) are consistent with the fresh working.
- Problem tree unchanged (state-derived hop).
- **KB-RUNTIME PASS.**
