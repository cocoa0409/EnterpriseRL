# vehicle_purchase_deals — instantiation plan (M=2, band 1) — ROUND 6 FINAL (round 6: F1 generic incentive assembly, shared order_account selection stated once); ROUND 4 (round 3: N1, N2, N3, T0-4; round 4: T1-3, R1, zero-amount ruling)

Draws (draw_counts.py --tasks 2, unchanged): task 0 prerequisite_problems=3, factor_counts=[5,6,5,5]; task 1 prerequisite_problems=1, factor_counts=[6,4].
Read domain: blueprint/, audits/render_source/XF_recipe.md, audits/policy_task/vehicle_purchase_deals/, erlbench/, skills/. Scratch: /tmp/vehicle_purchase_deals_0075/.
Cross category: `service` only (service_accounts, service_ro_lines). No maintenance, no trade-ins (the purchase ledger has no row carrying a trade allowance).
Note: between 03:53 and 04:02 another writer replaced this file, the charter and the tools with an unaudited variant; its files are kept in
/tmp/vehicle_purchase_deals_0075/foreign_writer_0353_0402/. Everything below is the audited round-1 design with the round-2 fixes.

## Policies / tools / values
| task | policy (computes) | tool (owner) | factors | gold | whole baseline |
|---|---|---|---|---|---|
| 0 | purchase_ext_fleet_delivery_fee (reversal_amount) | reverse_fleet_delivery_fee_7a0a59bd (agent) | 5 (4p/1m) | 26.33 | 0.00 |
| 0 | purchase_ext_fleet_unit_incentive (incentive_amount) | credit_fleet_incentive_b735a70c (agent) | 5 (4p/1m) | 2750.00 | 1150.00 |
| 0 | purchase_ext_fleet_late_balance_fee (fee_amount, 2026-10) | post_fleet_late_fee_7ed43dd7 (agent) | 6 (5p/1m) | 171.74 | 360.41 |
| 0 | purchase_ext_fleet_order_deposit ROOT (deposit_amount) | pay_fleet_order_deposit_c9caca35 (user, ach) | 5 (4p/1m) | 5066.79 | 3634.00 |
| 1 | purchase_ext_extension_deposit (deposit_amount) | pay_extension_deposit_9124466d (user, debit) | 6 (5p/1m) | 1940.49 | 1063.25 |
| 1 | purchase_ext_hold_extension_days ROOT (extension_days) | extend_vehicle_hold_21e7c68f (agent) | 4 (3p/1m) | 7 | 3 |
Edges: t0 order_deposit -> late_fee (state_gate, state, negated, record test incl. "balance still due above 0.00");
late_fee -> delivery_fee (value_input, ACTION form with fallback_reason: the check leaves an entry only when an excess exists);
late_fee -> unit_incentive (value_input, state, negated). t1 hold_extension_days -> extension_deposit (value_input, state, negated:
"a deposit received on the handling date stands on the deal"; N3: both extension policies cover only an extension asked for on a day after the reserved_date, and on such a deal any deposit added after the reserved_date is the extension deposit, so the waited-on record can only come from that write). Edge skips: late fee 171.90 / 188.12 (gold 171.74); extension 6 (gold 7).

## Factor tables: tier taken in the task world, T1 (that factor alone at baseline), T2 (a producible world where it alone moves)
delivery_fee (radius fixed at the deal type's 150 miles; no factor gates another):
- commercial_standing_share P,X,multi (Net30+0 late fees 12m 0.80 | Net15+0 0.90 | 1): 0.80; T1 0.00; T2 any Net 15 clean buyer.
- price_class_mile_rate P (vehicle_price >=60k 1.60 | 45k-60k 1.45 | 1.25): 1.45; T1 40.20; T2 any 45k unit.
- weekend_delivery P (Sat 45 | Sun 85 | 0): Sat; T1 56.93; T2 Sunday delivery.
- late_delivery_miles M (>15 days late: min(0.5*beyond, 50) | 1-15: max(0.5*beyond, beyond-4*days) | beyond): 102; T1 2.66; T2 20-days-late delivery (probe 77.60). N2: charged miles never rise with lateness for any distance (scan of beyond 1..150 x lateness 0..40: 0 violations).
- account_tenure_share P,X (>=60m 0.85 | 24-59m 0.95 | 1): 0.85; T1 3.18; T2 30-month account.
unit_incentive: unit_price_class P 1650 (T1 2250.00); quarterly_program P 500 (T1 2250.00, T2 May delivery); order_bank_lead P 300
(T1 2450.00, T2 20-day lead); registered_fleet_size P,X 350 (T1 2400.00, T2 Net 15); registration_report_timing M
(filed >10 days: summed - 25/day, floor half | unfiled: summed - 25 per day since delivery beyond 10, floor half | summed): T1 2800.00, T2 unfiled world (probe 1550.00).
late_balance_fee: payment_standing_rate P,X,multi 0.0100 (T1 210.78); open_credit_use P,X +0.0010 (T1 156.13); late_fee_history_basis M
(no earlier fee: prorate days/30 | earlier fee + later buyer payment: balance - earlier fees net of reversals | balance) T1 257.62;
paid_down_share P 0.90 (T1 190.83); service_early_payer P,X 0.95 (T1 180.78); down_payment_record P 0.95 (T1 180.78). Scope test:
credit-hold account -> base fee (probe 360.41).
order_deposit: commercial_standing_rate P,X 0.05 (T1 8670.03); service_late_history P,X +0.025 (T1 3265.18); extended_hold_rate P +0.02
(T1 3625.50); check_funds_rate P +0.01 (T1 4346.15); account_exposure_base M (credit hold: rate*price + whole open balance | active fleet
with open balance: rate*(price+open balance) | rate*price) T1 3940.70, T2 credit-hold buyer (probe 17732.40).
extension_deposit: rewards_tier_rate P,X 0.04 (T1 2293.30); returned_bank_payment_rate P,X +0.01 (T1 1587.67); hold_time_left_rate P
+0.005 (T1 1764.08); service_spend_record P,X 0.90 (T1 2156.10); deposit_received_record P 0.95 (T1 2042.62); deposit_funds_credit M
(card still held: max(0, held - card net of refunds) | recent check: 0 | held) T1 940.49. Credit capped at max_credit_share 0.6 of the extension deposit required before shares, stated in the baseline paragraph (rounds 4-5: something is always owed, 0.765 > 0.6); minimum min_extension_deposit_usd 250 applies only to a positive amount owed.
hold_extension_days: deposit_cover P,multi +1 (T1 6); service_visit_record P,X +1 (T1 6); service_tenure_days P,X +1 (T1 6);
extension_start_day M (Sat/Sun expiry: 7 - weekday | weekday + recent check: max(0, DAYS(expiry, check)+10) | 0) T1 6, T2 Saturday expiry (offset 2).

## All-pairs method tables (distinguishing input per pair)
late_delivery_miles: half-share capped (min-pick with cap) vs per-day credit (days input, max-pick floor) vs plain.
registration_report_timing: filed-lag deduction (title date) vs unfiled deduction (handling date) vs plain.
late_fee_history_basis: prorate (days) vs net of earlier fees (late-fee sums) vs plain balance.
account_exposure_base: rate*price + open balance (balance unscaled) vs rate*(price + open balance) (balance scaled) vs rate*price.
deposit_funds_credit: held - card (card sums) vs 0 (held absent; not zero elsewhere) vs held.
extension_start_day: 7 - weekday (weekday input) vs check-clearing day (check date input) vs 0.

## Read probe table (decoy / absent record per read; date anchors)
| read | decoy / edge | rule |
|---|---|---|
| CFIELD service (status filters active / credit_hold) | one account per customer (service_agg_multi_holding); closed account -> None -> fall-through (probe 195.16); credit hold -> late fee base scope, order deposit tier A | stated |
| reinstated account | records keep no hold history; current status decides (scope test is a coarse exact record test) | stated in scope sentence |
| XCOUNT service late fees 12m / 24m | 2025-08-05: 14 months (outside 12, inside 24); month-end: MONTHS() whole-month convention, e.g. 2024-10-31 -> 2026-10-21 = 23 | window sentence |
| XCOUNT returned service payments | t1 counts check+ACH only (card chargebacks excluded); t0 counts any returned payment | stated per rule |
| XSUM spend 12m / XCOUNT line-A labor 12m | RO 512248 (13 months) excluded; one count per RO via line A | stated |
| SUM vehicle_price charged | read by one factor per policy (C8); 0 when no contract charge -> lowest class | stated |
| SUM home_delivery_fee net of reversals | earlier partial reversal subtracted; distance within radius -> whole posted fee reversed (probe 157.50) | b5 / free |
| COUNT/SUM/LATEST late fees on deal | reversed earlier fee still "carries an earlier fee", subtracted net of reversal (probe 257.62); same-day payment is not "later" | basis sentence |
| SUM buyer payments | deposit_transfer, lender_funding, manufacturer_incentive excluded; returned subtracted | part sentence |
| deposits (card / check / collected) | refunded card deposit: credited max(0, held - net card) (probe 1940.25); refunded debit: no collected funds (probe 6); same-day tie: a hold extension asked for on the reserved_date is outside both extension policies (base extension 3 days, deposit 0 / not taken; probes 3 and 0), so a reservation-day deposit can never meet the t1 wait (N3) | stated |
| title_application_date | None -> unfiled tier, days since delivery (probe 1550.00); negative lags impossible (filing after delivery) | report sentence |
| date anchors | late fee: delivery + 40 (day 0 = delivery, exclusive) and days after it floored at 0; delivery window: contract + 30 (day 0 = contract); hold: reserved + hold days, expiry weekday via DAYS from Monday 2000-01-03; order lead: contract -> delivery; tenure: MONTHS(opened, NOW) | stated |
| zero / negative | reversal floored at 0 (then nothing is booked); deposits: order floored at 0 (probe 0.0), extension floored at 250 (probe 250.0); credit_limit 0 -> no add-on; incentive deductions floored at half | stated |

## Rounding contract (round 4 ruling)
Every rule: "rounded to the cent, half up" at the last step (late fee: before the minimum comparison). Compute writes every money rounding as
RND(x + 0.000000001, 2) on a non-negative amount (7 sites): exact ties round up (probe 0.0125 x 4420.40 = 55.255 -> 55.26) and no finite-decimal
non-tie with at most 8 places moves. Checked (r4_check): of the 52 RND arguments evaluated for every scored, baseline and factor-sensitivity figure of
both tasks, every figure sits more than 1e-6 from a half cent; the only exact-tie arguments left are task-0 intermediates of the delivery fee under a
factor's baseline (163.965 and the like), whose rounded value is then compared with the 157.50 posted fee and gives the same figure (0.00) whichever
way it rounds. Task 1's cash_price moved 41260.00 -> 41265.00 to clear the ties 1763.865 and 2155.835 (closest argument now 0.00125 from a tie).
Tool bodies: _Money.cents (Decimal ROUND_HALF_UP).

## Zero-amount edges (recipe 19 + round-4 ruling: no floor creates an amount on nothing owed)
- order deposit waits on the late fee: the wait covers only delivered fleet deals with a balance still due above 0.00, where the fee is >= 50.00;
  the late-fee compute returns 0 (no fee, minimum not applied) when balance_due <= 0 (rule sentence added in round 4).
- late fee waits on the incentive credit, which for a qualifying deal is never below report_floor_share x summed incentive (>= 575.00).
- late fee waits on the delivery-fee check (action form "checked ... and any excess reversed"): with no excess nothing is booked and the check
  itself meets the wait ("a fee posted at or below the fleet home delivery fee is left as posted").
- extension days wait on the extension deposit: credited deposits are capped at max_credit_share (0.6) of the extension deposit required before shares (baseline paragraph, round 5); every share product is >= 0.765, so a
  positive amount is always owed; the 250.00 minimum only raises a positive amount. Out of scope (request on the reservation date) nothing waits.
- order deposit (root) may compute 0.00 when the deposit held covers the requirement: nothing is collected and nothing waits on it.

## Events written by my tools and base triggers (XF18)
| tool | event | base triggers |
|---|---|---|
| reverse_fleet_delivery_fee_7a0a59bd | purchase_charge_reversed (home_delivery_fee, source = the posted fee) + balance_due | [] |
| credit_fleet_incentive_b735a70c | purchase_payment_posted (manufacturer_incentive) + balance_due | [] |
| post_fleet_late_fee_7ed43dd7 | purchase_charge_posted (late_balance_fee, billing_month) + balance_due | [] |
| pay_fleet_order_deposit_c9caca35 (user) | purchase_deposit_received (ach) + deposit_held_balance | [] |
| pay_extension_deposit_9124466d (user) | purchase_deposit_received (debit_card) + deposit_held_balance | [] |
| extend_vehicle_hold_21e7c68f | purchase_hold_extended (hold_expires_date, hold_extension_count) | [] |
Tools enforce only published formats: amount > 0 after half-up cents, billing_month YYYY-MM, whole days > 0, reversal source = a
home_delivery_fee charge of the same deal; otherwise "Error:" and nothing written.

## Defining-sentence table (recipe A4): every rule sentence -> the baseline or the single factor / plain role that uses it
| policy | sentence | opens with | used by |
|---|---|---|---|
| purchase_ext_fleet_delivery_fee | scope | For a Fleet Vehicle Purchase Agreement delivered by home delivery beyo... | scope + out-of-scope base fee + posting once per deal on the delivery date (overwrite replaced_by, N1) |
| purchase_ext_fleet_delivery_fee | posting (REMOVED in round 3; its content now sits in the scope sentence, N1) | Every home delivery fee, this one included, is posted once per deal un... | in-force posting restated (plain) |
| purchase_ext_fleet_delivery_fee | b1 | The fleet home delivery fee is figured from the deal's recorded one-wa... | baseline |
| purchase_ext_fleet_delivery_fee | b2 | The chargeable delivery miles are the miles of that distance beyond th... | baseline |
| purchase_ext_fleet_delivery_fee | b3 | The delivery mileage charge is the chargeable delivery miles times the... | baseline |
| purchase_ext_fleet_delivery_fee | b4 | The fleet home delivery fee is the delivery mileage charge rounded to ... | baseline |
| purchase_ext_fleet_delivery_fee | free | A fleet delivery whose distance does not exceed the deal type's home_d... | baseline (in-force within-radius rule; plain binding fleet_delivery_fee) |
| purchase_ext_fleet_delivery_fee | b5 | The excess reversed is the home delivery fee posted on the deal, less ... | baseline (plain binding posted_delivery_fee / result) |
| purchase_ext_fleet_delivery_fee | corr | A home delivery fee found posted on such a fleet deal above the fleet ... | plain: correction booking (result) |
| purchase_ext_fleet_delivery_fee | asm | Where an amount is added to the delivery mileage charge and shares app... | assembly (plain fleet_delivery_fee) |
| purchase_ext_fleet_delivery_fee | standing | A buyer in good commercial standing pays a standing share of the fee: ... | factor commercial_standing_share |
| purchase_ext_fleet_delivery_fee | window12 | A service late fee falls in the last 12 whole months when fewer than 1... | factor commercial_standing_share (its window) |
| purchase_ext_fleet_delivery_fee | rate | The per-mile delivery rate for a fleet unit follows the vehicle price ... | factor price_class_mile_rate |
| purchase_ext_fleet_delivery_fee | weekend | A fleet delivery made on a weekend carries a weekend delivery surcharg... | factor weekend_delivery |
| purchase_ext_fleet_delivery_fee | timely | How the chargeable delivery miles are counted depends on when the unit... | factor late_delivery_miles |
| purchase_ext_fleet_delivery_fee | tenure | A long-standing commercial customer pays a tenure share of the fee set... | factor account_tenure_share |
| purchase_ext_fleet_unit_incentive | scope | A qualifying fleet deal is a Fleet Vehicle Purchase Agreement in deliv... | scope (overwrite replaced_by) |
| purchase_ext_fleet_unit_incentive | b1 | The fleet unit incentive credited on a qualifying deal is the deal typ... | baseline |
| purchase_ext_fleet_unit_incentive | b2 | The fleet unit incentive is rounded to the cent, half up, and credited... | baseline |
| purchase_ext_fleet_unit_incentive | asm | Every amount added to the per-unit amount is added first, giving the s... | assembly, generic (round 6, F1: names no factor quantity) (plain summed_incentive / result) |
| purchase_ext_fleet_unit_incentive | cls | The per-unit amount follows the unit's price class, read from the vehi... | factor unit_price_class |
| purchase_ext_fleet_unit_incentive | quarter | The manufacturer's quarterly fleet program adds program cash by the ca... | factor quarterly_program |
| purchase_ext_fleet_unit_incentive | order | A unit ordered ahead of delivery earns an order-bank bonus by the cale... | factor order_bank_lead |
| purchase_ext_fleet_unit_incentive | size | The size of the buyer's registered fleet, shown by the buyer's commerc... | factor registered_fleet_size |
| purchase_ext_fleet_unit_incentive | report | How promptly the unit's registration was reported sets how the summed ... | factor registration_report_timing |
| purchase_ext_fleet_late_balance_fee | scope | For a Fleet Vehicle Purchase Agreement whose buyer's service account i... | scope + out-of-scope base fee (plain base_scope_fee; overwrite replaced_by) |
| purchase_ext_fleet_late_balance_fee | pre_hdf | The fleet late balance fee is fixed only after the home delivery fee p... | prerequisite (action form) |
| purchase_ext_fleet_late_balance_fee | pre_inc | The fleet late balance fee is not worked out until the manufacturer fl... | prerequisite (state form) |
| purchase_ext_fleet_late_balance_fee | b1 | The fleet late balance fee for a billing month is the deal type's late... | baseline |
| purchase_ext_fleet_late_balance_fee | b2 | The fee basis is the balance_due standing on the deal at assessment.... | baseline |
| purchase_ext_fleet_late_balance_fee | b3 | The fleet late balance fee is rounded to the cent, half up, and is nev... | baseline |
| purchase_ext_fleet_late_balance_fee | asm | Any add-on to the monthly rate is added to it first; the resulting rat... | assembly (plain monthly_rate / fee_before_rounding / result) |
| purchase_ext_fleet_late_balance_fee | standing | The monthly rate follows the buyer's payment standing: a buyer holding... | factor payment_standing_rate |
| purchase_ext_fleet_late_balance_fee | window | A service ledger entry falls in the last 12 or 24 whole months when fe... | shared window convention (payment_standing_rate 24m, service_early_payer 12m) — a definition, no quantity |
| purchase_ext_fleet_late_balance_fee | credit | A fleet buyer drawing on the service account's open credit pays a cred... | factor open_credit_use |
| purchase_ext_fleet_late_balance_fee | basis | How the fee basis is taken depends on the deal's late balance fee hist... | factor late_fee_history_basis |
| purchase_ext_fleet_late_balance_fee | part | A buyer who has paid down the deal earns a part-payment share: the buy... | factor paid_down_share |
| purchase_ext_fleet_late_balance_fee | early | A buyer who pays service invoices early earns an early-payment record ... | factor service_early_payer |
| purchase_ext_fleet_late_balance_fee | down | A buyer who put money down on the deal earns a down-payment share: whe... | factor down_payment_record |
| purchase_ext_fleet_order_deposit | scope | For a reserved Fleet Vehicle Purchase Agreement this policy sets the o... | scope (in-force deposit limits restated) |
| purchase_ext_fleet_order_deposit | pre | A fleet order deposit is not taken on a reserved unit until every deli... | prerequisite (state form) |
| purchase_ext_fleet_order_deposit | b1 | The fleet order deposit to collect is the order deposit required on th... | baseline |
| purchase_ext_fleet_order_deposit | b2 | The order deposit required is the order deposit rate times the unit's ... | baseline |
| purchase_ext_fleet_order_deposit | b3 | The fleet order deposit to collect is rounded to the cent, half up, an... | baseline |
| purchase_ext_fleet_order_deposit | asm | Every add-on to the order deposit rate is added to it first; the resul... | assembly (plain deposit_rate_total / result) |
| purchase_ext_fleet_order_deposit | sel | The buyer's active service account is the buyer's service account in a... | shared selection stated once (round 6): plain order_account, read by commercial_standing_rate and account_exposure_base |
| purchase_ext_fleet_order_deposit | rate | The order deposit rate follows the buyer's commercial standing: a buye... | factor commercial_standing_rate |
| purchase_ext_fleet_order_deposit | late | A buyer whose service ledger shows late fees adds a late-history rate ... | factor service_late_history |
| purchase_ext_fleet_order_deposit | window | A service late fee falls in the last 24 whole months when fewer than 2... | factor service_late_history (its window) |
| purchase_ext_fleet_order_deposit | hold | A unit held beyond the deal type's standard hold adds a held-unit rate... | factor extended_hold_rate |
| purchase_ext_fleet_order_deposit | check | Deposits paid by check add a check-funds rate to the order deposit rat... | factor check_funds_rate |
| purchase_ext_fleet_order_deposit | exposure | What the rate is applied to depends on the buyer's service account: fo... | factor account_exposure_base |
| purchase_ext_extension_deposit | scope | For a reserved deal of any deal type other than Fleet Vehicle Purchase... | scope (in-force deposit limits restated) |
| purchase_ext_extension_deposit | nofee | For a reserved deal of any deal type other than Fleet Vehicle Purchase... | overwrite replaced_by of 'Extensions carry no fee and leave the deposit unchanged.' (C1; round 3 adds the reservation-date carve-out, N3) |
| purchase_ext_extension_deposit | kind | On such a deal, a deposit the buyer adds on a day after the reserved_date is the extension depo... | scope: the extension deposit is the only deposit added after the reservation date (N3); plain binding requested_on_reserved_date |
| purchase_ext_extension_deposit | b1 | The extension deposit to collect is the extension deposit required les... | baseline |
| purchase_ext_extension_deposit | b2 | The extension deposit required is the extension deposit rate times the... | baseline |
| purchase_ext_extension_deposit | b3 | Every deposit received on the deal and still held (deposit_held_balanc... | baseline |
| purchase_ext_extension_deposit | b4 | The extension deposit to collect is rounded to the cent, half up, and ... | baseline (minimum) |
| purchase_ext_extension_deposit | asm | Every add-on to the extension deposit rate is added to it first; the r... | assembly (plain extension_rate / result) |
| purchase_ext_extension_deposit | tier | The extension deposit rate follows the buyer's Owner Rewards standing:... | factor rewards_tier_rate |
| purchase_ext_extension_deposit | ret | Returned payments on the buyer's service account add a returned-paymen... | factor returned_bank_payment_rate |
| purchase_ext_extension_deposit | window | A service ledger entry falls in the last 12 or 24 whole months when fe... | shared window convention (returned 24m, spend 12m) — a definition |
| purchase_ext_extension_deposit | timing | The time left on the hold when the extension deposit is taken adds a h... | factor hold_time_left_rate |
| purchase_ext_extension_deposit | spend | The buyer's customer-pay service spend sets a service-spend share: whe... | factor service_spend_record |
| purchase_ext_extension_deposit | resv | The deposits received on the deal set a deposit-received share: where ... | factor deposit_received_record |
| purchase_ext_extension_deposit | credit | Which deposits are credited toward the extension deposit required depe... | factor deposit_funds_credit |
| purchase_ext_hold_extension_days | scope | For a reserved deal of any deal type other than Fleet Vehicle Purchase... | scope (requests after the reserved_date) + fleet / reservation-date base extension restated (overwrite replaced_by, N3); plain binding requested_on_reserved_date |
| purchase_ext_hold_extension_days | one | Each request a buyer makes is handled as one extension of the hold; a ... | request scope: one request = one extension (T1-1) |
| purchase_ext_hold_extension_days | pre | The extension days are not worked out until a deposit received on the ... | prerequisite (state form) |
| purchase_ext_hold_extension_days | b1 | One hold extension moves the hold forward by the extension length coun... | baseline |
| purchase_ext_hold_extension_days | b2 | The extension length is the deal type's hold_extension_days calendar d... | baseline |
| purchase_ext_hold_extension_days | b3 | The extension days passed are the calendar days from the current hold_... | baseline |
| purchase_ext_hold_extension_days | asm | Every added day is added to the deal type's hold_extension_days first,... | assembly (plain extension_length / result) |
| purchase_ext_hold_extension_days | cover | A buyer whose deposits cover a larger part of the price is held longer... | factor deposit_cover |
| purchase_ext_hold_extension_days | visits | A buyer who services a vehicle with the group is held longer: where th... | factor service_visit_record |
| purchase_ext_hold_extension_days | window | A service repair order falls in the last 12 whole months when fewer th... | factor service_visit_record (its window) |
| purchase_ext_hold_extension_days | tenure | A long-standing service customer is held longer: where the buyer's act... | factor service_tenure_days |
| purchase_ext_hold_extension_days | start | The extension's starting day depends on how the hold stands: where the... | factor extension_start_day |

## Mechanical decoy probes (round 3, r3_check.py on scratch copies of the task worlds; decoy / absent / tie / month-end / zero-amount)
| probe | result |
|---|---|
| late fee, gold world | 171.74 |
| late fee, decoy earlier fee posted then reversed, ACH after it (basis net 0) | 257.62 |
| late fee, balance 16000.00 (non-tie control): 16000*(20/30)*0.011*0.9*0.95*0.95 = 95.304 -> 95.30 | 95.3 |
| late fee, exact tie: credit-hold base fee 0.0125*2420.40 = 30.255 -> min 50 | 50.0 |
| late fee, exact tie: credit-hold base fee 0.0125*4420.40 = 55.255 -> half up 55.26 | 55.26 |
| late fee, decoy closed service account -> fall-through rate | 195.16 |
| delivery fee, distance within radius -> whole posted fee reversed | 157.5 |
| delivery fee, 20 days late (Saturday) -> min(0.5*126, 50) = 50 miles | 77.6 |
| incentive, absent title filing -> 2800 - 25*50 = 1550 | 1550.0 |
| incentive, month-end delivery 2026-03-31 -> Q1, no program cash | 2150.0 |
| order deposit, credit hold -> rate*price + whole open balance - held | 17732.4 |
| order deposit, zero edge: deposit held covers requirement -> 0 (nothing collected) | 0.0 |
| extension deposit, same-day tie (reserved on the handling date) -> out of scope, 0 | 0 |
| extension days, same-day tie -> base hold_extension_days 3 | 3 |
| extension deposit, held 5000.00 by debit card | superseded by the round-5 probe below (374.48) |
| extension days, Saturday expiry -> offset 2 | 7 |

## Round-4 probes (r4_probe on scratch copies)
| probe | result |
|---|---|
| late fee, zero edge: balance_due 0.00 -> no fee (0), minimum not applied | 0 |
| late fee, credit-balance deal on a credit-hold account -> 0 | 0 |
| late fee, exact tie: credit-hold base fee 0.0125 x 4420.40 = 55.255 -> 55.26 (half up) | 55.26 |
| extension deposit, held 5000.00 by debit card (round 5 cap before shares): 0.055 x 41265 = 2269.575 x 0.90 x 0.85 = 1736.22, credit min(5000, 0.6 x 2269.575 = 1361.75) -> 374.48 owed | 374.48 |
| extension deposit, auditor R4-1 world (Service Guest Account, no service lines, 2000.00 cash, more than 4 days left): every factor at baseline 2063.25 - min(2000, 1237.95) = 825.30 = baseline paragraph; with the deposit-received share 0.95 firing -> 722.14 | 825.30 / 722.14 |
| extension deposit, same-day request -> out of scope, 0 (nothing waits) | 0 |
| extension days, same-day request -> base 3 | 3 |
