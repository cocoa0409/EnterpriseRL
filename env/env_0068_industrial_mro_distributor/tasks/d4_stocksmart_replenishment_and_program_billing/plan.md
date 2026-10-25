# d4_stocksmart_replenishment_and_program_billing — plan (M=2)

## Draws (draw_counts.py --tasks 2)
- task 0: prerequisite_problems=2, factor_counts=[6,5,6]
- task 1: prerequisite_problems=2, factor_counts=[6,4,5]

## Hard constraints discovered at Step 0
- SKILL Principle D: no task tool may write a row of an event whose trigger fires into another category.
  vmi_replenishment_billed, vmi_program_fee_charged, vmi_buyback_billed, vmi_consumption_billed all carry an
  unconditional trigger to credit:credit_invoice_posted -> NO fee / billing / buyback tool in this difficulty.
  Numeric vmi events without triggers: vmi_bin_set (min/max), vmi_replenishment_delivered, vmi_consignment_stocked,
  vmi_consignment_consumed, vmi_shrink_billed, vmi_consignment_withdrawn.
- Owner=user: only bin requests carry a number a customer's own written act can hold (termination notice has no
  numeric field). "A bin is flagged critical only at the customer's written request" grounds a user-owned bin_set.
- DSL: compute sees only the world; target object of each computation pinned by a record (LATEST of a seeded or
  prior-written row), ties avoided by filters; no calendar-month windows on rows without billing_period.
- XLATEST over pricing_items cannot exclude future-dated lines -> scope clause + guard (count of lines effective
  on/before today vs all lines) where a price is read.

## Design (v1)
- Task 0 (Twice-Weekly consignment program, credit active): item moved out of a VendPoint machine goes onto consignment.
  - P0a user  vmi_ext_vended_item_fill_level  (vmi_bin_set new_bin consigned) computes max_qty  [6]
  - P0b agent vmi_ext_removal_count_shrink    (vmi_shrink_billed) computes quantity           [5]
  - P0c agent vmi_ext_opening_consignment     (vmi_consignment_stocked) computes quantity     [6]  ROOT
  - edges: P0c<-P0a value_input (fill-to level); P0c<-P0b state_gate (consigned value cap headroom)
- Task 1 (Twice-Weekly consignment program, credit ON HOLD, critical_items_only): slow mover converted at par review.
  - P1a agent vmi_ext_conversion_reorder_point (vmi_bin_set par_change consigned=false) computes min_qty [4|5]
  - P1b user  vmi_ext_critical_fill_level      (vmi_bin_set par_change critical) computes max_qty       [5|4]
  - P1c agent vmi_ext_hold_converted_fill      (vmi_replenishment_delivered) computes quantity          [6]  ROOT
  - edges: P1c<-P1b value_input (fill-to + critical), P1b<-P1a value_input (reorder point feeds fill-to)

## Design v2 (supersedes v1; reasons below)
- Shrink (v1 P0b) dropped: absorbed within-tolerance shrink has no booking event (books would carry phantom units).
- Withdrawal as a computed problem dropped: units withdrawn = units on the books, no business variation to ladder.
- Ties: two bin entries written the same day are only read where they agree (the later entry copies max/critical).

Task 0 (StockSmart Twice-Weekly Service, credit active) — item taken out of a VendPoint machine goes onto consignment
  - P0a user  vmi_ext_vended_item_fill_level      vmi_bin_set new_bin consigned=true      max_qty   [6]
  - P0b agent vmi_ext_consigned_reorder_point     vmi_bin_set par_change (copies max)      min_qty   [6]
  - P0c agent vmi_ext_opening_consignment          vmi_consignment_stocked                  quantity  [5]  ROOT
  - edges: P0b<-P0a value_input (pins the new bin, copies fill-to); P0c<-P0a value_input (fill-to); P0c<-P0b value_input (reorder point in trial level)
Task 1 (StockSmart Onsite Storeroom, credit ON HOLD past_due, critical_items_only cap 10000) — slow consigned item converted at par review
  - P1a user  vmi_ext_converted_critical_fill     vmi_bin_set par_change critical=true     max_qty   [6]
  - P1b agent vmi_ext_conversion_reorder_point    vmi_bin_set par_change consigned=false   min_qty   [5]  (copies max/critical)
  - P1c agent vmi_ext_hold_converted_fill         vmi_replenishment_delivered              quantity  [4]  ROOT
  - edges: P1b<-P1a value_input (critical flag under hold -> safety days); P1c<-P1b state_gate (bin customer-owned);
           P1c<-P1a value_input (fill-to, critical)

## Task 0 factor plan (final candidate)
Pins: removal = the customer's latest VendPoint selection removal (XLATEST planogram, change_source customer; same-day guard);
      demand = net vends (issued - returned - vend errors) of the item at the machine it was removed from.
P0a fill-to (user, new consigned bin): ceil(weekly usage x total cover weeks x ABC share x exposure share)
  a1 usage_trend   method  rising -> highest month x12/52 ; falling -> latest month x12/52 ; else 3-month net /13 (baseline)
  a2 restock_cover param   multi-source tier visits x scheduled visits completed last month: 0.5 / 1.0 / 2.0 (baseline)
  a3 route_cover   param   cross order route deliveries/week: 0 -> +1.0 ; 1-2 -> +0.5 ; 3+ -> +0 (baseline)
  a4 vend_safety   param   cross vending emergency restocks of the item, 3 months: >=2 -> +1.0 ; 1 -> +0.5 ; 0 -> 0
  a5 abc_share     param   annual usage value (12-month net vends x latest vend price): A -> 0.75 ; B -> 0.9 ; C -> 1.0
  a6 exposure      param   cross credit returned payments 12 months: >=2 -> 0.6 ; 1 -> 0.8 ; 0 -> 1.0
P0b reorder point (agent, par_change on the new bin, copies fill-to): ceil(daily usage x reorder days) + draw buffer
  r1 gap_basis     method  daily onsite tier -> 1 day ; missed visits -> 30/completed ; else 30/scheduled
  r2 backorder     param   cross order backorders of item at ship-to, 3 months: open -> ; filled -> ; none -> 0
  r3 expedite      param   cross order next-day-air bookings of item at ship-to, 6 months
  r4 route_lead    param   cross order route deliveries/week (reuse of a3 evidence, different quantity: lead days)
  r5 draw_buffer   param   cross vending largest single vend of the item
  r6 supply_lead   param   special item (vending selection flag) / non-stock special-order history at ship-to / catalog
P0c opening consignment (agent, root): floor(target x credit share x pause share x site share x cap share)
  s1 trial_level   method  all vends in last 3 months -> reorder point ; all within 6 months -> midpoint ; else fill-to
  s2 credit_use    param   cross credit receivable / limit: >=90% ; 75-90% ; else 1.0
  s3 shutdown_hold param   planned plant-shutdown pause starting within 14 days ; 15-45 days ; none
  s4 new_site      param   cross order ship-to opened < 6 months ; 6-11 months ; else
  s5 cap_share     param   program consigned book value / consigned value cap: >90% ; 75-90% ; else

## Probe table — task 0 (scratch copies of the seed, probe_t0.py; base results 22 / 17 / 12)
| policy | read probed | decoy / edge | result | rule tier that decides it |
|---|---|---|---|---|
| fill level | XLATEST planogram removal (customer) | later removal by Corbett (slow_mover) of another item | 22 (unchanged) | pin counts only removals "made at the customer's request" |
| fill level | same | second customer removal on the same latest date | 0 | "where two or more such removals carry that most recent effective date ... no fill-to level" |
| fill level | same | no removal at all (absent record) | 0 | "or the customer has none" |
| fill level | XCOUNT credit returned payments | returned payment of another customer on another account | unchanged (a decoy on this customer's account id is counted, as it should) | customer scope |
| fill level | vend_price None | no vend at demand machine | value 0 -> class C | "zero where it has no vend there" |
| reorder point | LATEST consigned new_bin | older consigned new-bin entry (June) | 17 (unchanged) | "most recent new-bin entry" |
| reorder point | same | second consigned new bin the same day | 0 | tie sentence |
| reorder point | XMAX largest vend | 9-unit vend at the locker | 17 (unchanged) | "at the demand machine" |
| reorder point | gap division | visits_done 0 / tier 0 visits | guarded tiers | "at least one but fewer"; "tier scheduling no visits -> 7 days" |
| opening stock | LATEST par min_qty | no par entry (absent) | 6 | "zero where it has none" |
| opening stock | CFIELD credit | credit limit 0 (zero division) | 9 | "an account with no credit limit counting as 0.9 or more" |
| opening stock | CFIELD order opened_date | other ship-to (2014) is filtered by the program's ship-to | unchanged | "the program's ship-to" |
| opening stock | return rate | no vends in window | share 1 | "or no vends in those months, puts 1" |
Credit holds one account per customer (credit charter), so the unfiltered CFIELD on credit has a single candidate.

## Probe table — task 1 (probe_t1.py; base results 15 / 10 / 7)
| policy | read probed | decoy / edge | result | rule tier that decides it |
|---|---|---|---|---|
| critical fill | LATEST withdrawal | older withdrawal (July) of another item | 15 | "most recent consignment withdrawal" |
| critical fill | same | second withdrawal the same day | 0 | tie sentence |
| critical fill | same | no withdrawal (absent) | 0 | tie/absent sentence (no converted item) |
| critical fill | SUM consumption 12 months | 2025-09 consumption (age 12) | excluded | "last twelve months" (age below twelve) |
| critical fill | limit use | credit limit 0 (zero division) | treated 1.0 or more | "no credit limit counting as 1.0 or more" |
| conversion reorder | CFIELD credit status/reason | account active, bin critical | 8 | "an account not on hold adds none" |
| hold fill | XLATEST price line | future-dated repricing line | 0 | "a price line that takes effect after today is outside" |
| hold fill | SUM critical deliveries | non-critical line at the visit | 7 | "critical replenishment already delivered" |
| hold fill | same | critical line at yesterday's visit | 7 | "at the same visit" (latest visit reference) |
| hold fill | CFIELD credit status | account active | 15 | active -> whole fill-to |
| hold fill | LATEST critical flag | bin not critical during hold | 0 | "any other bin while the account is not active is not filled" |
| hold fill | division by price | no price line | 0 (out of scope; capped_units guarded) | scope sentence |

## Round 2 design changes (audit revision_1)
- Task 1 moved to StockSmart Twice-Weekly Service (500-bin gate reachable with a 518-entry roster; Onsite would need 1,500 bins).
- Both worlds now carry a full bin roster, scheduled visits since 2026-09-03 with replenishment delivered and billed lines, contract price lines for every replenished item and a credit invoice per billed visit; receivables kept at 149,630.40 and 448,680.00.
- Methods replaced (F1): P0a trend = projection / recency-weighted / average; P0b demand rate = peak / peak-and-mean blend / average; P4 draw = peak / blend / average; P5 safety = spread-based / proportional / none. P6 hold_service dropped (F4); P6 is scoped to the hold, with payment_release added.

## Probe table — round 2 (probe_all.py on scratch copies; every LATEST / first-match / CFIELD read, absent, None, zero-division and date-edge case)
| task | probe | policy | result | expected reading |
|---|---|---|---|---|
| 0 | base | vmi_ext_vended_item_fill_level | 26 | 26 |
| 0 | decoy: later Corbett slow-mover removal of another item | vmi_ext_vended_item_fill_level | 26 | 26 (customer removals only) |
| 0 | decoy: second customer removal same date | vmi_ext_vended_item_fill_level | 0 | 0 (tie sentence) |
| 0 | absent: no customer removal | vmi_ext_vended_item_fill_level | 0 | 0 |
| 0 | decoy: locker vend of 9 units | vmi_ext_vended_item_fill_level | 26 | 26 (other machine) |
| 0 | decoy: returned payment dated 2025-10-15 (age 12) | vmi_ext_vended_item_fill_level | 26 | 26 (outside twelve months) |
| 0 | date edge: returned payment dated 2025-10-16 (age 11) | vmi_ext_vended_item_fill_level | 19 | 2 returned -> share 0.6 |
| 0 | None: no vend at demand machine (price None) | vmi_ext_vended_item_fill_level | 0 | defined (value 0) |
| 0 | zero: scheduled visits none in latest month | vmi_ext_vended_item_fill_level | 36 | standard 2-week cover |
| 0 | base | vmi_ext_consigned_reorder_point | 19 | 19 |
| 0 | decoy: older consigned new bin (June) | vmi_ext_consigned_reorder_point | 19 | 19 |
| 0 | decoy: second consigned new bin today | vmi_ext_consigned_reorder_point | 0 | 0 (tie) |
| 0 | decoy: second customer removal of 43318 same date at the locker | vmi_ext_consigned_reorder_point | 0 | 0 (tie) |
| 0 | zero-month: a month without net vends | vmi_ext_consigned_reorder_point | 12 | standard rate |
| 0 | special: locker selection flagged special | vmi_ext_consigned_reorder_point | 23 | supply 4 days |
| 0 | absent: no vend ever (XMAX 0) | vmi_ext_consigned_reorder_point | 0 | defined, buffer none |
| 0 | decoy: backorder opened in June filled in September | vmi_ext_consigned_reorder_point | 19 | some opened, more filled -> 1 day |
| 0 | base | vmi_ext_opening_consignment | 13 | 13 |
| 0 | absent: no par entry | vmi_ext_opening_consignment | 8 | reorder 0 |
| 0 | decoy: second par entry with lower reorder point | vmi_ext_opening_consignment | 13 | 13 (highest reorder point) |
| 0 | zero: credit limit 0 | vmi_ext_opening_consignment | 11 | tight share 0.7 |
| 0 | date edge: ship-to opened 2026-04-15 (age 6) | vmi_ext_opening_consignment | 13 | 0.9 |
| 0 | date edge: ship-to opened 2026-04-16 (age 5) | vmi_ext_opening_consignment | 10 | 0.7 |
| 0 | zero: no vends in three months (return rate) | vmi_ext_opening_consignment | 15 | share 1 |
| 1 | base | vmi_ext_converted_critical_fill | 19 | 19 |
| 1 | decoy: older withdrawal of another item | vmi_ext_converted_critical_fill | 19 | 19 |
| 1 | decoy: second withdrawal same date | vmi_ext_converted_critical_fill | 0 | 0 (tie) |
| 1 | absent: no withdrawal | vmi_ext_converted_critical_fill | 0 | 0 |
| 1 | absent: item never consumed | vmi_ext_converted_critical_fill | 0 | draw zero -> 0 |
| 1 | zero: credit limit 0 | vmi_ext_converted_critical_fill | 19 | share 0.75 |
| 1 | date edge: consumption dated 2025-10-08 (age 12) | vmi_ext_converted_critical_fill | 19 | excluded |
| 1 | base | vmi_ext_conversion_reorder_point | 8 | 8 |
| 1 | account active (critical no longer matters) | vmi_ext_conversion_reorder_point | 7 | 7 |
| 1 | decoy: older critical entry of the bin (2024) | vmi_ext_conversion_reorder_point | 7 | hold lead 0 (latest-date entries only) |
| 1 | absent: nothing billed in twelve months (zero division) | vmi_ext_conversion_reorder_point | 0 | no safety, defined |
| 1 | absent: no price line (value None) | vmi_ext_conversion_reorder_point | 10 | value share 1 |
| 1 | base | vmi_ext_hold_converted_fill | 8 | 8 |
| 1 | price: future-dated repricing line | vmi_ext_hold_converted_fill | 0 | 0 (out of scope) |
| 1 | price: two lines on the latest effective date | vmi_ext_hold_converted_fill | 0 | 0 (out of scope) |
| 1 | price: substitute line inside protection days | vmi_ext_hold_converted_fill | 9 | prior price 130.00 -> 9 |
| 1 | decoy: non-critical line at the visit | vmi_ext_hold_converted_fill | 8 | 8 |
| 1 | decoy: critical line at yesterday's visit | vmi_ext_hold_converted_fill | 8 | 8 |
| 1 | decoy: second visit today (emergency) | vmi_ext_hold_converted_fill | 0 | 0 (tie) |
| 1 | account active | vmi_ext_hold_converted_fill | 0 | 0 (outside: base fill) |
| 1 | bin not critical | vmi_ext_hold_converted_fill | 0 | 0 |
| 1 | date edge: withdrawal 30 days ago | vmi_ext_hold_converted_fill | 5 | quarter release |
| 1 | date edge: payment dated 2026-09-08 (age 1) | vmi_ext_hold_converted_fill | 3 | payments 3,705 -> 0.5 percent |
| 1 | decoy: payment of another month (2026-08-30) | vmi_ext_hold_converted_fill | 8 | 8 |

## Probe table — round 3 (after F6/F9/F10 fixes; same probes, refreshed results)
| task | probe | policy | result | expected reading |
|---|---|---|---|---|
| 0 | base | vmi_ext_vended_item_fill_level | 26 | 26 |
| 0 | decoy: later Corbett slow-mover removal of another item | vmi_ext_vended_item_fill_level | 26 | 26 (customer removals only) |
| 0 | decoy: second customer removal same date | vmi_ext_vended_item_fill_level | 0 | 0 (tie sentence) |
| 0 | absent: no customer removal | vmi_ext_vended_item_fill_level | 0 | 0 |
| 0 | decoy: locker vend of 9 units | vmi_ext_vended_item_fill_level | 26 | 26 (other machine) |
| 0 | decoy: returned payment dated 2025-10-15 (age 12) | vmi_ext_vended_item_fill_level | 26 | 26 (outside twelve months) |
| 0 | date edge: returned payment dated 2025-10-16 (age 11) | vmi_ext_vended_item_fill_level | 19 | 2 returned -> share 0.6 |
| 0 | None: no vend at demand machine (price None) | vmi_ext_vended_item_fill_level | 0 | defined (value 0) |
| 0 | zero: scheduled visits none in latest month | vmi_ext_vended_item_fill_level | 36 | standard 2-week cover |
| 0 | base | vmi_ext_consigned_reorder_point | 19 | 19 |
| 0 | decoy: older consigned new bin (June) | vmi_ext_consigned_reorder_point | 19 | 19 |
| 0 | decoy: second consigned new bin today | vmi_ext_consigned_reorder_point | 0 | 0 (tie) |
| 0 | decoy: second customer removal of 43318 same date at the locker | vmi_ext_consigned_reorder_point | 0 | 0 (tie) |
| 0 | zero-month: a month without net vends | vmi_ext_consigned_reorder_point | 12 | standard rate |
| 0 | special: locker selection flagged special | vmi_ext_consigned_reorder_point | 23 | supply 4 days |
| 0 | absent: no vend ever (XMAX 0) | vmi_ext_consigned_reorder_point | 0 | defined, buffer none |
| 0 | decoy: backorder opened in June filled in September | vmi_ext_consigned_reorder_point | 19 | some opened, more filled -> 1 day |
| 0 | base | vmi_ext_opening_consignment | 13 | 13 |
| 0 | absent: no par entry | vmi_ext_opening_consignment | 8 | reorder 0 |
| 0 | decoy: second par entry with lower reorder point | vmi_ext_opening_consignment | 13 | 13 (highest reorder point) |
| 0 | zero: credit limit 0 | vmi_ext_opening_consignment | 11 | tight share 0.7 |
| 0 | date edge: ship-to opened 2026-04-15 (age 6) | vmi_ext_opening_consignment | 13 | 0.9 |
| 0 | date edge: ship-to opened 2026-04-16 (age 5) | vmi_ext_opening_consignment | 10 | 0.7 |
| 0 | zero: no vends in three months (return rate) | vmi_ext_opening_consignment | 15 | share 1 |
| 1 | base | vmi_ext_converted_critical_fill | 19 | 19 |
| 1 | decoy: older withdrawal of another item | vmi_ext_converted_critical_fill | 19 | 19 |
| 1 | decoy: second withdrawal same date | vmi_ext_converted_critical_fill | 0 | 0 (tie) |
| 1 | absent: no withdrawal | vmi_ext_converted_critical_fill | 0 | 0 |
| 1 | absent: item never consumed | vmi_ext_converted_critical_fill | 0 | draw zero -> 0 |
| 1 | zero: credit limit 0 | vmi_ext_converted_critical_fill | 19 | share 0.75 |
| 1 | date edge: consumption dated 2025-10-08 (age 12) | vmi_ext_converted_critical_fill | 19 | excluded |
| 1 | base | vmi_ext_conversion_reorder_point | 8 | 8 |
| 1 | account active (critical no longer matters) | vmi_ext_conversion_reorder_point | 7 | 7 |
| 1 | decoy: older critical entry of the bin (2024) | vmi_ext_conversion_reorder_point | 7 | hold lead 0 (latest-date entries only) |
| 1 | absent: nothing billed in twelve months (zero division) | vmi_ext_conversion_reorder_point | 0 | no safety, defined |
| 1 | absent: no price line (value None) | vmi_ext_conversion_reorder_point | 10 | value share 1 |
| 1 | base | vmi_ext_hold_converted_fill | 8 | 8 |
| 1 | price: future-dated repricing line | vmi_ext_hold_converted_fill | 0 | 0 (out of scope) |
| 1 | price: two lines on the latest effective date | vmi_ext_hold_converted_fill | 0 | 0 (out of scope) |
| 1 | price: substitute line inside protection days | vmi_ext_hold_converted_fill | 9 | prior price 130.00 -> 9 |
| 1 | decoy: non-critical line at the visit | vmi_ext_hold_converted_fill | 8 | 8 |
| 1 | decoy: critical line at yesterday's visit | vmi_ext_hold_converted_fill | 8 | 8 |
| 1 | decoy: second visit today (emergency) | vmi_ext_hold_converted_fill | 0 | 0 (tie) |
| 1 | account active | vmi_ext_hold_converted_fill | 0 | 0 (outside: base fill) |
| 1 | bin not critical | vmi_ext_hold_converted_fill | 0 | 0 |
| 1 | date edge: withdrawal 30 days ago | vmi_ext_hold_converted_fill | 5 | quarter release |
| 1 | date edge: payment dated 2026-09-08 (age 1) | vmi_ext_hold_converted_fill | 3 | payments 3,705 -> 0.5 percent |
| 1 | decoy: payment of another month (2026-08-30) | vmi_ext_hold_converted_fill | 8 | 8 |

Round 3 additional absent-record probes (probe_r3.py) for the newly guarded reads:

| task | probe | policy | result | expected reading |
|---|---|---|---|---|
| 0 | absent: ship-to opening date | opening | 10 | counts as opened today -> 0.7 -> 10 |
| 0 | absent: no credit account | opening | 11 | counts as 0.9 or more -> 0.7 |
| 0 | absent: ship-to service level not on record | fill level | 21 | adds none -> 21 |
| 0 | absent: ship-to service level not on record | reorder point | 18 | adds none -> 18 |
| 1 | absent: no pricing agreement | hold fill | 0 | 0 (out of scope) |
| 1 | absent: no credit account | hold fill | 0 | 0 (not on hold -> outside) |
| 1 | absent: no credit account | critical fill | 19 | share 0.75 -> 19 |

Pairwise method-tier table (unchanged by round 3; distinguishing inputs from each world):
| policy | method tiers | values on the world |
|---|---|---|
| fill level (task 0) | projection / recency-weighted / average | 13.96 / 10.04 / 9.38 a week (months 52/35/35) |
| reorder point (task 0) | peak / peak-and-mean blend / average | 1.733 / 1.544 / 1.341 a day |
| opening stock (task 0) | reorder point / midpoint / fill-to | 19 / 22.5 / 26 |
| critical fill (task 1) | peak / blend / average | 12.00 / 8.31 / 4.62 a week |
| conversion reorder (task 1) | spread-based / proportional / none | 2.80 / 1.56 / 0 units |
| hold fill (task 1) | substitute prior price / contract / list less discount | prior price / 142.50 / 152.15 |

## Probe table — round 4 (newly stated branches: no customer removal, same-date price ties, opening stock at the cap, tier and status scope)

| task | probe | policy | result | expected reading |
|---|---|---|---|---|
| 0 | no customer-requested removal (Corbett slow-mover removal only) | reorder point | 0 | 0 (or there is none) |
| 0 | no customer-requested removal (Corbett slow-mover removal only) | opening stock | 0 | 0 (or there is none) |
| 0 | two price lines of 43318 on one date | opening stock | 0 | 0 (no single in-effect line) |
| 0 | future-dated price line of 43318 | opening stock | 0 | 0 (line not in effect) |
| 0 | opening stock at the cap: room for exactly 13 units | opening stock | 13 | 13 (fits) |
| 0 | opening stock at the cap: room for 9 units | opening stock | 9 | 9 (cut to the cap) |
| 0 | opening stock at the cap: no room | opening stock | 0 | 0 |
| 0 | program on a tier without consignment | fill level | 0 | 0 (other tier) |
| 0 | two vend prices on the latest vend date (29.95 decoy) | fill level | 22 | highest price of that date: value class A -> lower fill |
| 1 | two price lines of 41827 on one date | conversion reorder | 10 | value counts zero -> share 1 -> 10 |
| 1 | program paused | hold fill | 0 | 0 (status not active or terminating) |
| 1 | no service visit at all | hold fill | 0 | 0 (no visit) |

Round-3 probe table re-run after round 4 (all results unchanged):
48

## Probe table — round 5 (restrictions newly enforced: visit of the day, par-review conversion, first fill, prerequisite states)

| task | probe | policy | result | expected reading |
|---|---|---|---|---|
| 0 | no service visit dated today | opening stock | 0 | 0 |
| 0 | two service visits dated today | opening stock | 0 | 0 |
| 0 | no reorder point above zero (prerequisite state) | opening stock | 0 | 0 (not placed) |
| 1 | withdrawal after the customer removed the bin | critical fill | 0 | 0 (not a conversion) |
| 1 | withdrawal after the customer removed the bin | conversion reorder | 0 | 0 |
| 1 | withdrawal after the customer removed the bin | hold fill | 0 | 0 |
| 1 | program closed (program-end withdrawal) | converted_critical_fill | 0 | 0 |
| 1 | program closed (program-end withdrawal) | conversion_reorder_point | 0 | 0 |
| 1 | an earlier customer-owned fill of 41827 on the program | hold fill | 0 | 0 (not the first fill) |
| 1 | no customer-owned conversion entry (prerequisite state) | hold fill | 0 | 0 (not booked) |

The round-3/4 table re-runs identically except "absent: no par entry" on the opening stock, now 0 (was 8): the state "reorder point above zero" is enforced (O14).

## Probe table — round 6 (customer-request state encoded for edges E4 and E5)

| task | probe | policy | result | expected reading |
|---|---|---|---|---|
| 1 | no customer request (skip the request) | conversion reorder | 0 | 0 (not recorded) |
| 1 | customer request dated before the latest bin entry date (older request) | conversion reorder | 0 | 0 (request not on the latest date) |
| 1 | customer request on the latest date | conversion reorder | 8 | 8 |
| 1 | bin already critical, conversion entry only, no customer request | hold fill | 0 | 0 (not booked) |
| 1 | request and conversion entry on the latest date | hold fill | 8 | 8 |

The earlier table re-runs identically except "decoy: older critical entry of the bin (2024)" on the conversion reorder point, now 0 (was 7): with the request moved to 2024 no customer request stands on the latest date, so no conversion entry is recorded (E4).

## Probe table — round 7 (customer request recognised by "par level entry naming no reorder point", consigned or not)

| task | probe | policy | result | expected reading |
|---|---|---|---|---|
| 1 | revised customer request dated after the conversion (customer-owned, no reorder point) | hold fill | 5 | booked (request and not-consigned entry on the latest date; release a quarter) |
| 1 | request and conversion the day before, nothing dated today | hold fill | 5 | booked on the latest date 2026-10-07 entries |
| 1 | Corbett par entry (reorder point 12) dated after the conversion, no new request | hold fill | 0 | 0 (no request on the latest date) |

Round-6 probes and the full earlier table re-run with identical results.

## Round 8 probes (seed-only re-judge: S2-S5, N1-N4)

The full round-2..7 probe table (probe_all) re-runs with identical results on the round-8 seed. New rows probe the added other-product history; none reaches a factor:

| task | probe | policy | result | expected reading |
|---|---|---|---|---|
| 0 | seed r8: Indianapolis next-day-air booking of 43318 on 2026-10-09 | vmi_ext_consigned_reorder_point | 19 | 19 (other ship-to) |
| 0 | seed r8: Indianapolis open backorder of 43318 opened 2026-10-01 | vmi_ext_opening_consignment | 13 | 13 (other ship-to) |
| 0 | seed r8: usage bills and fees removed | vmi_ext_vended_item_fill_level | 26 | 26 (bills and fees are not vends or restocks) |
| 0 | seed r8: usage bills and fees removed | vmi_ext_consigned_reorder_point | 19 | 19 |
| 0 | seed r8: rebate accrual and 2025-09 finance charge removed | vmi_ext_vended_item_fill_level | 26 | 26 (charges are not returned payments) |
| 0 | seed r8: rebate accrual and 2025-09 finance charge removed | vmi_ext_opening_consignment | 13 | 13 |
| 0 | band edge: receivable +12,369.60 (ratio 0.9) | vmi_ext_opening_consignment | 11 | moves (credit room tier edge, 12,369.60 away) |
| 0 | band: receivable 135,000.00 (ratio 0.75) | vmi_ext_opening_consignment | 13 | 13 (0.75 to below 0.9) |
| 1 | seed r8: plant order lines removed | vmi_ext_converted_critical_fill | 19 | 19 (no factor reads them) |
| 1 | seed r8: plant order lines removed | vmi_ext_conversion_reorder_point | 8 | 8 |
| 1 | seed r8: 41827 next-day-air shipments removed | vmi_ext_converted_critical_fill | 19 | 19 (rush cover reads bookings) |
| 1 | seed r8: 41827 next-day-air shipments removed | vmi_ext_hold_converted_fill | 8 | 8 |
| 1 | seed r8: commitment back to 1,500,000.00 | vmi_ext_hold_converted_fill | 8 | 8 (no factor reads it) |

The band-edge row shows task 0's receivable margin: the opening stock moves only when the receivable rises by 12,369.60 (ratio 0.9); the round-8 history keeps it at 149,630.40 exactly.

## Round 9 probes (S6: no next-day-air shipment in either world)

probe_all (rounds 2-7) and the round-8 seed probes re-run with identical results on the round-9 seed. New rows:

| task | probe | policy | result | expected reading |
|---|---|---|---|---|
| 0 | r9: next-day-air backorders and fills removed (BO-418377 alone) | vmi_ext_consigned_reorder_point | 19 | 19 (opened and as many filled) |
| 0 | r9: next-day-air backorders and fills removed (BO-418377 alone) | vmi_ext_opening_consignment | 13 | 13 |
| 0 | r9: fill of BO-419721 (2026-10-08) removed | vmi_ext_consigned_reorder_point | 23 | moves (open backorder) |
| 0 | r9: fill of BO-419721 (2026-10-08) removed | vmi_ext_opening_consignment | 9 | moves (open backorder share) |
| 1 | r9: BO-437426 and its fill removed | vmi_ext_converted_critical_fill | 19 | 19 (BO-440918 keeps the backorder tier) |
| 1 | r9: BO-437426 and its fill removed | vmi_ext_conversion_reorder_point | 8 | 8 (outside three months) |
| 1 | r9: BO-437426 left open (fill removed) | vmi_ext_conversion_reorder_point | 8 | 8 (outside three months) |

The three task-0 next-day-air bookings are now wholly backordered and filled by route truck inside the call day; with all three filled the backorder tiers read as before (opened and as many filled), and an unfilled one would move them, which the 2026-10-08 fill rules out.
