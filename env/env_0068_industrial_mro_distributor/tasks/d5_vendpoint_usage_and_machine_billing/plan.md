# d5_vendpoint_usage_and_machine_billing — instantiate plan (M=2)

Category: `vending` (VendPoint Industrial Vending Program). Blueprint frozen; base copied verbatim.

## Draws (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=1, factor_counts=[4, 6]
- task 1: prerequisite_problems=2, factor_counts=[6, 4, 6]

## DSL / world constraints found at Step 0 (drive the design)
- History primitives filter by equality only and window only by `within_months` from today (MONTHS convention);
  vend / return / error rows carry no billing month, so no calendar-month vend sum is computable. Monthly
  quantities are therefore read from rows that carry `billing_period` (usage bills, fees, shrink) and the month
  string comes from a record (latest usage bill), never from NOW.
- SUM/COUNT/LATEST are scoped to the target machine; sibling machines are unreadable -> site pooling cannot be
  computed; the shortfall policy is scoped (self-naming overwrite) to a machine tested on its own.
- String concat and lexicographic MX/MN on 'YYYY-MM-DD' work (month first day = M + '-01').
- Weekdays between two dates: F(d) = (DAYS('1970-01-05', d) // 7) * 5 + MN(DAYS('1970-01-05', d) % 7, 4) + 1
  (1970-01-05 is a Monday); weekdays in (a, b] = F(b) - F(a).
- Only `vending_removal_noticed` is a by:user transition; second user write = the customer's own chargeable
  emergency restock request (fee per request the customer places: base parameter meaning).
- vending_fee_charged has an unconditional trigger to credit:credit_invoice_posted (billing consequence, not
  executed by the engine). The blueprint names fees as d5's agent writes, so fee rows are written; recorded as a
  known risk in worklog.

## Problem trees
### Task 0 (n=1) — emergency restock on an emptied coil
- A `vending_ext_stockout_par_resize` (agent, 6 factors, state_due): Corbett re-sizes the par of a selection that
  ran empty between scheduled visits. Tool: resize_selection_par_* (vending_selection_set, change_source corbett).
- B `vending_ext_emergency_restock_fee` (user, 4 factors, on_request, ROOT): the customer's emergency restock
  request booked with its fee. Tool: place_emergency_restock_request_* (vending_fee_charged emergency_restock_fee).
- Edge B <- A value_input (undersizing relief reads the Corbett par change dated the request day).

### Task 1 (n=2) — removal notice on a Carousel 90
- C `vending_ext_month_shortfall_fee` (agent, 6, state_due): shortfall fee for the latest billed month.
- D `vending_ext_install_fee` (agent, 4, state_due): installation fee owed and never billed.
- E `vending_ext_early_removal_notice` (user, 6, on_request, ROOT): the customer's written removal notice, which
  fixes and books the early removal fee.
- Edges E <- C value_input (minimum-usage record tier), E <- D value_input (installation concession recovery).

## Factor sketch (to be finalised in the extended yaml; independence: no factor reads another's binding)
A par: PF1 usage basis (method: since-added anchor / lumpy peak / 13-week average), PF2 safety allowance by item
category, PF3 storeroom backup (vmi bins at the ship-to, cross), PF4 consigned-exposure limit (credit status /
returned payments, cross), PF5 replenishment-lead allowance (special item / substitute contract line, cross
pricing), PF6 repeat-stockout allowance (emergency fee lines 3 months).
B emergency fee: EF1 undersizing relief (Corbett par change today + item category), EF2 visit-schedule method
(zero / prorated / flat by days since last scheduled restock), EF3 StockSmart technician on site (cross vmi),
EF4 repeat-request surcharge (emergency fee lines 3 months).
C shortfall: SF1 plant-shutdown proration (method, vmi pause), SF2 graduated minimum (tested months since
install), SF3 stockout relief (emergency fees billed for the month), SF4 shortfall rate by 12-month invoiced
merchandise (cross credit), SF5 cap by contract tier (cross pricing), SF6 StockSmart consumption credit (cross vmi).
D install fee: IF1 contract concession (cross pricing), IF2 route-crew credit (cross order), IF3 late-install
method (weekday lateness), IF4 StockSmart onsite crew credit (cross vmi).
E early removal: RF1 fee basis method by contract tier (flat / linear / stepped by contract year), RF2
minimum-usage record (shortfall lines 12 months), RF3 concession recovery (install fee not billed, by months run),
RF4 StockSmart conversion credit (cross vmi), RF5 site status (cross order), RF6 machine-fault credit (vend error
credits 6 months).

## Method tier pairwise tables (distinguishing input)  — filled per policy in worklog
## Probe table (CFIELD / first-match / LATEST decoys, absent records, None / zero-division / date edges)
(filled per policy as the compute is written; see sections below)

### Probe tables (done)
Task 0 (par review, emergency fee) and task 1 (shortfall, installation, early removal) probe tables — every CFIELD /
first-match / LATEST read with its decoy, every absent-record case with its rule tier, and the None / zero-division /
date-difference edges — are recorded with their run results in worklog.md (sections "Task 0" and "Task 1"); runs:
/tmp scratch verify.py, v_t0.py, v_t1.py, probe_t1.py (scratch only, nothing under the write domain).

## Round 3 redesign (coordinator ruling: no task tool may write vending_fee_charged or vending_usage_billed)
Allowed numeric writes: vending_item_returned, vending_vend_error_credited, vending_selection_set (all triggers []).
Every problem is one of these, each policy its own action kind:
- Task 0 (n=1, [4,6]): root `vending_ext_startup_item_return` (customer returns unused units of the start-up item,
  user, 4 factors) <- `vending_ext_startup_par_review` (Corbett start-up review, agent, 6, kept from r1/r2);
  value link: the review raises the selection's par, which moves the return's fill-level tier.
- Task 1 (n=2, [6,4,6]): root `vending_ext_substitute_par_setting` (customer sets the par of a Corbett-placed
  substitute, user, 6) <- `vending_ext_substitute_placement` (Corbett places the approved substitute in the retired
  item's selection, agent, 6) <- `vending_ext_retired_item_vend_credit` (Corbett credits vends logged after the
  retired item ran out, agent, 4); value links: the credit corrects the retired item's units the placement sizes on;
  the placement's starting par is the starter par the customer's sizing settles on.
Per-object computations are identified from records only (newest add entry; highest removal / substitute contract
line reference), since the DSL cannot read the customer's choices.

### Round 3 problem trees (as built)
- Task 0 (2026-10-05 10:40 EDT, Tamarack, Carousel 90 VP-551273): root `vending_ext_startup_item_return` (user, 4 factors: fill_level_shape method, trial_length_share, machine_return_rate, item_handling_share) <- `vending_ext_startup_par_review` (agent, 6 factors, unchanged rule). Gold: par 28, unit credit 5.74 (skip review: 5.35).
- Task 1 (2026-10-07 14:20 EDT, Westbrook, Carousel 90 VP-562218): root `vending_ext_substitute_par_setting` (user, 6) <- `vending_ext_substitute_placement` (agent, 6) <- `vending_ext_retired_item_vend_credit` (agent, 4). Gold: credit 4 units / 50.76, placement par 55, settling par 46 (skips: 108; 56 and 47).
- Dropped (no task triggers them, no tool writes them): emergency restock fee, month shortfall fee, installation fee, early removal notice policies and their four tools.

### Round 3 method-tier pairwise table (distinguishing input)
| policy / factor | tier A | tier B | tier C | distinguishing input -> A / B / C |
| --- | --- | --- | --- | --- |
| start-up return / fill_level_shape | MX(0, p - 0.75) | 0.95 p | p | p = 6.55 -> 5.80 / 6.2225 / 6.55 (A = B only at p = 15.00) |
| retired credit / dispense_unit_basis | ceil(s / l) x l | MX(0, s - loaded x tol / 100) | s | s = 3, l = 2, loaded 324, tol 1.5 -> 4 / 0 / 3 |
| placement / substitute_demand_basis | avg / t | MX(par, largest / t) | par | units 259 -> 49.81 vs par 60; no window units, largest 20 -> MX(60, 100) = 100 vs 60 |
| settling par / settling_demand_basis | MX(avg, starter x t) | MX(avg, largest) | avg | avg 9.96, starter 55, largest 12 -> 11 / 12 / 9.96 |
| start-up review / demand_pattern_basis (unchanged) | MX(avg, largest) | MX(avg, starter x (1 - t)) | avg | avg 3.94, largest 6, starter 24 -> 6 / 19.2 / 3.94 |
Every parameter-labelled factor of the five policies selects a number (K() constant or 1 / 0) in every tier; no parameter tier computes a formula (F2-C1 class swept).

### Round 3 probe table (scratch copies of the task worlds; script probe_r3.py)
| policy | probe | result |
| --- | --- | --- |
| R | gold | 5.74 |
| R | decoy: AB-50926 removal line re-dated after the repricing (other sku) | 5.74 |
| R | absent: no contract line for AB-53318 -> latest vend price 6.85 | 6.0 |
| R | None/empty: no return line on the machine -> share 1 | 5.85 |
| R | zero-division: none (no division in the compute); ledger 0 with par 0 | 5.35 |
| R | date: today 2026-09-25 -> 30 days since add -> mid share | 5.74 |
| R | date: today 2026-09-24 -> 29 days -> share 1 | 5.92 |
| R | date: return 2026-07-05 counts? (move VR to 2026-07-05: 3 whole months -> out) | 5.85 |
| P1 | gold (opening world) | 28 |
| FV | gold | 50.76 |
| FV | decoy: older removal line of CT-56104 (earlier effective date) | 0.0 |
| FV | absent: no removal line | 0.0 |
| FV | None: retired item never vended (vends dropped) | 0.0 |
| FV | zero-division: latest vend quantity 0 | 0.0 |
| FV | date: today 2026-10-08 -> 7 days -> long share | 52.64 |
| FV | date: today 2026-10-01 -> 0 days -> no share | 48.88 |
| FV | after own credit (ledger +1) -> nothing owed | 0.0 |
| SUB | gold (after credit) | 55 |
| SUB | decoy: SF-55247 shipped to ST-52614 only (drop ST-52611 line) -> channel 1 | 61 |
| SUB | absent: no added line for the retired item -> list step 1 | 46 |
| SUB | zero-division: retired list price 0 -> list step 1 | 46 |
| SUB | None: retired item never vended (largest vend 0) -> carry tier | 56 |
| SUB | date: retired vends only before the window (today 2027-01-15) -> largest-vend tier | 74 |
| SUB | date: today 2026-12-23 -> order line of 2026-09-22 out of 3 months | 2 |
| SP | gold | 46 |
| SP | decoy: Romulus shipment only -> channel 1 | 51 |
| SP | absent: no contract line for SF-55247 -> value share 1 | 51 |
| SP | None: no substitute vends (MAX empty -> 0) | 46 |
| SP | date: today 2026-11-04 -> 28 days -> lumpy/avg tier | 29 |
| SP | date: today 2026-11-03 -> 27 days -> settling tier | 46 |

## Round 4 updates (audit revision_3: F3-C1..C4, T0-F1, T1-F6, T1-F7, O16-O18)
- Task 0 gold: par 28; start-up unit credit 6.00 from the price paid on the item's latest vend VT-5515953 (line credit 12.00). Skipping the review gives 5.62.
- Task 1 gold: vend error credit 1 unit / 10.43 against the failed vend VT-5626378. Then placement par 55 and settling par 46. Skipping the credit gives 56 / 47; skipping the placement gives 120.

### Round 4 method-tier pairwise table (distinguishing input)
| policy / factor | tier A | tier B | tier C | distinguishing input -> A / B / C |
| --- | --- | --- | --- | --- |
| start-up return / fill_level_shape | MX(0, p - 0.75) | 0.95 p | p | p = 6.85 -> 6.10 / 6.5075 / 6.85 |
| retired credit / dispense_unit_basis | shortfall | MX(0, shortfall - tolerance units) | units of the latest vend | shortfall 1, vend 2, loaded 323, tol 1.5 -> 1 / 0 / 2 |
| placement / substitute_demand_basis | avg / t | larger of par and (largest / t) | par | units 259 -> 49.81 vs 60; no window units, largest 20 -> 100 vs 60 |
| settling par / settling_demand_basis | larger of avg and (starter x t) | larger of avg and largest | avg | avg 9.96, starter 55, largest 12 -> 11 / 12 / 9.96 |
| start-up review / demand_pattern_basis | larger of avg and largest | larger of avg and (starter x (1 - t)) | avg | avg 3.94, largest 6, starter 24 -> 6 / 19.2 / 3.94 |

### Round 4 probe table (scratch copies; probe_r3.py)
| policy | probe | result |
| --- | --- | --- |
| R | gold | 6.0 |
| R | decoy: today's contract price 6.55 (PCH-552790) dropped -> unchanged, credit uses price paid | 6.0 |
| R | tie: same vended_at as the latest vend, lower vend number (decoy price 7.10 on VT-5515942 re-timed) -> highest vend number wins, 6.00 | 6.0 |
| R | absent: no vend of the item at all -> price None (scope not met) | 0.0 |
| R | None/empty: no return line on the machine -> share 1 | 6.12 |
| R | zero-division: none (no division in the compute); ledger 0 with par 0 | 5.62 |
| R | date: today 2026-09-25 -> 30 days since add -> mid share | 6.0 |
| R | date: today 2026-09-24 -> 29 days -> share 1 | 6.19 |
| R | date: return 2026-07-05 counts? (move VR to 2026-07-05: 3 whole months -> out) | 6.12 |
| P1 | gold (opening world) | 28 |
| FV | gold | 10.43 |
| FV | decoy: older removal line of CT-56104 (lower change reference PCH-556001) | 10.43 |
| FV | absent: no removal line | 0.0 |
| FV | None: retired item never vended (vends dropped) | 0.0 |
| FV | zero-division: latest vend quantity 0 -> out of scope | 0.0 |
| FV | scope: shortfall 3 > latest vend 2 (earlier vend +2 units) -> base rules, 0.0 | 0.0 |
| FV | max shares (no program 0.1, PPE 0.25, long delay 0.1) -> 0.95, credit below billed 11.59 | 11.01 |
| FV | date: today 2026-10-06 -> 7 days -> long share | 10.43 |
| FV | date: today 2026-10-05 -> 6 days -> short share | 9.85 |
| FV | date: today 2026-09-29 -> 0 days -> no share | 9.27 |
| FV | after own credit (ledger 0) -> nothing owed | 0.0 |
| SUB | gold (after credit) | 55 |
| SUB | decoy: SF-55247 shipped to ST-52614 only (drop ST-52611 line) -> channel 1 | 61 |
| SUB | absent: no added line for the retired item -> list step 1 | 46 |
| SUB | zero-division: retired list price 0 -> list step 1 | 46 |
| SUB | None: retired item never vended (largest vend 0) -> carry tier | 56 |
| SUB | date: retired vends only before the window (today 2027-01-15) -> largest-vend tier | 74 |
| SUB | date: today 2026-12-23 -> order line of 2026-09-22 out of 3 months | 2 |
| SP | gold | 46 |
| SP | decoy: Romulus shipment only -> channel 1 | 51 |
| SP | absent: no contract line for SF-55247 -> value share 1 | 51 |
| SP | None: no substitute vends (MAX empty -> 0) | 46 |
| SP | date: today 2026-11-04 -> 28 days -> lumpy/avg tier | 29 |
| SP | date: today 2026-11-03 -> 27 days -> settling tier | 46 |

### Round 6 probe additions (KB audit SRC-1)
| policy | probe | result |
| --- | --- | --- |
| SUB | zero: substitute list price 0 (protected line with no list price) -> list step 1 | 46 |
| SUB | zero-division: retired list price 0 -> list step 1 | 46 |
