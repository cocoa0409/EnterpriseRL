# Policy-KB bijection audit — d1_credit_account_billing_and_credits / task 0

## revision_1

Scope: credit_ext_backorder_room_payment (root, on_request, pay_by_bank_debit_4d9f44ce) and credit_ext_window_discount_catchup (state_due, book_cash_discount_2280b564), their base policies credit_evt_cash_discount (3 clauses retired), credit_evt_payment_methods and credit_hold_and_collections, the variants they read, and the two task tools. Source: credit.extended.yaml (charter sha 96e73223…), task_tools.py ab50360b…. Docs: docs/credit (50; check_docs tree 2971b6b5ce969a27). Gates re-run on the final form by `/tmp/erl0068_coord/kb_snapshot.sh` at close: `DOCS OK (50 docs, tree 2971b6b5ce969a27)`, `TRACEABILITY OK; non-unlock misses: 0`, gates EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK.

## source_to_kb

### credit_ext_window_discount_catchup
| Source atom | KB home | Judgement |
|---|---|---|
| Rule opening: discount earned inside the window; catch-up line booked when the latest payment earned it and its invoice has no discount line | catch_up_cash_discount_booking (hub) opening + table | equivalent |
| Payment/invoice concerned; tie on latest received date -> nothing; payment amount; invoice total | catch_up_discount_amount §1.1–1.2; worked row "two payment entries share the latest received date" | equivalent |
| Scope: invoice inside the current term of the one live (active / renewal pending) CPA; other invoices -> base figure, including no live or more than one live agreement | catch_up_discount_amount §2.1, §4; every factor doc repeats the scope | equivalent |
| Overwrite 1 replaced_by | catch_up_discount_amount §2.2 | verbatim |
| Overwrite 2 replaced_by | short_payment_merchandise_allocation "Rule" para 1; catch_up_discount_amount §4 (base figure out of scope) | equivalent |
| Overwrite 3 replaced_by | contract_pricing_tier_and_discount_rate clause; catch_up_discount_amount §4 | equivalent |
| Baseline rule (rate = tier %, discountable = merchandise subtotal, paid-for = whole subtotal, proportion, final rounding) + "Every share … multiplies the tier's percentage …; no merchandise earns nothing" | catch_up_discount_amount §3.1–3.3 | verbatim; default constants carried |
| What is left open (net of payments, memos, discount lines, write-offs, plus reversals; unrounded) | catch_up_discount_amount §1.3; short_payment doc | verbatim |
| Factor payment_allocation_to_merchandise (method, 3 tiers) | short_payment_merchandise_allocation: rule + allocation table + five boundary cases | full ladder, every tier |
| Factor payment_record_share_of_rate (0 / one half / whole; <12 whole months) | finance_charge_record_and_discount_rate: clause, schedule, whole-month convention, counting examples incl. 12-month boundary | full ladder |
| Factor contract_share_of_rate (net-priced 0 / Category or Volume 75 / other 100) | contract_pricing_tier_and_discount_rate: clause, excluded-tier list, schedule, renewal-pending Q&A | full ladder |
| Factor discountable_merchandise_deduction (open goods dispute / return credits / subtotal) | disputed_and_returned_merchandise_in_discounts: clause, Q&A, cases | full ladder |
| Tool contract book_cash_discount_2280b564 (5 params, return fields, no eligibility check) | hub "Booking the line" + parameter table + Q&A | equivalent to docstring |
| Retired surface: 3 superseded clauses of credit_evt_cash_discount | prompt_payment_cash_discount_terms "Retired clauses" (all three, marked no longer in force); the other clauses (window, counting, zero-day tier, short-paid) carried as "Clauses in force" | correct |

### credit_ext_backorder_room_payment
| Source atom | KB home | Judgement |
|---|---|---|
| Rule opening (room payment by bank debit, no remittance detail, amount keeping the account inside its room ceiling once backorders ship and month-end program billing posts) | backorder_room_payment_by_bank_debit (hub) opening | verbatim |
| Baseline rule (receivable + open backorders counted - room ceiling, floor 0, final rounding; open backorders = backordered - filled - cancelled at booked prices; ceiling = limit x (1 + tier tolerance)) | room_payment_amount §1–2 + inputs table + worked figure | verbatim; tolerance named and found in credit_limit_and_review_schedule |
| Assembly sentence (amounts add to receivable + backorders; points add to tolerance used; never above tier tolerance) | room_payment_amount §3 | verbatim (see SRC-1) |
| Factor tolerance_share_by_tenure_and_returns (4 rows) | tenure_and_returned_payments_tolerance | full ladder, 120-month and lookback boundaries |
| Factor backorder_sales_tax_ratio (consolidated / per shipment / zero; zero merchandise) | sales_tax_on_open_backorders | full ladder |
| Factor stocksmart_month_end_billing (whole / half / quarter; recurring fees definition) | stocksmart_fees_in_room_payment; names StockSmart Vendor-Managed Inventory Program and fee kinds | full ladder |
| Factor contract_tolerance_points (5 / 2 / 0 at 250000 / 25000) | committed_spend_tolerance_points | full ladder with boundaries |
| Factor vendpoint_month_end_billing (method: floored trend / 3-month average / latest month / nothing; cellular fees) | vendpoint_billing_in_room_payment; names VendPoint Industrial Vending Program, usage bills, cellular data fees, model minimum usage | full ladder; model minimum found in docs/vending minimum_usage_schedule (Coil 40 1250.00) |
| Tool contract pay_by_bank_debit_4d9f44ce (user-owned) | hub "Making the payment" | equivalent |
| Base: credit_evt_payment_methods (no-remittance application, certified funds), credit_hold_and_collections (over-limit tolerance) | payment_methods_and_cash_application; payment_acceptance_schedule; credit_hold_and_collections_referral; hold schedule | equivalent |

### prerequisite (room payment -> catch-up)
- policy_source (state form): "The room payment is worked out only after the account's most recent payment carries a discount line on the invoice it is applied to, wherever a catch-up discount above nothing is owed for that payment under the prompt-payment discount rule; where none is owed, the room payment waits on no discount line."
- Carried verbatim in backorder_room_payment_by_bank_debit (hub of the blocked policy), section "When the room payment is worked out"; a same-form restatement follows ("Put another way: … the room payment figure rests on an account whose records show that discount line …"). Connective "only after", strength (hard wait, conditional on a discount above nothing) and form (state) intact.
- Resolution basis: catch_up_cash_discount_booking describes, in the same words ("discount line", "most recent payment", "the invoice that payment is applied to"), the write that books the line; amount from catch_up_discount_amount + factor docs; records show ACHTR-1608314 on INV-1488218 with no credit_cash_discount_taken entry.
- No other policy's document carries the sentence (content grep for "room payment" hits only the room-payment hub, its baseline and its own factor docs). condition / resolved_by / effect have no home in any document.

## kb_to_source
- Every normative sentence of the 27 extended-policy docs and the base docs read traces to the extended rule, a replaced_by, a base rule, a parameter_schema description, a variant figure or a tool docstring. Derived restatements checked: "Other program fees (setup, emergency visit, trip, bin and change fees, early exit) are not recurring fees" (entailed by "meaning the monthly minimum and onsite management fees"); "An agreement in any status other than active earns no points" (entailed by "active"); hub contract note "The tool records the amount it is given" (tool docstring + rule). All hypothetical examples recomputed; none equals a scored value (128.08, 2550.42, intermediates 59390.00, 35225.46, 15532.13, 96300.00 absent from docs/).
- Additions / rewrites / omissions: none found.
- Cross-problem operational guidance: none (each tool name appears only in its own policy's hub; no "first call", route or chain).
- Opening world state written as policy fact: none.
- Unlock schemas (book_cash_discount_2280b564, pay_by_bank_debit_4d9f44ce) carry no figure.

## bijection_verdict
KB-BIJECTION PASS (revision_1). Source-side items recorded for the verdict line: SRC-1 (assembly sentences that the source rule itself places in the computation; rendered in room_payment_amount §3 and catch_up_discount_amount §3.3), SRC-3 (seed), SRC-4 (seed), SRC-5 (parameter descriptions), SRC-6 (catch-up out-of-scope record test). See _verdict.md.

## dependency_form
- Prerequisite sentence verbatim on the blocked side, state form, and its same-form restatement only: not RED.
- No state-form sentence restated as an action; neither the catch-up tool nor its policy is named in the room-payment documents; the catch-up documents do not mention the room payment.
- No aggregated table, checklist or route; no FAQ walking across the two problems; no wrong-vs-right contrast across problems.
- Titles: "Room Payments for Backordered Goods on the Commercial Credit Account" names the on_request subject; "Catch-Up Prompt-Payment Discount Lines …" general. No task mirroring.
- Factor docs: none says which tier a customer falls on, none names the computation doc or another factor.
- Computation docs: room_payment_amount §3 ("Every amount a schedule in this rule adds …") and catch_up_discount_amount §3.3 ("Every share of the discount rate this rule sets multiplies the tier's percentage") tell the reader that schedules modify the figure, without naming one. Both sentences are verbatim source rule text, so they are recorded as SRC-1 (placement), not as a rendering addition. In the blind audit they pre-solved nothing: every factor was reached from record words.
- Verdict: KB-EXPLICIT PASS.

## Three part-verdicts
runtime=PASS, bijection=PASS, dependency_form=PASS.


## revision_2

### source_to_kb / kb_to_source
- Charter (96e73223…), task_tools (ab50360b…) and docs/credit (tree 2971b6b5ce969a27; listing e6336789…) are byte-unchanged since revision_1. So every revision_1 entry stands as recorded: the atom-by-atom forward scan, the reverse scan, the retired surface and the prerequisite carriage.
- New scored values (task 0 room payment 2619.61; task 1 granted 149075.00) and the new intermediates (15601.32, 0.077529, 4748.64, 2747.69) appear in no document example and no unlock schema. Grep restricted to docs/ was empty, and the unlock schemas carry no figures.

### Cross-product rows after the rework (producible by the owning product's published rules)
- **Ship-To returns:** RMA-1529966 and RMA-1530418 now exist for both return credit memos. Each has the reason wrong_item_shipped (a Corbett-error return) and route pickup.
  - RMA dated 21 and 6 days after shipping, inside the Route Delivery 60-day window; goods received within the 30-day validity.
  - Route Delivery waives the restocking fee on Corbett-error returns, and route pickup carries no label fee, so the full credits 742.15 / 1860.00 follow (return_fee_credit_schedule; return terms clauses 5, 9 and 10).
  - Credit memos are dated 3 business days after receipt (credit issue 3) and applied to the invoice that billed each item (credit_memo_application clause 1).
  - **SRC-3 CLOSED.**
- **Freight:** Standard Ship-To orders of 93.00–129.50 are below the 150.00 threshold, giving 12.95 per shipment; Route Delivery freight is 0.00; no order is below the minimum order. This matches invoice freight (freight_minimum_order_schedule).
- **StockSmart:** 32 monthly minimum fees of 400.00 since go-live 2024-02-05. Program spend is 0 < 8000.00, and there are no bins, so no bin fees.
- **VendPoint:** vends are now seeded, and each usage bill equals that month's vends, billed per cost center (Coil 40 cost center billing yes). Badges are at most 7 against 100 included.
  - Ramp-up Dec–Feb; every tested month is at or above the 1250.00 minimum, so no shortfall.
  - Cellular data fee 15.00 every month since installation.
  - **SRC-4 CLOSED for task 0.**
- Backorders: open 61+ days fewer than the 90-day auto-cancel; fill ships freight-free; unchanged.
- Residual note (not an item): sales tax is not fixed by any product's published rule, so the reworked tax amounts are free seed inputs. No published catalogue fixes item prices. Program fees are folded into the consolidated invoice's merchandise amount ("all shipments and services of a calendar month are billed on one invoice").

### bijection_verdict
KB-BIJECTION PASS (revision_2); no regression.

### dependency_form
Docs unchanged; KB-EXPLICIT PASS (revision_2).

### Three part-verdicts
runtime=PASS, bijection=PASS, dependency_form=PASS.
