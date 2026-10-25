# d3_ship_to_orders_backorders_and_returns — instantiate plan (round 1, fresh relaunch)

## Draw (draw_counts.py --tasks 2)
- task 0: prerequisite_problems=1, factor_counts=[4, 6]
- task 1: prerequisite_problems=1, factor_counts=[5, 5]
=> 4 extended policies, 2 per task; each tree = 1 root + 1 prerequisite; >= 1 value_input edge per task; >= 1 owner=user tool per task.

## Hard constraints discovered in Step 0 (why the design looks the way it does)
1. Trigger rule (Principle D): order_line_shipped, order_backorder_filled, order_fee_charged (every fee_type: two triggers cover
   standard_freight and not-standard_freight) and order_return_received all trigger credit:* events -> NO task tool may write them.
   order_line_cancelled on a special-order line triggers order_fee_charged (which triggers credit) -> also excluded.
   Writable d3 events left: order_line_booked, order_line_cancelled (stocked), order_backorder_cancelled, order_return_authorized,
   order_return_declined, order_return_closed_no_credit, order_ship_to_reactivated, order_service_level_changed, order_ship_to_closed.
   => every base money formula of d3 (freight, fees, restocking, label, credit, special-order cancellation fee) lands on a forbidden event.
   Route-around: the multi-factor quantities are (a) the service level a ship-to holds (variant_name, string result — check_compute
   `near()` falls back to string equality) and (b) the quantity authorized on a stock-rotation RMA (integer), whose money allowance carries the factors.
2. DSL scope: SUM/COUNT/MAX/LATEST are scoped to the target ship-to (ship_to_id=HID) with eq filters only; no sister ship-to reads;
   XSUM/XCOUNT/... scoped to the customer; eq-filter values may be bindings (used to key on one record).
   within_months = whole months between event date and NOW in [0, N).
3. Line identity for the rotation RMA: the ship-to's (single) customer-reason request declined as outside the return window —
   LATEST over order_return_declined; seed exactly one declined row (XF9 tie rule).
4. Cross-difficulty categories available: credit (d1), pricing (d2), vmi (d4), vending (d5). calibration/safety are not difficulties.

## Scope split (Principle C)
- task 0 (claims review + rotation):
  - prereq P_A `order_ext_anniversary_review` — agent records the overdue anniversary service-level review (state_due), computes the
    level held after review (variant_name), 4 factors. Tool: record_..._review (agent, order_service_level_changed).
  - root  P_B `order_ext_stock_rotation_return` — customer submits a stock-rotation return of slow-moving stock (owner=user),
    computes quantity authorized, 6 factors; its allowance rate reads the held service level -> value_input edge from P_A.
- task 1 (claims reactivation + move-up):
  - prereq P_C `order_ext_reactivation_level` — agent reactivates a suspended ship-to, computes the level on reactivation, 5 factors.
    Tool: reactivate_... (agent, order_ship_to_reactivated).
  - root  P_D `order_ext_requested_move_up` — customer elects a move up one level (owner=user, order_service_level_changed), computes the
    level after the request, 5 factors; "the higher level" is the next level above the level held -> value_input edge from P_C.
  Realism hook for task 1: the warehouse ship-to was suspended for "no booked order" while all its buying ran through a StockSmart
  program and a VendPoint machine; reactivation level rests on non-spend evidence (dormancy, credit standing, route territory),
  the move-up rests on spend (own shipments + program spend at the ship-to) -> the two policies measure different things (coherent).
- Remaining headroom after task 1: none needed (M=2); untouched d3 capabilities (closure, backorder/line cancellation, declines,
  RMA closure) carry no multi-factor quantity on a writable event and are left to base.

## Prerequisite sentences (draft; direction chosen per business wording)
- P_B waits on P_A (state form): "The stock-rotation allowance is fixed only after the ship-to's service level carries the review
  for its most recent opening anniversary." (state: last_review_date on/after the latest anniversary; written only by P_A's tool)
- P_D waits on P_C (state form, negated direction): "A requested move up is not decided until the ship-to's status is active."
  (state: status=active; the only d3 write that sets active from suspended is P_C's tool)

## Probe table (run on scratch copies of the task worlds; probes.py in /tmp scratch) — expected unchanged unless the row says otherwise
| probe (policy) | result |
|---|---|
Traceback (most recent call last):
  File "/tmp/d3_ship_to_orders_backorders_and_returns_0068/probes.py", line 6, in <module>
    s0=json.load(open('t0_state.json')); s1=json.load(open('t1_state.json'))
                 ^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: 't0_state.json'

Notes: decoy declined line (other decline_reason) and decoy price line (other sku), decoy StockSmart program / VendPoint machine at the sister
ship-to leave results unchanged (filters by decline_reason, sku, ship_to_id). Absent-record tiers: no declined line -> 0 (rule: requested quantity 0);
no credit account -> standing 0 percent (rule: 'or the customer has no such account'); no agreement -> all-merchandise scope and default cap;
no last_order_date -> no dormancy drop (rule says so); no program -> no take-back; no streams -> twelve-month total 0.00 -> trailing-year tier
(guard 'above 0.00'); no history in the review -> level kept (shipped-merchandise guard). Zero-division: review pace and move-up growth guarded by
'twelve-month ... above 0.00'; rotation units guarded by unit value > 0. Same-day ties: one declined line; price lines on distinct effective dates;
one shipment on the rotation line. Month-end: windows are 'fewer than N whole months' (MONTHS is day-of-month aware), stated in every rule.

## Revision 2 (policy audit r1) — design deltas and probe table
- Task 0: opened_date 2019-10-14 (the review falls due on the call date, 2026-10-14); review method = review_tenure_basis (MN / MX / C12);
  review spend 50080.00 < 51000.00 -> Priority; rotation 28 (rate 7, standing inside the gross product, scope single shipment, lower contract 61.60).
- Task 1: move-up measure = own merchandise + VendPoint usage only (vmi clause); VendPoint Coil 40 (18000.00 / 10000.00); method site_ordering_basis
  (MX for a ship-to with no shipped line in 12 months) -> 20000.00 vs gate 25000 x .92 x .90 x .95 = 19665.00 -> Priority; reactivation route
  drops read the last active year (4 route runs -> 1 drop) -> Standard.
- Superseded: the 'Design v1' factor names review_pace_window, site_growth_window, replenishment_counted and the r1 world figures above.

| probe (policy) | result |
|---|---|
| B base | 28 |
| B two declined lines on the latest date (scope -> 0) | 0 |
| B older second declined line (decoy, unchanged) | 28 |
| B later declined line other reason (decoy, unchanged) | 28 |
| B no declined line (absent -> 0) | 0 |
| B second shipment same date (scope -> 0) | 0 |
| B backorder fill on the line (scope -> 0) | 0 |
| B hazmat class (scope -> 0) | 0 |
| B special-order item (scope -> 0) | 0 |
| B second price line on the same effective date (tier a off -> invoiced) | 27 |
| B price line of another agreement (decoy, unchanged) | 28 |
| B aged shipment 12 months, no later price (markdown tier) | 29 |
| B closed program at same ship-to (decoy, unchanged) | 28 |
| B program paused (half share) | 23 |
| B no credit account (standing 0) | 0 |
| B no agreement (all scope, default cap, no price line) | 23 |
| A base | Corbett Priority Ship-To |
| A young ship-to opened 2025-03-14 (MX tier) | Corbett Route Delivery Ship-To |
| A no history (level kept by the shipped-merchandise guard) | Corbett Route Delivery Ship-To |
| A route shipment exactly 12 whole months back (outside, unchanged) | Corbett Priority Ship-To |
| C base | Corbett Standard Ship-To |
| C no last_order_date (D=0: no dormancy drop; no route run in the window -> 2 route drops) | Corbett Standard Ship-To |
| C no route run in last active year (2 drops) | Corbett Parcel Ship-To |
| C no program (no take-back) | Corbett Parcel Ship-To |
| C last order 2024-05-31 against 2026-10-15 (day-of-month convention: 28 months) | Corbett Standard Ship-To |
| D base | Corbett Priority Ship-To |
| D machine suspended (half share) | Corbett Standard Ship-To |
| D no machine (0 counted) | Corbett Standard Ship-To |
| D no usage rows (zero measure) | Corbett Standard Ship-To |
| D terms tier Net 10 (terms share 100 -> gate 20700) | Corbett Standard Ship-To |
| D held Priority (out of scope) | Corbett Priority Ship-To |
| D young ship-to opened 2026-10-15 with no shipment (guard MX(1, months)) | Corbett Priority Ship-To |

## Revision 3 (policy audit r2: C10, C11) — probe table (probes2.py on scratch copies; supersedes the r2 table)
| probe (policy) | result |
|---|---|
| B base | 28 |
| B two declined lines on the latest date (scope -> 0) | 0 |
| B older second declined line (decoy, unchanged) | 28 |
| B later declined line other reason (decoy, unchanged) | 28 |
| B no declined line (absent -> 0) | 0 |
| B second shipment same date (scope -> 0) | 0 |
| B backorder fill on the line (scope -> 0) | 0 |
| B hazmat class (scope -> 0) | 0 |
| B special-order item (scope -> 0) | 0 |
| B second price line on the same effective date (tier a off -> invoiced) | 27 |
| B price line of another agreement (decoy, unchanged) | 28 |
| B aged shipment 12 months, no later price (markdown tier) | 29 |
| B closed program at same ship-to (decoy, unchanged) | 28 |
| B program paused (half share) | 23 |
| B no credit account (standing 0) | 0 |
| B no agreement (all scope, default cap, no price line) | 23 |
| A base | Corbett Priority Ship-To |
| A young ship-to opened 2025-03-14 (MX tier) | Corbett Route Delivery Ship-To |
| A no history (level kept by the shipped-merchandise guard) | Corbett Route Delivery Ship-To |
| A route shipment exactly 12 whole months back (outside, unchanged) | Corbett Priority Ship-To |
| C base | Corbett Standard Ship-To |
| C no last_order_date (no dormancy drop, no last active year -> no route drop) | Corbett Route Delivery Ship-To |
| C no opened_date (tenure 0 months -> as added) | Corbett Parcel Ship-To |
| C no route run in last active year (2 drops) | Corbett Parcel Ship-To |
| C no program (no take-back) | Corbett Parcel Ship-To |
| C last order 2024-05-31 against 2026-10-15 (day-of-month convention: 28 months) | Corbett Standard Ship-To |
| D base | Corbett Priority Ship-To |
| D machine suspended (half share) | Corbett Standard Ship-To |
| D no machine (0 counted) | Corbett Standard Ship-To |
| D no usage rows (zero measure) | Corbett Standard Ship-To |
| D terms tier Net 10 (terms share 100 -> gate 20700) | Corbett Standard Ship-To |
| D held Priority (out of scope) | Corbett Priority Ship-To |
| D young ship-to opened 2026-10-15 with no shipment (guard MX(1, months)) | Corbett Priority Ship-To |
| A no opened_date (0 months -> higher-of tier) | Corbett Route Delivery Ship-To |
| B no opened_date (base rate) | 19 |
| D no opened_date with a shipment in 12 months (0 months, divided by at least 1) | Corbett Priority Ship-To |

Method-tier pairwise table (current): review_tenure_basis MN(C12,2C6) / MX(C12,2C6) / C12 — C12=100, C6=30 -> 60/100/100, C6=70 -> 100/140/100; rotation_base_scope category 12m / sku 24m / all 12m — record populations differ (any line outside the category); tenure_adjustment floor(x/2) / max(0,x-1) / x — x=4 -> 2/3/4; site_ordering_basis MX(C12,2C6) / C12x12/max(1,m) / C12 — C12=100, C6=70, m=8 -> 140/150/100. rotation_unit_value is a parameter since r3 (its tiers select the divisor).

## Revision 4 (render_r1 findings) — probe table (probes2.py on scratch copies; supersedes the r3 table)
| probe (policy) | result |
|---|---|
| B base | 28 |
| B two declined lines on the latest date (scope -> 0) | 0 |
| B older second declined line (decoy, unchanged) | 28 |
| B later declined line other reason (decoy, unchanged) | 28 |
| B no declined line (absent -> 0) | 0 |
| B second shipment same date (scope -> 0) | 0 |
| B backorder fill on the line (scope -> 0) | 0 |
| B hazmat class (scope -> 0) | 0 |
| B special-order item (scope -> 0) | 0 |
| B second price line on the same effective date (tier a off -> invoiced) | 27 |
| B price line of another agreement (decoy, unchanged) | 28 |
| B aged shipment 12 months, no later price (markdown tier) | 29 |
| B closed program at same ship-to (decoy, unchanged) | 28 |
| B program paused (half share) | 23 |
| B no credit account (standing 0) | 0 |
| B no agreement (all scope, default cap, no price line) | 23 |
| A base | Corbett Priority Ship-To |
| A young ship-to opened 2025-03-14 (MX tier) | Corbett Route Delivery Ship-To |
| A no history (level kept by the shipped-merchandise guard) | Corbett Route Delivery Ship-To |
| A route shipment exactly 12 whole months back (outside, unchanged) | Corbett Priority Ship-To |
| C base | Corbett Standard Ship-To |
| C no last_order_date (no dormancy drop, no last active year -> no route drop) | Corbett Route Delivery Ship-To |
| C no opened_date (tenure 0 months -> as added) | Corbett Parcel Ship-To |
| C no route run in last active year (2 drops) | Corbett Parcel Ship-To |
| C no program (no take-back) | Corbett Parcel Ship-To |
| C last order 2024-05-31 against 2026-10-15 (day-of-month convention: 28 months) | Corbett Standard Ship-To |
| D base | Corbett Priority Ship-To |
| D machine suspended (half share) | Corbett Standard Ship-To |
| D no machine (0 counted) | Corbett Standard Ship-To |
| D no usage rows (zero measure) | Corbett Standard Ship-To |
| D terms tier Net 10 (terms share 100 -> gate 20700) | Corbett Standard Ship-To |
| D held Priority (out of scope) | Corbett Priority Ship-To |
| D young ship-to opened 2026-10-15 with no shipment (guard MX(1, months)) | Corbett Priority Ship-To |
| A no opened_date (0 months -> higher-of tier) | Corbett Route Delivery Ship-To |
| B no opened_date (base rate) | 19 |
| D no opened_date with a shipment in 12 months (0 months, divided by at least 1) | Corbett Priority Ship-To |
| D decoy: removed machine at the ship-to listed first (never read, unchanged) | Corbett Priority Ship-To |
| D machine removal_pending only (idle share 50 -> 10000 < gate) | Corbett Standard Ship-To |
| C decoy: closed Onsite program listed first plus the active Self-Scan (closed never read, unchanged) | Corbett Standard Ship-To |
| C program paused only (no active program -> no take-back) | Corbett Parcel Ship-To |
| B decoy: closed program listed first plus the active one (unchanged) | 28 |

Method-tier pairwise table unchanged from r3 (review_tenure_basis, rotation_base_scope, tenure_adjustment, site_ordering_basis). tenure_adjustment now acts on the net total (drops less drops taken back, floored at 0).

## Revision 5 (policy audit r4: R4-1) — probe table (probes2.py on scratch copies; supersedes the r4 table)
| probe (policy) | result |
|---|---|
| B base | 28 |
| B two declined lines on the latest date (scope -> 0) | 0 |
| B older second declined line (decoy, unchanged) | 28 |
| B later declined line other reason (decoy, unchanged) | 28 |
| B no declined line (absent -> 0) | 0 |
| B second shipment same date (scope -> 0) | 0 |
| B backorder fill on the line (scope -> 0) | 0 |
| B hazmat class (scope -> 0) | 0 |
| B special-order item (scope -> 0) | 0 |
| B second price line on the same effective date (tier a off -> invoiced) | 27 |
| B price line of another agreement (decoy, unchanged) | 28 |
| B aged shipment 12 months, no later price (markdown tier) | 29 |
| B closed program at same ship-to (decoy, unchanged) | 28 |
| B program paused (half share) | 23 |
| B no credit account (standing 0) | 0 |
| B no agreement (all scope, default cap, no price line) | 23 |
| A base | Corbett Priority Ship-To |
| A young ship-to opened 2025-03-14 (MX tier) | Corbett Route Delivery Ship-To |
| A no history (level kept by the shipped-merchandise guard) | Corbett Route Delivery Ship-To |
| A route shipment exactly 12 whole months back (outside, unchanged) | Corbett Priority Ship-To |
| C base | Corbett Standard Ship-To |
| C no last_order_date (no dormancy drop, no last active year -> no route drop) | Corbett Route Delivery Ship-To |
| C no opened_date (tenure 0 months -> as added) | Corbett Parcel Ship-To |
| C no route run in last active year (2 drops) | Corbett Parcel Ship-To |
| C no program (no take-back) | Corbett Parcel Ship-To |
| C last order 2024-05-31 against 2026-10-15 (day-of-month convention: 28 months) | Corbett Standard Ship-To |
| D base | Corbett Priority Ship-To |
| D machine suspended (half share) | Corbett Standard Ship-To |
| D no machine (0 counted) | Corbett Standard Ship-To |
| D no usage rows (zero measure) | Corbett Standard Ship-To |
| D terms tier Net 10 (terms share 100 -> gate 20700) | Corbett Standard Ship-To |
| D held Priority (out of scope) | Corbett Priority Ship-To |
| D young ship-to opened 2026-10-15 with no shipment (guard MX(1, months)) | Corbett Priority Ship-To |
| A no opened_date (0 months -> higher-of tier) | Corbett Route Delivery Ship-To |
| B no opened_date (base rate) | 19 |
| D no opened_date with a shipment in 12 months (0 months, divided by at least 1) | Corbett Priority Ship-To |
| D decoy: removed machine at the ship-to listed first (never read, unchanged) | Corbett Priority Ship-To |
| D machine removal_pending only (idle share 50 -> 10000 < gate) | Corbett Standard Ship-To |
| C decoy: closed Onsite program listed first plus the active Self-Scan (closed never read, unchanged) | Corbett Standard Ship-To |
| C program paused only (no active program -> no take-back) | Corbett Parcel Ship-To |
| B decoy: closed program listed first plus the active one (unchanged) | 28 |
| D two active machines at the ship-to (count 2 -> base rule: own trailing spend 0.00 < 25000 -> keeps Standard) | Corbett Standard Ship-To |
| D one active plus one suspended machine (count 2 -> base rule -> keeps Standard) | Corbett Standard Ship-To |
| D two active machines of the same model (counted once by the stated status-and-model convention -> inside the rule) | Corbett Priority Ship-To |

Method-tier pairwise table unchanged from r3/r4.

## Revision 6 (policy audit r5: R5-1) — probe table (probes2.py on scratch copies; supersedes the r5 table)
| probe (policy) | result |
|---|---|
| B base | 28 |
| B two declined lines on the latest date (scope -> 0) | 0 |
| B older second declined line (decoy, unchanged) | 28 |
| B later declined line other reason (decoy, unchanged) | 28 |
| B no declined line (absent -> 0) | 0 |
| B second shipment same date (scope -> 0) | 0 |
| B backorder fill on the line (scope -> 0) | 0 |
| B hazmat class (scope -> 0) | 0 |
| B special-order item (scope -> 0) | 0 |
| B second price line on the same effective date (tier a off -> invoiced) | 27 |
| B price line of another agreement (decoy, unchanged) | 28 |
| B aged shipment 12 months, no later price (markdown tier) | 29 |
| B closed program at same ship-to (decoy, unchanged) | 28 |
| B program paused (half share) | 23 |
| B no credit account (standing 0) | 0 |
| B no agreement (all scope, default cap, no price line) | 23 |
| A base | Corbett Priority Ship-To |
| A young ship-to opened 2025-03-14 (MX tier) | Corbett Route Delivery Ship-To |
| A no history (level kept by the shipped-merchandise guard) | Corbett Route Delivery Ship-To |
| A route shipment exactly 12 whole months back (outside, unchanged) | Corbett Priority Ship-To |
| C base | Corbett Standard Ship-To |
| C no last_order_date (no dormancy drop, no last active year -> no route drop) | Corbett Route Delivery Ship-To |
| C no opened_date (tenure 0 months -> as added) | Corbett Parcel Ship-To |
| C no route run in last active year (2 drops) | Corbett Parcel Ship-To |
| C no program (no take-back) | Corbett Parcel Ship-To |
| C last order 2024-05-31 against 2026-10-15 (day-of-month convention: 28 months) | Corbett Standard Ship-To |
| D base | Corbett Priority Ship-To |
| D terms tier Net 10 (terms share 100 -> gate 21208.75) | Corbett Standard Ship-To |
| D held Priority (out of scope) | Corbett Priority Ship-To |
| D young ship-to opened 2026-10-15 with no shipment (guard MX(1, months)) | Corbett Priority Ship-To |
| A no opened_date (0 months -> higher-of tier) | Corbett Route Delivery Ship-To |
| B no opened_date (base rate) | 19 |
| D no opened_date with a shipment in 12 months (0 months, divided by at least 1) | Corbett Standard Ship-To |
| C decoy: closed Onsite program listed first plus the active Self-Scan (closed never read, unchanged) | Corbett Standard Ship-To |
| C program paused only (no active program -> no take-back) | Corbett Parcel Ship-To |
| B decoy: closed program listed first plus the active one (unchanged) | 28 |
| D two active machines of the same model at the ship-to (VendPoint never read -> unchanged) | Corbett Priority Ship-To |
| D removed machine listed first plus an active one (never read -> unchanged) | Corbett Priority Ship-To |
| D no last_order_date (no last active year -> measure 0.00 -> keeps Standard) | Corbett Standard Ship-To |
| D credit account held 57 months (tenure share 100 -> gate 20985.50 > measure -> keeps Standard) | Corbett Standard Ship-To |
| D no credit account (standing, terms, tenure in full -> keeps Standard) | Corbett Standard Ship-To |

Method-tier pairwise tables: review_tenure_basis, rotation_base_scope, tenure_adjustment unchanged; site_ordering_basis now (a) S_last_active_year x 12 / (D + 12) (window anchored on the last order), (b) C12 x 12 / max(1, months open), (c) C12 — S = 120, D = 28, C12 = 100, open 8 -> 36 / 150 / 100.

## Revision 7 (KB audit SRC-1) — probe table (probes2.py on scratch copies; supersedes the r6 table)
| probe (policy) | result |
|---|---|
| B base | 28 |
| B two declined lines on the latest date (scope -> 0) | 0 |
| B older second declined line (decoy, unchanged) | 28 |
| B later declined line other reason (decoy, unchanged) | 28 |
| B no declined line (absent -> 0) | 0 |
| B second shipment same date (scope -> 0) | 0 |
| B backorder fill on the line (scope -> 0) | 0 |
| B hazmat class (scope -> 0) | 0 |
| B special-order item (scope -> 0) | 0 |
| B second price line on the same effective date (tier a off -> invoiced) | 27 |
| B price line of another agreement (decoy, unchanged) | 28 |
| B aged shipment 12 months, no later price (markdown tier) | 29 |
| B closed program at same ship-to (decoy, unchanged) | 28 |
| B program paused (half share) | 23 |
| B no credit account (standing 0) | 0 |
| B no agreement (all scope, default cap, no price line) | 23 |
| A base | Corbett Priority Ship-To |
| A young ship-to opened 2025-03-14 (MX tier) | Corbett Route Delivery Ship-To |
| A no history (level kept by the shipped-merchandise guard) | Corbett Route Delivery Ship-To |
| A route shipment exactly 12 whole months back (outside, unchanged) | Corbett Priority Ship-To |
| C base | Corbett Standard Ship-To |
| C no last_order_date (no dormancy drop, no last active year -> no route drop) | Corbett Route Delivery Ship-To |
| C no opened_date (tenure 0 months -> as added) | Corbett Parcel Ship-To |
| C no route run in last active year (2 drops) | Corbett Parcel Ship-To |
| C no program (no take-back) | Corbett Parcel Ship-To |
| C last order 2024-05-31 against 2026-10-15 (day-of-month convention: 28 months) | Corbett Standard Ship-To |
| D base | Corbett Priority Ship-To |
| D terms tier Net 10 (terms share 100 -> gate 21208.75) | Corbett Standard Ship-To |
| D held Priority (out of scope) | Corbett Priority Ship-To |
| D young ship-to opened 2026-10-15 with no shipment (guard MX(1, months)) | Corbett Priority Ship-To |
| A no opened_date (0 months -> higher-of tier) | Corbett Route Delivery Ship-To |
| B no opened_date (base rate) | 19 |
| D no opened_date with a shipment in 12 months (0 months, divided by at least 1) | Corbett Standard Ship-To |
| C decoy: closed Onsite program listed first plus the active Self-Scan (closed never read, unchanged) | Corbett Standard Ship-To |
| C program paused only (no active program -> no take-back) | Corbett Parcel Ship-To |
| B decoy: closed program listed first plus the active one (unchanged) | 28 |
| D two active machines of the same model at the ship-to (VendPoint never read -> unchanged) | Corbett Priority Ship-To |
| D removed machine listed first plus an active one (never read -> unchanged) | Corbett Priority Ship-To |
| D no last_order_date (no last active year -> measure 0.00 -> keeps Standard) | Corbett Standard Ship-To |
| D credit account held 57 months (tenure share 100 -> gate 20985.50 > measure -> keeps Standard) | Corbett Standard Ship-To |
| D no credit account (standing, terms, tenure in full -> keeps Standard) | Corbett Standard Ship-To |
| B stated order: narrowing first, StockSmart addition on the narrowed figure (36268.75 + 20000.00 = 56268.75) | 28 |
| B reverse reading (addition first, then narrowing to the category, which drops the uncategorized StockSmart bills) = base 36268.75 | 17 |

Method-tier pairwise tables unchanged from r6.

## Revision 8 (KB re-judge revision_3, seed-only) — probe table (probes2.py on scratch copies; supersedes the r7 table; every result identical to r7)
| probe (policy) | result |
|---|---|
| B base | 28 |
| B two declined lines on the latest date (scope -> 0) | 0 |
| B older second declined line (decoy, unchanged) | 28 |
| B later declined line other reason (decoy, unchanged) | 28 |
| B no declined line (absent -> 0) | 0 |
| B second shipment same date (scope -> 0) | 0 |
| B backorder fill on the line (scope -> 0) | 0 |
| B hazmat class (scope -> 0) | 0 |
| B special-order item (scope -> 0) | 0 |
| B second price line on the same effective date (tier a off -> invoiced) | 27 |
| B price line of another agreement (decoy, unchanged) | 28 |
| B aged shipment 12 months, no later price (markdown tier) | 29 |
| B closed program at same ship-to (decoy, unchanged) | 28 |
| B program paused (half share) | 23 |
| B no credit account (standing 0) | 0 |
| B no agreement (all scope, default cap, no price line) | 23 |
| A base | Corbett Priority Ship-To |
| A young ship-to opened 2025-03-14 (MX tier) | Corbett Route Delivery Ship-To |
| A no history (level kept by the shipped-merchandise guard) | Corbett Route Delivery Ship-To |
| A route shipment exactly 12 whole months back (outside, unchanged) | Corbett Priority Ship-To |
| C base | Corbett Standard Ship-To |
| C no last_order_date (no dormancy drop, no last active year -> no route drop) | Corbett Route Delivery Ship-To |
| C no opened_date (tenure 0 months -> as added) | Corbett Parcel Ship-To |
| C no route run in last active year (2 drops) | Corbett Parcel Ship-To |
| C no program (no take-back) | Corbett Parcel Ship-To |
| C last order 2024-05-31 against 2026-10-15 (day-of-month convention: 28 months) | Corbett Standard Ship-To |
| D base | Corbett Priority Ship-To |
| D terms tier Net 10 (terms share 100 -> gate 21208.75) | Corbett Standard Ship-To |
| D held Priority (out of scope) | Corbett Priority Ship-To |
| D young ship-to opened 2026-10-15 with no shipment (guard MX(1, months)) | Corbett Priority Ship-To |
| A no opened_date (0 months -> higher-of tier) | Corbett Route Delivery Ship-To |
| B no opened_date (base rate) | 19 |
| D no opened_date with a shipment in 12 months (0 months, divided by at least 1) | Corbett Standard Ship-To |
| C decoy: closed Onsite program listed first plus the active Self-Scan (closed never read, unchanged) | Corbett Standard Ship-To |
| C program paused only (no active program -> no take-back) | Corbett Parcel Ship-To |
| B decoy: closed program listed first plus the active one (unchanged) | 28 |
| D two active machines of the same model at the ship-to (VendPoint never read -> unchanged) | Corbett Priority Ship-To |
| D removed machine listed first plus an active one (never read -> unchanged) | Corbett Priority Ship-To |
| D no last_order_date (no last active year -> measure 0.00 -> keeps Standard) | Corbett Standard Ship-To |
| D credit account held 57 months (tenure share 100 -> gate 20985.50 > measure -> keeps Standard) | Corbett Standard Ship-To |
| D no credit account (standing, terms, tenure in full -> keeps Standard) | Corbett Standard Ship-To |
| B stated order: narrowing first, StockSmart addition on the narrowed figure (36268.75 + 20000.00 = 56268.75) | 28 |
| B reverse reading (addition first, then narrowing to the category, which drops the uncategorized StockSmart bills) = base 36268.75 | 17 |

Method-tier pairwise tables unchanged; rotation_base_scope on task 0 now 36268.75 / 6966.00 / 62804.25 (pre-agreement BR-31406 line at 76.95).

## Revision 9 (policy audit R8-1, seed-only) — probe table (probes2.py on scratch copies; identical to r8)
| probe (policy) | result |
|---|---|
| B base | 28 |
| B two declined lines on the latest date (scope -> 0) | 0 |
| B older second declined line (decoy, unchanged) | 28 |
| B later declined line other reason (decoy, unchanged) | 28 |
| B no declined line (absent -> 0) | 0 |
| B second shipment same date (scope -> 0) | 0 |
| B backorder fill on the line (scope -> 0) | 0 |
| B hazmat class (scope -> 0) | 0 |
| B special-order item (scope -> 0) | 0 |
| B second price line on the same effective date (tier a off -> invoiced) | 27 |
| B price line of another agreement (decoy, unchanged) | 28 |
| B aged shipment 12 months, no later price (markdown tier) | 29 |
| B closed program at same ship-to (decoy, unchanged) | 28 |
| B program paused (half share) | 23 |
| B no credit account (standing 0) | 0 |
| B no agreement (all scope, default cap, no price line) | 23 |
| A base | Corbett Priority Ship-To |
| A young ship-to opened 2025-03-14 (MX tier) | Corbett Route Delivery Ship-To |
| A no history (level kept by the shipped-merchandise guard) | Corbett Route Delivery Ship-To |
| A route shipment exactly 12 whole months back (outside, unchanged) | Corbett Priority Ship-To |
| C base | Corbett Standard Ship-To |
| C no last_order_date (no dormancy drop, no last active year -> no route drop) | Corbett Route Delivery Ship-To |
| C no opened_date (tenure 0 months -> as added) | Corbett Parcel Ship-To |
| C no route run in last active year (2 drops) | Corbett Parcel Ship-To |
| C no program (no take-back) | Corbett Parcel Ship-To |
| C last order 2024-05-31 against 2026-10-15 (day-of-month convention: 28 months) | Corbett Standard Ship-To |
| D base | Corbett Priority Ship-To |
| D terms tier Net 10 (terms share 100 -> gate 21208.75) | Corbett Standard Ship-To |
| D held Priority (out of scope) | Corbett Priority Ship-To |
| D young ship-to opened 2026-10-15 with no shipment (guard MX(1, months)) | Corbett Priority Ship-To |
| A no opened_date (0 months -> higher-of tier) | Corbett Route Delivery Ship-To |
| B no opened_date (base rate) | 19 |
| D no opened_date with a shipment in 12 months (0 months, divided by at least 1) | Corbett Standard Ship-To |
| C decoy: closed Onsite program listed first plus the active Self-Scan (closed never read, unchanged) | Corbett Standard Ship-To |
| C program paused only (no active program -> no take-back) | Corbett Parcel Ship-To |
| B decoy: closed program listed first plus the active one (unchanged) | 28 |
| D two active machines of the same model at the ship-to (VendPoint never read -> unchanged) | Corbett Priority Ship-To |
| D removed machine listed first plus an active one (never read -> unchanged) | Corbett Priority Ship-To |
| D no last_order_date (no last active year -> measure 0.00 -> keeps Standard) | Corbett Standard Ship-To |
| D credit account held 57 months (tenure share 100 -> gate 20985.50 > measure -> keeps Standard) | Corbett Standard Ship-To |
| D no credit account (standing, terms, tenure in full -> keeps Standard) | Corbett Standard Ship-To |
| B stated order: narrowing first, StockSmart addition on the narrowed figure (36268.75 + 20000.00 = 56268.75) | 28 |
| B reverse reading (addition first, then narrowing to the category, which drops the uncategorized StockSmart bills) = base 36268.75 | 17 |

## Revision 10 (policy audit R9-1, seed-only, task 0) — probe table (probes2.py on scratch copies; identical to r9)
| probe (policy) | result |
|---|---|
| B base | 28 |
| B two declined lines on the latest date (scope -> 0) | 0 |
| B older second declined line (decoy, unchanged) | 28 |
| B later declined line other reason (decoy, unchanged) | 28 |
| B no declined line (absent -> 0) | 0 |
| B second shipment same date (scope -> 0) | 0 |
| B backorder fill on the line (scope -> 0) | 0 |
| B hazmat class (scope -> 0) | 0 |
| B special-order item (scope -> 0) | 0 |
| B second price line on the same effective date (tier a off -> invoiced) | 27 |
| B price line of another agreement (decoy, unchanged) | 28 |
| B aged shipment 12 months, no later price (markdown tier) | 29 |
| B closed program at same ship-to (decoy, unchanged) | 28 |
| B program paused (half share) | 23 |
| B no credit account (standing 0) | 0 |
| B no agreement (all scope, default cap, no price line) | 23 |
| A base | Corbett Priority Ship-To |
| A young ship-to opened 2025-03-14 (MX tier) | Corbett Route Delivery Ship-To |
| A no history (level kept by the shipped-merchandise guard) | Corbett Route Delivery Ship-To |
| A route shipment exactly 12 whole months back (outside, unchanged) | Corbett Priority Ship-To |
| C base | Corbett Standard Ship-To |
| C no last_order_date (no dormancy drop, no last active year -> no route drop) | Corbett Route Delivery Ship-To |
| C no opened_date (tenure 0 months -> as added) | Corbett Parcel Ship-To |
| C no route run in last active year (2 drops) | Corbett Parcel Ship-To |
| C no program (no take-back) | Corbett Parcel Ship-To |
| C last order 2024-05-31 against 2026-10-15 (day-of-month convention: 28 months) | Corbett Standard Ship-To |
| D base | Corbett Priority Ship-To |
| D terms tier Net 10 (terms share 100 -> gate 21208.75) | Corbett Standard Ship-To |
| D held Priority (out of scope) | Corbett Priority Ship-To |
| D young ship-to opened 2026-10-15 with no shipment (guard MX(1, months)) | Corbett Priority Ship-To |
| A no opened_date (0 months -> higher-of tier) | Corbett Route Delivery Ship-To |
| B no opened_date (base rate) | 19 |
| D no opened_date with a shipment in 12 months (0 months, divided by at least 1) | Corbett Standard Ship-To |
| C decoy: closed Onsite program listed first plus the active Self-Scan (closed never read, unchanged) | Corbett Standard Ship-To |
| C program paused only (no active program -> no take-back) | Corbett Parcel Ship-To |
| B decoy: closed program listed first plus the active one (unchanged) | 28 |
| D two active machines of the same model at the ship-to (VendPoint never read -> unchanged) | Corbett Priority Ship-To |
| D removed machine listed first plus an active one (never read -> unchanged) | Corbett Priority Ship-To |
| D no last_order_date (no last active year -> measure 0.00 -> keeps Standard) | Corbett Standard Ship-To |
| D credit account held 57 months (tenure share 100 -> gate 20985.50 > measure -> keeps Standard) | Corbett Standard Ship-To |
| D no credit account (standing, terms, tenure in full -> keeps Standard) | Corbett Standard Ship-To |
| B stated order: narrowing first, StockSmart addition on the narrowed figure (36268.75 + 20000.00 = 56268.75) | 28 |
| B reverse reading (addition first, then narrowing to the category, which drops the uncategorized StockSmart bills) = base 36268.75 | 17 |

## Revision 11 (KB re-judge revision_4 SRC-R4-1..4 + O-R10-1, seed-only final sweep) — probe table (identical to r10)
| probe (policy) | result |
|---|---|
| B base | 28 |
| B two declined lines on the latest date (scope -> 0) | 0 |
| B older second declined line (decoy, unchanged) | 28 |
| B later declined line other reason (decoy, unchanged) | 28 |
| B no declined line (absent -> 0) | 0 |
| B second shipment same date (scope -> 0) | 0 |
| B backorder fill on the line (scope -> 0) | 0 |
| B hazmat class (scope -> 0) | 0 |
| B special-order item (scope -> 0) | 0 |
| B second price line on the same effective date (tier a off -> invoiced) | 27 |
| B price line of another agreement (decoy, unchanged) | 28 |
| B aged shipment 12 months, no later price (markdown tier) | 29 |
| B closed program at same ship-to (decoy, unchanged) | 28 |
| B program paused (half share) | 23 |
| B no credit account (standing 0) | 0 |
| B no agreement (all scope, default cap, no price line) | 23 |
| A base | Corbett Priority Ship-To |
| A young ship-to opened 2025-03-14 (MX tier) | Corbett Route Delivery Ship-To |
| A no history (level kept by the shipped-merchandise guard) | Corbett Route Delivery Ship-To |
| A route shipment exactly 12 whole months back (outside, unchanged) | Corbett Priority Ship-To |
| C base | Corbett Standard Ship-To |
| C no last_order_date (no dormancy drop, no last active year -> no route drop) | Corbett Route Delivery Ship-To |
| C no opened_date (tenure 0 months -> as added) | Corbett Parcel Ship-To |
| C no route run in last active year (2 drops) | Corbett Parcel Ship-To |
| C no program (no take-back) | Corbett Parcel Ship-To |
| C last order 2024-05-31 against 2026-10-15 (day-of-month convention: 28 months) | Corbett Standard Ship-To |
| D base | Corbett Priority Ship-To |
| D terms tier Net 10 (terms share 100 -> gate 21208.75) | Corbett Standard Ship-To |
| D held Priority (out of scope) | Corbett Priority Ship-To |
| D young ship-to opened 2026-10-15 with no shipment (guard MX(1, months)) | Corbett Priority Ship-To |
| A no opened_date (0 months -> higher-of tier) | Corbett Route Delivery Ship-To |
| B no opened_date (base rate) | 19 |
| D no opened_date with a shipment in 12 months (0 months, divided by at least 1) | Corbett Standard Ship-To |
| C decoy: closed Onsite program listed first plus the active Self-Scan (closed never read, unchanged) | Corbett Standard Ship-To |
| C program paused only (no active program -> no take-back) | Corbett Parcel Ship-To |
| B decoy: closed program listed first plus the active one (unchanged) | 28 |
| D two active machines of the same model at the ship-to (VendPoint never read -> unchanged) | Corbett Priority Ship-To |
| D removed machine listed first plus an active one (never read -> unchanged) | Corbett Priority Ship-To |
| D no last_order_date (no last active year -> measure 0.00 -> keeps Standard) | Corbett Standard Ship-To |
| D credit account held 57 months (tenure share 100 -> gate 20985.50 > measure -> keeps Standard) | Corbett Standard Ship-To |
| D no credit account (standing, terms, tenure in full -> keeps Standard) | Corbett Standard Ship-To |
| B stated order: narrowing first, StockSmart addition on the narrowed figure (36268.75 + 20000.00 = 56268.75) | 28 |
| B reverse reading (addition first, then narrowing to the category, which drops the uncategorized StockSmart bills) = base 36268.75 | 17 |

## Revision 13 (KB-VERDICT revision_5 SRC-R5-1..4, seed-only) — probe table (probes2.py on scratch copies; identical to r11/r12)
| probe (policy) | result |
|---|---|
| B base | 28 |
| B two declined lines on the latest date (scope -> 0) | 0 |
| B older second declined line (decoy, unchanged) | 28 |
| B later declined line other reason (decoy, unchanged) | 28 |
| B no declined line (absent -> 0) | 0 |
| B second shipment same date (scope -> 0) | 0 |
| B backorder fill on the line (scope -> 0) | 0 |
| B hazmat class (scope -> 0) | 0 |
| B special-order item (scope -> 0) | 0 |
| B second price line on the same effective date (tier a off -> invoiced) | 27 |
| B price line of another agreement (decoy, unchanged) | 28 |
| B aged shipment 12 months, no later price (markdown tier) | 29 |
| B closed program at same ship-to (decoy, unchanged) | 28 |
| B program paused (half share) | 23 |
| B no credit account (standing 0) | 0 |
| B no agreement (all scope, default cap, no price line) | 23 |
| A base | Corbett Priority Ship-To |
| A young ship-to opened 2025-03-14 (MX tier) | Corbett Route Delivery Ship-To |
| A no history (level kept by the shipped-merchandise guard) | Corbett Route Delivery Ship-To |
| A route shipment exactly 12 whole months back (outside, unchanged) | Corbett Priority Ship-To |
| C base | Corbett Standard Ship-To |
| C no last_order_date (no dormancy drop, no last active year -> no route drop) | Corbett Route Delivery Ship-To |
| C no opened_date (tenure 0 months -> as added) | Corbett Parcel Ship-To |
| C no route run in last active year (2 drops) | Corbett Parcel Ship-To |
| C no program (no take-back) | Corbett Parcel Ship-To |
| C last order 2024-05-31 against 2026-10-15 (day-of-month convention: 28 months) | Corbett Standard Ship-To |
| D base | Corbett Priority Ship-To |
| D terms tier Net 10 (terms share 100 -> gate 21208.75) | Corbett Standard Ship-To |
| D held Priority (out of scope) | Corbett Priority Ship-To |
| D young ship-to opened 2026-10-15 with no shipment (guard MX(1, months)) | Corbett Priority Ship-To |
| A no opened_date (0 months -> higher-of tier) | Corbett Route Delivery Ship-To |
| B no opened_date (base rate) | 19 |
| D no opened_date with a shipment in 12 months (0 months, divided by at least 1) | Corbett Standard Ship-To |
| C decoy: closed Onsite program listed first plus the active Self-Scan (closed never read, unchanged) | Corbett Standard Ship-To |
| C program paused only (no active program -> no take-back) | Corbett Parcel Ship-To |
| B decoy: closed program listed first plus the active one (unchanged) | 28 |
| D two active machines of the same model at the ship-to (VendPoint never read -> unchanged) | Corbett Priority Ship-To |
| D removed machine listed first plus an active one (never read -> unchanged) | Corbett Priority Ship-To |
| D no last_order_date (no last active year -> measure 0.00 -> keeps Standard) | Corbett Standard Ship-To |
| D credit account held 57 months (tenure share 100 -> gate 20985.50 > measure -> keeps Standard) | Corbett Standard Ship-To |
| D no credit account (standing, terms, tenure in full -> keeps Standard) | Corbett Standard Ship-To |
| B stated order: narrowing first, StockSmart addition on the narrowed figure (36268.75 + 20000.00 = 56268.75) | 28 |
| B reverse reading (addition first, then narrowing to the category, which drops the uncategorized StockSmart bills) = base 36268.75 | 17 |
