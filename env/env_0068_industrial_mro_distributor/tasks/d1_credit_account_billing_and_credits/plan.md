# d1_credit_account_billing_and_credits — instantiate plan (M=2)

Draw (scripts/draw_counts.py --tasks 2):
- task 0: prerequisite_problems=1, factor_counts=[5, 4]
- task 1: prerequisite_problems=1, factor_counts=[6, 4]

Identifier band k=1: C-1xxxxx, ein 1xxx, phone digits 4-6 in 210-299, zip 43000-43299, surnames/companies A-D,
all minted references start with digit 1, SKUs 1xxxx.

## Why this shape (design notes)
The compute DSL only reads the target credit account, its own ledgers and other categories' holdings / ledgers,
so every computation is account-level or bound to one record selected by a stated rule (latest statement,
latest payment, the pending request). User-owned writes in this charter that carry a computed figure: a customer
payment, a customer limit request. One task each.

## Task 0 — room on the line for shutdown backorders (frozen 2026-10-14)
- Q0 prereq (agent, 4 factors) `credit_ext_window_discount_catchup` -> `book_cash_discount_2280b564`
  the discount line owed for the account's most recent payment received inside its statement's window with no
  discount line booked (state_due).
- R0 root (user, 5 factors) `credit_ext_backorder_room_payment` -> `pay_by_bank_debit_4d9f44ce`
  the payment that keeps receivable + open backorders + month-end program billing within the over-limit point.
- edge R0 <- Q0, value_input on R0's receivable binding, state form.

## Task 1 — permanent limit increase (frozen 2026-10-15)
- Q1 prereq (user, 6 factors) `credit_ext_permanent_request_figure` -> `submit_limit_request_dcbbb504`
  the limit a permanent request names: the limit the account's net purchases support.
- R1 root (agent, 4 factors) `credit_ext_permanent_increase_grant` -> `decide_limit_request_85fdd39c`
  the approved limit: requested limit capped at the step room (step % + tenure points, contract uplift,
  StockSmart allowance) and the tier ceiling.
- edge R1 <- Q1, value_input on R1's requested binding, state form.

## Probe table (filled as worlds land) — see bottom

## Probe table (rework round 2; scratch copies, /tmp/d1_credit_account_billing_and_credits_0068/r2/probe_out.txt)
Every LATEST / first-match / CFIELD read site, with a decoy, the absent record and None / zero-division / date edges.
| policy | read site | probe | result | rule tier |
|---|---|---|---|---|
| P1 | LATEST payment (pay_date/pay_ref/inv) | second payment entry on the latest date | 0 | tie: no catch-up |
| P1 | LATEST payment | no payment entry | 0 | nothing to book |
| P1 | CFIELD pricing (live, status-filtered; round 7) | agreement renewal_pending, invoice in term | 128.08 | recorded tier: three quarters |
| P1 | scope (round 7) | ended Net-Price row listed first + live Category / no agreement / active + renewal_pending rows / invoice before the live term | 128.08 / 371.07 / 371.07 / 371.07 | live read in scope / base figure (612.50 x 40,000 / 66,024.54) / base figure / base figure |
| P1 | base figure (round 8) | renewed live Net-Price, prior-term invoice / same agreement renewal_pending / only an expired Net-Price covering the invoice / two expired Net-Price rows + live Category / no agreement, non-partial short payment | 0 / 371.07 / 371.07 / 128.08 / 0.00 | base reads live recorded tier + status active: nothing / not active: base figure / ended rows not read / in scope / base short payment |
| P2 | aggregates (round 8) | two machines of one model (second bills 1,320.00 + 15.00) / two machines of different models / two programs of one tier (second fee 400.00) | 3,005.42 / 3,005.42 / 2,950.42 | every machine and program summed, each figure on its own records |
| P4 | aggregates (round 8; re-run round 9) | two machines of one model (750 + 900) / two programs of one tier (second fee 400.00) / fees only in the last whole month | 149,537.00 / 149,487.00 / 148,275.00 | half of 1,650 / summed / fee history 400.00 (round 9: fees billed in the three months take the history tier) |
| P2/P4 | absent lines (round 8; P4 fee row superseded by round 9 below) | no StockSmart fee lines / no VendPoint usage or fee lines (P2); no fee lines / no usage lines (P4); usage of 3,500.00 billed last month (P4) | 2,150.42 / 1,124.80; 147,875.00 / 148,712.00; 0 (whole usage added, increase 52,212.00 above the desk authority: referred) | nothing / nothing; none / none; full-usage tier then desk referral |
| P2 | VendPoint method tiers (round 9) | gold (Jul 1,412.60, Aug 1,288.35, Sep 1,530.90: not rising) / Aug raised to 1,450.00 (rising) / usage only Aug + Sep / usage only Aug / no usage in three months, cellular fees still charged | 2,550.42 / 2,751.60 / 2,670.70 / 2,428.15 / 1,124.80 | average 1,410.62 + 15 / projection 1,611.80 + 15 / latest 1,530.90 + 15 / latest carrying usage 1,288.35 + 15 / nothing |
| P2 | StockSmart share ladder (round 9) | gold (minimum fees Jul, Aug, Sep) / Jul fee removed / onsite fee 250.00 added on 2026-09-30 / no recurring fee last month (Jul, Aug only) / recurring fee only last month / decoy emergency visit fee 180.00 on 2026-09-30 | 2,550.42 / 2,350.42 / 2,800.42 / 2,150.42 / 2,250.42 / 2,550.42 | whole 400 (three months) / half 200 (two months) / whole 650 / half of nothing / quarter 100 (one month) / not a recurring fee |
| P4 | StockSmart method tiers (round 9; paused row superseded by round 10: one month's minimum 148,275.00) | gold (fees Jul-Sep 1,212.00) / no fee in three months, active Weekly Service / same, program paused / no program at all / program closed, fees in three months / fees only last month | 149,087.00 / 149,075.00 / 147,875.00 / 147,875.00 / 149,087.00 / 148,275.00 | fee history / minimum commitment 3 x 400 / no active program: none / none / fee history / fee history 400 |
| P4 | StockSmart minimum commitment, several active programs (round 9) | no fee in three months, active Weekly (400) + Monthly (150) / Weekly + Twice-Weekly (750) | 149,075.00 / 0 | 3 x largest 400 / 3 x 750 = 2,250, increase 50,125.00 above desk authority: referred |
| P4 | VendPoint share ladder (round 9) | gold (750.00 last month) / 3,200.00 last month / 400.00 last month / no usage last month | 149,087.00 / 0 / 148,812.00 / 148,712.00 | half 375 / whole, increase 51,912.00 above desk authority: referred / quarter 100 / quarter of nothing |
| P1 | CFIELD pricing (live) | Cost-Plus (excluded tier) in term | 0.00 | net-priced: nothing |
| P2 | prerequisite with nothing owed (round 4) | two finance charges: catch-up nothing, room payment on the receivable as it stands | P1 0.00, P2 2,678.50 | waits on no line |
| P1 | disputes on invoice | open freight dispute / open quantity-shortage dispute / goods dispute already resolved | 128.08 / 131.41 / 128.08 | freight not a goods dispute / deduct dispute / closed |
| P1 | tier partial flag | Net 30 Preferred short payment | 0.00 | nothing paid for |
| P1 | returned payment on invoice | reversal 1,000.00 adds to left open | 128.08 (still partial) | allocation tier 1 |
| P1 | zero division | invoice merchandise 0 | 0 | no merchandise earns nothing |
| P2 | LATEST invoice date ratio | second invoice on the latest date | 2,550.94 (ratio over both) | all invoices of that date |
| P2 | tax history | no tax billed | 1,497.09 | ratio zero |
| P2 | all cross holdings | absent | 0.00 | floor at zero |
| P2 | tolerance cap | full share 10% + 5 points | capped at 10% -> 0.00 | never exceeds tier tolerance |
| P3 | latest statement | second invoice on the latest date | 198,674.22 (summed) | statement = invoices of that date |
| P3 | purchase base | latest 1.27 x average | 139,178.00 | blend |
| P3 | paper lag (F-C5) | per-shipment email with paper fees / per-shipment paper with fees | 88,702.02 / 100,528.95 | 30 / 40 days |
| P3 | invoices | none | 2,324.22 (contract support only) | base nothing |
| P3 | CFIELD pricing active | agreement expired | 188,912.50 | nothing added |
| P4 | LATEST request | no new request (latest decided) / second permanent request same date | 0 / 0 | nothing decided |
| P4 | tier ladder (F-C12) | Net 30 Standard, step 25: one mark 18.75 | 49,999.00 (ceiling) | monotone |
| P4 | month count | last review 2026-03-31, today 2026-10-15 | 139,087.00 (6 whole months, no points) | stated convention |

## Method tiers — pairwise table (XF 11, round 2)
| policy / factor | tier A | tier B | tier C | distinguishing input (task world unless noted) |
|---|---|---|---|---|
| P1 payment_allocation_to_merchandise | payment less freight and tax (allocation, MX floor) | nothing | whole merchandise | 40,000 payment on 61,250 merch, 4,774.54 freight+tax: 35,225.46 / 0 / 61,250 |
| P3 purchase_base_measure | latest statement alone | (latest + average) / 2 | average | 63,500 vs 40,960.88: 63,500 / 52,230.44 / 40,960.88; B and C meet only at latest = average, outside B's domain (B needs latest >= 1.2 x average) |
| P4 stocksmart_program_allowance (round 11) | billed-fee sum (established billing) | billed-to-date plus forward commitment (new billing) | commitment projection (no fee in three months) | see the round-11 structural table below |
Former method labels on swapped multipliers / subtrahends / windows (P1 earning share, P1 discountable merchandise, P2 gross-up) are now parameter factors deciding a value (merchandise deduction, sales-tax ratio).

### Round 9 (trend tier superseded by round 12 below): VendPoint estimate tiers, pairwise (P2 vendpoint_month_end_billing; u0/u1/u2 = usage billed less than one / one / two whole months back across machines, c = last month's cellular fees)
| pair | tier formulas | distinguishing input (probe9) | values |
|---|---|---|---|
| projection vs average | u0 + (u0 - u1) + c vs (u0 + u1 + u2) / 3 + c | rising 1,412.60 < 1,450.00 < 1,530.90 | 1,626.80 vs 1,479.50 |
| projection vs latest | u0 + (u0 - u1) + c vs u0 + c | usage only Aug 1,288.35 + Sep 1,530.90 (latest tier) | 1,788.45 vs 1,545.90 |
| projection vs nothing | u0 + (u0 - u1) + c vs 0 | no usage, cellular 15.00 | 15.00 vs 0 |
| average vs latest | (u0 + u1 + u2) / 3 + c vs u0 + c | gold (average tier) / usage only Aug + Sep | 1,425.62 vs 1,545.90; 954.75 vs 1,545.90 |
| average vs nothing | (u0 + u1 + u2) / 3 + c vs 0 | no usage, cellular 15.00 | 15.00 vs 0 |
| latest vs nothing | u0-or-u1 + c vs 0 | usage only Aug | 1,303.35 vs 0 |
Cellular fees are inside the three usage tiers, so the nothing tier (machines with no usage billed for three whole months are dormant and nothing is expected to post) differs from every other tier wherever cellular fees are charged on a dormant machine.
StockSmart month-end billing (P2: whole / one half / one quarter by the number of the three months carrying recurring fees) and the VendPoint allowance (P4: whole at 3,000 or more / one half at 500 to under 3,000 / one quarter under 500) are real three-rung share ladders over one figure; the former "nothing" rungs, which equalled one half of zero, are gone. Drawn counts unchanged (P2 5 factors, P4 6 factors); scored values unchanged (2,550.42; 149,087.00).

### Round 10 (superseded by round 11 below): P4 stocksmart_program_allowance, every tier's formula on every other tier's domain
A = fee history (fees billed across programs in the last three whole months); B = 3 x largest monthly minimum fee among active programs; C = largest monthly minimum fee among enrolled, paused or terminating programs. Domains: A = a fee billed in three months; B = no fee, an active program; C = no fee, no active program. Probes: /tmp/d1_credit_account_billing_and_credits_0068/r2/probe10_out.txt.
| pair | input from the first tier's domain: first vs second formula | input from the second tier's domain: first vs second formula |
|---|---|---|
| A vs B | task 1 (fees Jul-Sep, active Weekly): 1,212.00 vs 1,200.00 | no fee, active Weekly: 0 vs 1,200.00 |
| A vs C | task 1 with the program paused: 1,212.00 vs 400.00 | no fee, Weekly paused: 0 vs 400.00 |
| B vs C | no fee, active Weekly + paused Monthly: 1,200.00 vs 150.00 | no fee, Weekly paused: 0 vs 400.00 |

| policy | read site | probe | result | rule tier |
|---|---|---|---|---|
| P4 | StockSmart tiers (round 10) | gold / program paused, fees in three months / no fee + active Weekly / + paused Monthly / no fee, Weekly paused / enrolled / terminating / paused Weekly + enrolled Twice-Weekly / only a closed program / no program | 149,087.00 / 149,087.00 / 149,075.00 / 149,075.00 / 148,275.00 x3 / 148,625.00 / 147,875.00 / 147,875.00 | A / A / B 1,200 / B / C 400 / C 750 / C has no input: nothing |
C is non-zero wherever an enrolled, paused or terminating program exists, which A and B (both 0 there) never are; the only zero sub-case of C (no program on record but a closed one, or none at all) is the formula's empty input, stated in the rule.

### Round 11 (F-C23): P4 stocksmart_program_allowance, operation structure of each tier and all three pairs
Notation: S3 = sum of the program fees billed across the customer's programs in the last three whole months (event rows); S2 = the same sum over the last two whole months; m = the largest monthly_minimum_fee_usd among the customer's ACTIVE programs (tier parameter, 0 with no active program; paused programs excluded because the vmi charter prorates the minimum away for paused days).
| tier | domain | operation structure |
|---|---|---|
| A billed-fee sum | a program fee dated two whole months before today | S3: an aggregation of billed amounts only; no tariff term |
| B billed-to-date plus forward commitment | none dated that far back, fees billed less than two whole months before today | S2 + m: an aggregation of billed amounts PLUS one tariff term (two different sources combined by addition) |
| C commitment projection | no program fee billed in the last three whole months | 3 x m: a tariff term scaled by the window; no billed-amount aggregation at all |

| pair | structural difference | input from the first tier's domain (first vs second) | input from the second tier's domain (first vs second) |
|---|---|---|---|
| A vs B | A reads billed fees only; B adds a forward tariff term to billed fees (a different source enters the formula) | Jul fee 250.00 (A domain): 1,062.00 vs 1,212.00 | fee only Sep 400.00 (B domain): 400.00 vs 800.00 |
| A vs C | A is a sum of billed rows; C has no billed rows and is a tariff projection | task 1: 1,212.00 vs 1,200.00 | no fee, active Weekly: 0 vs 1,200.00 |
| B vs C | B combines billed-to-date with one month of tariff; C is a tariff projection only | fee only Sep 400.00: 800.00 vs 1,200.00 | no fee, active Weekly: 400.00 vs 1,200.00 |
No pair differs only by a multiplier, window, constant or status filter: A has no tariff term, C has no billed-row term, B has both.

| policy | read site | probe (r2/probe11_out.txt) | result | rule tier |
|---|---|---|---|---|
| P4 | StockSmart tiers (round 11) | gold / Jul fee 250.00 / fees only Aug + Sep / fee only Sep / Aug + Sep with program closed / no fee + active Weekly / + active Twice-Weekly / no fee with program paused, enrolled, terminating, closed / no program | 149,087.00 / 148,937.00 / 149,087.00 / 148,675.00 / 148,687.00 / 149,075.00 / 0 / 147,875.00 x4 / 147,875.00 | A 1,212 / A 1,062 / B 812 + 400 / B 400 + 400 / B 812 + 0 / C 1,200 / C 2,250, increase above desk authority: referred / C with no active program: nothing (no reserve on a paused program) / nothing |
Round-10 probe rows giving a paused, enrolled or terminating program one month's minimum (148,275.00 / 148,625.00) are superseded: that tier is gone.

### Round 12 (F-C23): P2 vendpoint_month_end_billing, auditor's normalised-shape test on every pair
Normalisation (revision_11): every aggregate of one field counts as one input whatever its window or filter; constant multipliers, weights and addends are ignored. u = monthly usage sums (u0/u1/u2), c = last month's cellular fees, f = largest min_monthly_usage_usd among the customer's ACTIVE VendPoint machines (model tariff parameter, 0 with none active).
| tier | domain | expression | normalised shape |
|---|---|---|---|
| T1 floored trend | usage in each of three months, rising each month | MX(u0 + (u0 - u1), f) + c | max(usage combination, tariff) + cellular |
| T2 three-month average | usage two whole months back, not rising | (u0 + u1 + u2) / 3 + c | usage combination + cellular |
| T3 latest-month selection | usage only within the last two whole months | (u0 if u0 > 0 else u1) + c | conditional pick of usage + cellular |
| T4 nothing | no usage in three whole months | 0 | (domain-coincidence test) |

| pair | shape test | distinguishing input (probe12 / probe9) |
|---|---|---|
| T1 vs T2 | pass: T1 adds a floor (max) and a tariff input T2 lacks | rising 300 < 500 < 600: 1,265.00 vs 481.67 |
| T1 vs T3 | pass: T1 has max + tariff, T3 a conditional pick; neither has the other's operation | usage only Aug 1,288.35 + Sep 1,530.90: T1 1,788.45 vs T3 1,545.90 |
| T2 vs T3 | pass: T3 is a conditional pick, T2 a fixed combination | gold: 1,425.62 vs 1,545.90 |
| T4 vs T1 | pass: on T4's domain T1 = f + c, non-zero with an active machine | no usage, active Coil 40: 1,265.00 vs 0 |
| T4 vs T2, T3 | pass: on T4's domain they give c, non-zero with a cellular fee | no usage, cellular 15.00: 15.00 vs 0 |
Realism: a rising machine's next bill is projected from its trend but never below the model's monthly minimum usage, the level the shortfall rule bills a machine up to; suspended / removal-pending machines carry no floor.

| policy | read site | probe (r2/probe12_out.txt) | result | rule tier |
|---|---|---|---|---|
| P2 | VendPoint T1 (round 12) | gold / rising with Aug 1,450.00 / rising 300 < 500 < 600 / same, machine suspended / same + active Coil 60 with no lines | 2,550.42 / 2,751.60 / 2,389.80 / 1,839.80 / 3,139.80 | T2 average / T1 trend 1,611.80 above floor / T1 floor 1,250.00 / T1 trend 700.00, no active floor / T1 floor 2,000.00 |


### Round 13 (renderer source scan r1): binding ownership, P1
Plain (shared) set now holds inv_date, pa_eff, pa_end, pa_in_force (read by in_scope and by contract_share) and pay_amt, inv_total, applied_out, returned_in, left_open, full_rate_disc (read by base_share and by paid_merch). payment_allocation_to_merchandise keeps [inv_freight_tax, paid_merch]; contract_share_of_rate keeps [pa_tier, contract_share]. New plain rule sentence for the payment amount and invoice total; the left-open definition stands as its own plain sentence, the allocation ladder as the next sentence. Mechanical sweep (r2/own.py) over P1-P4: no plain binding reads a factor-internal binding; plain bindings read factor outputs only in the assembly bindings (disc_rate, result; bo_counted, tol_used, result; coverage, result; step_used, step_room). Every scored value and sensitivity identical.

### Round 14 (KB audit SRC-2 / SRC-3 / SRC-4, seed only; charter and task_tools byte-identical)
- SRC-2 (task 1): the 12.00 par change fee had no par-change entries behind it; removed. StockSmart billed-fee sum 1,200.00 (three minimum fees), grant 149,075.00 approved_reduced (was 149,087.00); sensitivities 0 / 139,075 / 0 / 144,075 / 147,875 / 148,700 (all-baseline 150,000). The commitment projection gives the same 1,200.00 on this world; the pairwise inputs of the round-11 table are unchanged.
- SRC-3 (task 0): return records behind CM-129966 / CM-130418: RMA-1529966 and RMA-1530418 authorized (route pickup), received unopened, reason wrong item shipped (Corbett error: restocking fee waived, full credit 742.15 / 1,860.00, memo within 3 business days). Catch-up 128.08 unchanged; find_order_returns read added (eval step indices +1: discount 14, payment 16).
- SRC-4: StockSmart minimum fee every month since go-live (VMI-13306 2024-02.., VMI-16408 2025-03..); VendPoint usage bill (and cellular fee for VP-118204) every month since installation, billed to the machine's cost center (CC-1140 / CC-1630) with vend lines behind every bill, ramp-up months untested and every tested month at or above the model minimum; order lines (booked + shipped) behind every monthly consolidated statement, which bills the month's shipments, StockSmart fees and VendPoint usage and fees as merchandise. Task 0 freight is the Tool Room's 12.95 standard freight per parcel order under the 150.00 threshold (route freight free): one order in freight months, two in September; each statement's tax absorbs the freight difference so every invoice total and every freight-plus-tax sum stays as billed. INV-1488218: freight 25.90, tax 4,748.64 (freight + tax 4,774.54 unchanged, so the catch-up is unchanged); the room payment's tax ratio becomes 4,748.64 / 61,250.00 = 0.07753 -> 15,601.32 counted, room payment 2,619.61 (was 2,550.42), sensitivities 0 / 1,497.09 / 2,219.61 / 4,419.61 / 1,193.99; without the discount line 2,747.69. Task 1 orders: one Priority ground-parcel order a month (free freight above 100.00) and an order booked and shipped 2026-10-09 (the ship-to's last order date); find_order_lines read added (submit 14, decide 16).
- Probe tables re-run on the new worlds (r2/probe8..12_r14_out.txt): every room-payment probe moves by +69.19 with the tax ratio; limit-grant probes whose tier-A sum carried the par change fee move by -12.00; tiers, orderings and distinguishing inputs unchanged.
