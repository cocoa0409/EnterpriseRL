# plan.md — service_repair_orders (env_0075), M=2, identifier band 2

Draw (draw_counts.py --tasks 2):
- task 0: prerequisite_problems=3, factor_counts=[4,6,5,6]
- task 1: prerequisite_problems=3, factor_counts=[5,4,6,6]

XF_recipe.md read in full; every section (A–G) is designed against below.

## Trees
T0 (retail, Kessler Owner Rewards Gold, individual "Diane Hartsfield"; frozen 2026-10-31 14:10:00 EDT = month-end run day)
  root d service_ext_owner_points_redemption (USER redeem_owner_points_3e3ce956), 6 factors
   <- j service_ext_paid_ro_points (credit_paid_ro_points_b77dd6a9), 6 factors   [value_input: points_on_file]
        <- h service_ext_estimate_overage_credit (credit_estimate_overage_3db3cf5c), 5 factors [value_input: paid_credits]
   <- e service_ext_month_end_points_expiry (expire_owner_points_a6cb3dc9), 4 factors [value_input: points_on_file]
  multiset {6,6,5,4} = draw [4,6,5,6]. Topological order h, j, e, d (e commutes with h/j: e reads no row h or j writes that ages; j's points are dated today, unaged).
T1 (fleet, Commercial Fleet Account - Net 30): root a service_ext_diagnostic_credit <- b repeat-repair estimate (USER); a <- g early-payment discount <- c comeback credit. Values (round 4): c 645.54, g 3.89, b 2847.19, a 76.36.

## Events written by T0 tools and their base triggers (XF 18/19)
| tool | event(s) written | base triggers | landing |
|---|---|---|---|
| credit_estimate_overage_3db3cf5c | service_line_credited (estimate_overage) | [] | service only |
| credit_paid_ro_points_b77dd6a9 | service_points_earned | [] | service only |
| expire_owner_points_a6cb3dc9 | service_points_expired | [] | service only |
| redeem_owner_points_3e3ce956 | service_points_redeemed + its triggered service_line_credited (rewards_redemption, same amount, same RO) | service_points_redeemed -> service:service_line_credited | service only, booked in the same call as base says |
Every money row written is > 0.00; points rows >= 1 point.

## Factor tables (T1 = moves result on the task world alone; T2 = a producible world exists where it alone moves result with all others at baseline)
### d redemption credit (computes credit_amount, USD)
| factor | effect | ladder (tiers) | T0 tier | T1 (result if baseline) | T2 world |
|---|---|---|---|---|---|
| tenure_point_value | parameter | Gold/Plat & >=60 mo: .0125 / Silver & >=60 mo: .011 / else points_value_usd | Gold 91 mo | 441.56 -> 358.25 | any long Gold account, all else base |
| owner_vehicle_bonus (purchase, maintenance) | parameter | closed deal & active plan: .16 / closed deal, no plan: .10 / else 0 | V1 deal closed + Kessler Care Plus active | -> 386.48 | bought vehicle, short-tenure Silver |
| shield_holder_bonus (vsc) | parameter | active Shield & Gold/Plat: .05 / active Shield & Silver: .03 / else 0 | V1 Exclusionary active | -> 424.34 | any Shield holder |
| held_points_rule | method | returned pmt <=12 mo & below Plat: balance-1000 (floor 0) / no returned pmt & opened <12 mo: balance - enrollment bonus points (floor 0) / else balance | returned check 2026-03-24 | -> 456.68 | Silver w/ returned pmt |
| home_store_redemption_credit | parameter | home store & Gold/Plat: $10 / home store & Silver: $5 / else 0 | R0 at KHB = home | -> 431.56 | any |
| frequent_visit_redemption_credit | parameter | >=4 payments in 12 mo & Gold/Plat: $15 / & Silver: $8 / else 0 | 5 payments | -> 426.56 | any |
All-pairs (method held_points_rule): (i) vs (ii): balance with 0 bonus points & returned pmt -> (i) subtracts 1000, (ii) subtracts 0; (i) vs (iii): any balance>0; (ii) vs (iii): account with enrollment bonus points. Shapes: constant hold / aggregate subtraction / identity. Cap (points_max_redemption_pct_of_ro x R0 labor+parts = 480.54) does not bind on T0 (441.56) — it binds only when e is skipped (480.54), which still moves the value.
### j points for the paid RO (computes points)
| factor | effect | ladder | T0 tier | T1 |
|---|---|---|---|---|
| owner_earning_rate (purchase) | parameter | deal financed dealer-arranged & Gold/Plat: +2 / deal cash or outside lender & Gold/Plat: +1 / else points_earn_per_usd | V2 outside lender -> 3 | 4666 -> 3682 |
| earning_dollars_rule | method | redemption credit on RO & paid <=30 d after close: total - redemption / paid >30 d: labor only / else total | 1,200-pt redemption, paid next day | -> 4711 |
| shield_labor_bonus (vsc) | parameter | Shield & Gold/Plat: +2/labor$ / Shield & Silver: +1 / else 0 | V2 Select active | -> 3351 |
| tenure_multiplier_rule | parameter | >=60 mo & Gold/Plat: 1.25 / >=60 mo & Silver: 1.1 / else 1 | 91 mo | -> 3813 |
| visit_frequency_bonus | parameter | >=3 payments 12 mo & Gold/Plat: 250 / & Silver: 100 / else 0 | 5 payments | -> 4416 |
| care_member_bonus (maintenance) | parameter | active plan & Gold/Plat: 150 / & Silver: 75 / else 0 | Kessler Care Plus on V1 | -> 4516 |
All-pairs earning_dollars_rule: (i) total - redemption vs (ii) labor only (differ whenever parts>0 or redemption != parts) ; (i) vs (iii) differ by the redemption credit; (ii) vs (iii) differ by parts net of credits. Baseline (all factors) 1598.
### h overage credit (computes credit_amount)
| factor | effect | ladder | T0 tier | T1 |
|---|---|---|---|---|
| tenure_tolerance | parameter | Gold/Plat & >=24 mo: .05 / Gold/Plat & <24 mo: .075 / else estimate_overage_tolerance_pct | .05 | 118.56 -> 76.22 |
| supplemental_decisions | method | >=2 authorized decisions, latest on/before labor close: SUM / >=2, latest after close: MAX / else LATEST | 2 decisions (10-14, 10-16), closed 10-20 | -> 800.16 |
| owner_overage_courtesy (purchase) | parameter | deal dealer-arranged & Gold/Plat: $25 / deal cash or outside lender & Gold/Plat: $15 / else 0 | V2 outside lender | -> 103.56 |
| late_completion_courtesy | parameter | closed >3 d after last decision & Gold/Plat: $20 / & other tier: $10 / else 0 | 4 days | -> 98.56 |
| supplies_refund | parameter | supplies fee on RO & Gold/Plat: shop_supplies_pct / & other tier: .5 x shop_supplies_pct / else 0 | 6 % | -> 113.83 |
All-pairs supplemental_decisions: SUM vs MAX differ when >=2 decisions both > 0; SUM vs LATEST differ when an earlier decision exists; MAX vs LATEST differ when the latest is not the largest (T0: latest 186.54 < 612.40). Baseline (all) 712.53.
### e month-end expiry (computes points)
| factor | effect | ladder | T0 tier | T1 |
|---|---|---|---|---|
| care_plan_extension (maintenance) | parameter | active plan & Gold/Plat: +6 mo / & Silver: +3 / else 0 | +6 | 3278 -> 9658 |
| shield_contract_extension (vsc) | parameter | active Shield & Gold/Plat: +3 / & Silver: +2 / else 0 | +3 | -> 5620 |
| used_points_order | method | Gold/Plat & redemption <=6 mo: expired + redeemed - recent redeemed / below Gold & returned pmt <=12 mo: expired + redeemed + points of the returned-payment RO / else expired + redeemed | 1,200-pt redemption 10-21 | -> 2078 |
| long_member_reserve | parameter | >=60 mo & Gold/Plat: 500 / & Silver: 250 / else 0 | 500 | -> 3778 |
All-pairs used_points_order: (i) drops the recent-redemption sum; (ii) adds the returned-RO points sum; (iii) neither — each pair differs whenever its distinguishing sum is non-zero. Baseline (all) 13866.

## Probe table (T0 reads) — decoys / absent / ties / month-end
| read | decoy / absent / tie | rule tier |
|---|---|---|
| open RO = LATEST labor RO | RO P labor (10-20) older than R0 (10-29); same-day tie keeps first row (one labor row on R0) | "repair order of the latest labor charge" |
| paid RO = LATEST payment RO | RO P 10-21 vs returned-check RO (03-17/03-27); R0 unpaid | "latest payment received" |
| CFIELD purchase status=closed by vehicle | V1, V2 both closed; a vehicle with no deal -> None -> fall-through | "closed purchase deal" |
| CFIELD maintenance status=active (by vehicle in d; any in j/e) | only V1 plan; V2 none -> d tier keyed on V1 | "active Kessler Care plan" |
| CFIELD vsc status=active | S1 (V1) and S2 (V2) active; expired/cancelled filtered out | "active Kessler Shield" |
| CFIELD purchase financing_type | V2 outside_lender; V1 dealer_arranged; no deal -> None -> fall-through | three tiers |
| authorizations on RO P line A | two authorized decisions; declined decisions excluded by filter | supplemental_decisions |
| expiry whole months | MONTHS() day-of-month convention is the rule's own convention (whole months from the date earned) | e rule sentence |
| returned payment 12 mo | one returned check 2026-03-24 (within) | held_points_rule / used_points_order |

## Owed-at-once check (XF 16)
T0 world: every older RO paid and pointed, prior month-end runs posted through 2026-09, diag credits booked, no repeat repair inside a repair warranty, no fleet terms. Cross-category holdings are closed deals, active plan/contracts in term; nothing in another product is owed.

## T1 (fleet: Hollister Landscape & Snow LLC, Commercial Fleet Account - Net 30, home store Kessler Commercial Vehicle Center; frozen 2026-11-18 10:30:00 EST)
  root a service_ext_diagnostic_credit (credit_diagnostic_fee_eae01e67), 4 factors
   <- b service_ext_repeat_repair_estimate (USER authorize_repair_estimate_690e2aa2), 6 factors [value_input: authorized_estimate; wait carved to repeats whose store warranty has ended]
   <- g service_ext_early_payment_discount (credit_early_payment_discount_b0e7362c), 6 factors [value_input: spend_12m]
        <- c service_ext_comeback_labor_credit (credit_comeback_labor_f15915d4), 5 factors [value_input: invoice_credits]
  multiset {4,6,6,5} = draw [5,4,6,6]. Order c, g, b, a (b commutes with c/g: replayed b,c,g,a -> identical terminal tables).

### Events written by T1 tools
| tool | event | base triggers | landing |
|---|---|---|---|
| credit_comeback_labor_f15915d4 | service_line_credited (comeback_repair) | [] | service |
| credit_early_payment_discount_b0e7362c | service_line_credited (early_payment_discount) | [] | service |
| authorize_repair_estimate_690e2aa2 | intake row service_repair_authorizations (decision authorized) | n/a (intake) | service |
| credit_diagnostic_fee_eae01e67 | service_line_credited (diagnostic_applied_to_repair) | [] | service |

### c comeback credit (credit_amount) — result 645.54, all-baseline 832.66 (fleet branch; other accounts: repeat labor x comeback_labor_covered_pct; owed only inside the store warranty and on another RO; never below 0.01 when owed)
| factor | effect | ladder | T1 tier | T1 (result at baseline) | T2 world |
|---|---|---|---|---|---|
| aged_repair_share | parameter | >=9 whole months .70 / 6-8 .80 / else comeback_labor_covered_pct | 8 mo | -> 796.93 | any repeat 6-11 months after the original |
| original_store_basis | method | other store: original labor charge / same store & repeat labor larger: original + half the excess / else repeat labor | KFS vs KCV | -> 609.49 | stores differ, or same store with a larger repeat |
| wear_deduction_rule (maintenance) | parameter | >8,000 mi & no plan .15 / >8,000 mi & plan .05 / else 0 | 11,600 mi, plan | -> 677.41 | any repeat > 8,000 mi later |
| declined_work_share | parameter | declined >= 500 .85 / declined all < 500 .90 / else 1 | 214.60 | -> 712.82 | any original RO with a declined line |
| repeat_fee_refund | method | original RO carried supplies + hazardous fees: repeat's supplies + hazardous added / supplies only: repeat's supplies added / else nothing | both fees -> 39.95 | -> 605.59 | any comeback whose original job paid a supplies fee |
All-pairs original_store_basis: tier1 (original) vs tier3 (repeat) differ whenever the charges differ; tier2 (original + half the excess) lies strictly between them on its whole domain (repeat > original). repeat_fee_refund: tier1 vs tier2 differ by the repeat's hazardous fee; tier2 vs tier3 by the repeat's supplies fee. (r2's rate-swap tier 2 and downtime allowance removed: N-4, N-2.)

### g early-payment discount (credit_amount) — result 3.89, all-baseline 0 (never below 0.01 on an invoice paid in full inside its window; no labor charge on the paid RO -> no invoice)
| factor | effect | ladder | T1 tier | T1 |
|---|---|---|---|---|
| ach_window_rule | parameter | ACH & Net 30: 15 d / ACH & Net 15: 12 d / else early_pay_discount_days | ACH, 12 days | -> 0 |
| fleet_deal_rate (purchase) | parameter | FVPA & Net 30 .025 / FVPA & Net 15 .015 / else early_pay_discount_pct | F-250 FVPA | -> 3.33 |
| prompt_payer_addition | parameter | >=8 payments in twelve whole months & Net 30 +.005 / & Net 15 +.0025 / else 0 | 12 payments | -> 3.33 |
| account_tenure_addition | parameter | >=60 whole months & Net 30 +.005 / & Net 15 +.0025 / else 0 | 70 mo | -> 3.33 |
| discountable_base_rule (maintenance) | method | card: labor - credits / ACH or check & plan: labor + parts + shop supplies - credits / else labor + parts - credits | ACH + plan | -> 3.27 |
| payment_standing_share | parameter | late fee 12 mo & no returned pmt .5 / returned pmt 12 mo .25 / else 1 | late fee 2026-02-27 | -> 7.77 |

### b repeat-repair estimate (estimate_amount) — result 2847.19, all-baseline 3719.65 (prices nothing for a failure inside the earlier repair's store warranty)
| factor | effect | ladder | T1 tier | T1 |
|---|---|---|---|---|
| rate_lock_rule | parameter (selects which posted rate) | estimate RO away & earlier at home: earlier posted rate / both away: lesser of the two / else the diagnostic fee's rate | KCF vs KCV | -> 2870.23 |
| diagnosis_overlap_hours | method | diag >= 1.0 h & single labor charge: hours - diag / two+ labor charges: sum - diag / else latest hours | 9.8 - 1.0 | -> 2906.28 |
| repeat_labor_allowance | parameter | <=24 mo & <=24,000 mi .5 / <=36 mo otherwise .75 / else 1 | 19 mo, 17,200 mi | -> 3367.20 |
| maintained_vehicle_allowance (maintenance) | parameter | plan & >15,000 mi .88 / plan & <=15,000 mi .8 / else 1 | plan, 17,200 mi | -> 2918.10 |
| parts_price_index | parameter | >=24 mo +.06 / 12-23 mo +.03 / else 0 | 19 mo | -> 2779.41 |
| parts_volume_discount | parameter | 12-mo customer-pay parts >= 10,000 .05 more / 5,000-9,999.99 .03 more / else 0 | 7,822.77 | -> 2935.57 |

### a diagnostic credit (credit_amount) — result 76.36, all-baseline 165.00 (fleet branch; other accounts: fee x diagnostic_credit_pct where diagnostic_credit_on_repair)
| factor | effect | ladder | T1 tier | T1 |
|---|---|---|---|---|
| spend_scaled_share | method | estimate >= 1,500 & 12-mo spend < 15,000: pct x spend/15,000 / estimate < 1,500 & spend < 15,000: pct x estimate/1,500 / else pct | 2847.19, spend 13,712.73 | -> 83.53 |
| away_store_share_rule (maintenance) | parameter | away & plan .9 / away & no plan .75 / else 1 | KCF, plan | -> 84.85 |
| decision_speed_share | parameter | >14 d .5 / 8-14 d .75 / else 1 | 9 days | -> 101.82 |
| diagnostic_standing_share | parameter | late fee 12 mo & no returned pmt .75 / returned pmt .5 / else 1 | late fee | -> 101.82 |
Edge loads (run): skip c -> g 15.18 (vs 3.89); skip g -> a 76.38 (vs 76.36); skip b -> a 0.

## Probe table (round 3; scratch copies of both worlds, outcomes as run)
| read / edge | world | outcome and rule tier |
|---|---|---|
| all T0 policies | opening / no payments / no parts / no labor / no auths / deals cancelled / plans expired | EOC 118.56/0/0/0/0/103.56/118.56; PRP 5108/0/3642/1347/5108/3977/4958; MEPE 3278 in all; OPR 417.30/402.30/201.24/0/417.30/368.26/400.95 - no crash, stated tiers |
| all T1 policies | opening / no payments / no parts / no labor / no diag fee / no auths / deals cancelled / plans expired | CLC 645.54/0/0/0/645.54/712.82/645.54/581.79; EPD 15.18/0/15.18/0/15.18/15.18/13.01/14.57; REE 2847.19/2847.19/0/2327.18/0/2847.19/2847.19/2918.10; DGC 0 everywhere at the opening (no decision) |
| N-1 zero-run month | T0 world dated 2026-09-30 | MEPE 0: the run is made without an entry, so the redemption's action-form wait is met; 2026-10-31: 3278 |
| exact tie | T1 copy on a Silver account, fee 2.01 x 0.5 = 1.005 | RND(x + 0.000000001, 2) = 1.01 (plain round 1.00); the exact decimal half-up tool helper gives 1.01 |
| zero-amount: comeback | original repair without a labor charge (other store) | basis 0, fee refund 39.95 -> 39.95; any owed credit >= 0.01 |
| zero-amount: discount | comeback credit 900.00 exceeds the charges | floor 0.01 (inside the window, paid in full) |
| zero-amount: discount | paid RO without a labor charge | no invoice to review -> 0, no wait arises |
| returned-payment tier | returned payment 2026-06-01 on the opening world | share 0.25 -> 7.59 (never 0) |
| N-3 in-warranty repeat | Silverado earlier repair moved to 2026-03-09 / 72,400 mi | estimate prices nothing (0); the diagnostic credit's wait does not apply to such a line |
| tie on latest payment day | RO 261019's payment moved to 2026-11-11, listed first | paid RO = RO 261019 (first listed): CLC 0, EPD 0 |
| twelve whole months | rows dated today; the 2025-11-03 check (12 months back) | today's rows count, 12-month-old row excluded |
| month-end whole months | day the later month lacks | complete on the 1st of the month after (stated in every rule) |
| zero-amount: overage / points | T0 copy on Silver with the line billed 0.056 over its tolerance; T0 copy on a new Silver account with 0.80 of labor and parts | overage credit 10.06 (late-completion courtesy on a positive overage; the rule floors any positive overage at 0.01); points 164 (visit and Care bonuses; the rule floors an earning tier at one point) |
| R-1 late month-end run | T0 world after gold, November run made late on 2026-12-10 | rule: ages to the day the run is made, entry dated that day with billing month 2026-11 -> 1000 (capped at the points balance on file; uncapped 2342); on time 2026-11-30 -> 0, made without an entry |
| R-2 non-finite / malformed input | 'inf', 'nan', float inf, '1e3', '27,541', 27541.0 into the overage, redeem and points tools | every case returns an Error string; no exception |
| R-3 EPD retail same-day payment | T0 world, RO 262107 paid on its labor date | 0 (retail invoices earn no discount; no floor) |
| R-3 CLC retail, deductible-only labor | T0 world, RO 262107 labor re-typed service_contract_deductible | 0 (no customer-pay labor, no repeat to review) |
| R-3 CLC fleet, deductible-only repeat | T1 world, RO 261030 labor re-typed | 0 |
| R-3 CLC fleet, original line without labor | T1 world, RO 260205 labor removed | 0 (parts sale); outside the discount's wait by its record test |
| R-4 CLC retail, parts-only original | T0 account (Gold), parts-only counter sale RO 262290 then paid labor RO 262301 | 0 (was 154.80); same world on Net 30 -> 0 |
| R-4 class sweep, estimate | T1 world, RO 250312 line A labor removed (parts sale) | estimate prices nothing (0); the diagnostic credit's wait does not apply |
| F1 PRP unpaid deductible | T0 world, unpaid 100.00 deductible labor row on RO 262107 | not paid in full -> 0 (opening 5108) |
| F2 EPD unpaid deductible | T1 world, unpaid 100.00 deductible labor row on RO 261030 | not paid in full -> 0 (opening 15.18) |
| F3 CLC second labor row | T1 world, second customer-pay labor row 150.00 on RO 261030 (listed after line A) | the latest customer-pay labor charge (line A, listed first on the tie) -> 645.54 |
| R-3 PRP labor under one dollar | T0 copy, RO 262107 labor 0.40 | 0 (no floor); outside the redemption's wait by its record test |
| R-3 EPD labor margin under 10.00 | T1 copy, comeback credit 825.00 on RO 261030 (margin 7.66) | 0; outside the diagnostic credit's wait by its record test |
| half-cent distance | every scored, baseline and sensitivity figure of both tasks | smallest distance 0.0004 (T1 discountable_base_rule 3.2746), 0.0005 (T0 shield_holder_bonus 424.3445) |

## Defining-sentence table (recipe A4, round 4) — every rule sentence -> the baseline, the single factor that uses it, or its plain role
| policy | sentence | used by |
|---|---|---|
| estimate_overage_credit | On every account this policy sets the estimate overage credit on an authorized line: the customer-pay labor an... | overwrite replaced_by |
| estimate_overage_credit | The overage is reviewed when a repair order is paid: the paid repair order is the repair order of the latest p... | baseline |
| estimate_overage_credit | Wherever a record is chosen as the latest of its kind and two such records share that date, the one listed fir... | tie rule (LATEST bindings) |
| estimate_overage_credit | Whole months are counted from one date to another, a whole month being complete on the same day of a later mon... | counting convention (window bindings) |
| estimate_overage_credit | The billed amount of the line is its customer-pay labor and parts charges. | baseline |
| estimate_overage_credit | The overage credit is the billed amount less the authorized amount increased by the estimate tolerance, never ... | baseline |
| estimate_overage_credit | The authorized amount is the estimate amount of the line's latest authorized decision. | baseline |
| estimate_overage_credit | The estimate tolerance is estimate_overage_tolerance_pct. | baseline |
| estimate_overage_credit | The estimate tolerance follows the tier and how long the account has been open: an account at Kessler Owner Re... | factor tenure_tolerance |
| estimate_overage_credit | The authorized amount follows the line's decisions: where the line carries two or more authorized decisions an... | factor supplemental_decisions |
| estimate_overage_credit | The owner courtesy follows how the vehicle on the line's labor charge was bought and the tier: where that vehi... | factor owner_overage_courtesy |
| estimate_overage_credit | The late completion courtesy follows how long the line stayed open after its last authorization: where the lin... | factor late_completion_courtesy |
| estimate_overage_credit | The shop supplies refund follows the repair order's fees and the tier: where a shop supplies fee stands on the... | factor supplies_refund |
| estimate_overage_credit | The credit is assembled in this order: first the overage beyond the tolerance is found, never below zero; then... | assembly (result) |
| estimate_overage_credit | The overage credit is booked against the line's latest customer-pay labor charge as credit_reason estimate_overage. | booking (target tool) |
| estimate_overage_credit | Where no payment has been received on the account, or the paid repair order carries no authorized estimate dec... | absent-record / zero guard (plain binding) |
| paid_ro_points | For a retail rewards account, this policy sets the points a repair order earns when it is paid in full, and on... | overwrite replaced_by |
| paid_ro_points | The paid repair order, whose points are being credited, is the repair order of the latest payment received on ... | baseline |
| paid_ro_points | Wherever a record is chosen as the latest of its kind and two such records share that date, the one listed fir... | tie rule (LATEST bindings) |
| paid_ro_points | The paid repair order is paid in full when its charges, customer-pay and deductible alike, less every credit on it, less the payments received on... | baseline |
| paid_ro_points | The paid labor and parts total is the paid repair order's customer-pay labor and parts charges less the estima... | baseline |
| paid_ro_points | The points credited for the paid repair order are the earning rate times the earning dollars, never more than ... | baseline |
| paid_ro_points | The earning rate is points_earn_per_usd points per dollar. | baseline |
| paid_ro_points | The earning dollars are the paid labor and parts total with the cents dropped. | baseline |
| paid_ro_points | The earning rate follows how the vehicle was bought and the tier: where the vehicle has a closed purchase deal... | factor owner_earning_rate |
| paid_ro_points | The earning dollars follow how the repair order was paid: where a rewards redemption credit stands on the paid... | factor earning_dollars_rule |
| paid_ro_points | The service contract labor bonus follows the vehicle's Kessler Shield contract and the tier: where the vehicle... | factor shield_labor_bonus |
| paid_ro_points | The tenure multiplier follows how long the account has been open and the tier: where the account was opened at... | factor tenure_multiplier_rule |
| paid_ro_points | The visit bonus follows the account's payment history and tier: where at least visit_bonus_payments payments w... | factor visit_frequency_bonus |
| paid_ro_points | The Kessler Care member bonus follows the customer's maintenance plans and tier: where the customer holds an a... | factor care_member_bonus |
| paid_ro_points | The points are assembled in this order: first the earning rate is applied to the earning dollars, every per-do... | assembly (result) |
| paid_ro_points | A record falls within the last twelve whole months when fewer than twelve whole months separate its date from ... | counting convention (window bindings) |
| paid_ro_points | The points for a paid repair order are fixed only after the records carry the overage credit owed on every lin... | prerequisite sentence |
| paid_ro_points | The points are booked as one points-earned entry for the paid repair order, dated on the crediting date. | booking (target tool) |
| paid_ro_points | Where no payment has been received on the account there is no paid repair order and no points are credited. | absent-record / zero guard (plain binding) |
| paid_ro_points | A repair order whose customer-pay labor charges, less the estimate overage, comeback, goodwill and rewards red... | absent-record / zero guard (plain binding) |
| month_end_points_expiry | For the month-end expiry of an open retail rewards account, this policy sets the points expiring, and only for... | overwrite replaced_by |
| month_end_points_expiry | The points expiring at a month-end run are the aged points less the points already used, never below zero. | baseline |
| month_end_points_expiry | A point is aged once more than the expiry period has passed since the date it was earned, counted in whole mon... | baseline |
| month_end_points_expiry | The expiry period follows the customer's Kessler Care plans and the tier: where the customer holds an active K... | factor care_plan_extension |
| month_end_points_expiry | The expiry period also follows the customer's Kessler Shield contracts and the tier: where the customer holds ... | factor shield_contract_extension |
| month_end_points_expiry | The points already used follow the account's recent activity: where the account is at Kessler Owner Rewards Go... | factor used_points_order |
| month_end_points_expiry | The protected reserve follows how long the account has been open and the tier: where the account was opened at... | factor long_member_reserve |
| month_end_points_expiry | The points expiring are figured in this order: first the aged points are found under the expiry period as ever... | assembly (result) |
| month_end_points_expiry | A record falls within the last whole months named when fewer than that many whole months separate its date fro... | counting convention (window bindings) |
| month_end_points_expiry | The month-end run for a calendar month is due on that month's last day; a run not made on that day is made on ... | baseline |
| owner_points_redemption | For a redemption of the whole redeemable points balance toward the open repair order of a retail rewards accou... | overwrite replaced_by |
| owner_points_redemption | The open repair order is the repair order of the latest labor charge on the account, and the redeeming vehicle... | baseline |
| owner_points_redemption | Wherever a record is chosen as the latest of its kind and two such records share that date, the one listed fir... | tie rule (LATEST bindings) |
| owner_points_redemption | The redemption credit is the redeemable points times the value of a redeemed point, never more than points_max... | baseline |
| owner_points_redemption | The redeemable points are the whole points balance on file. | baseline |
| owner_points_redemption | A redeemed point is worth points_value_usd. | baseline |
| owner_points_redemption | The value of a redeemed point follows the tier and how long the account has been open: an account at Kessler O... | factor tenure_point_value |
| owner_points_redemption | The owner redemption bonus follows the redeeming vehicle's records with the group: where the redeeming vehicle... | factor owner_vehicle_bonus |
| owner_points_redemption | The service contract bonus follows the redeeming vehicle's Kessler Shield contract and the tier: where the red... | factor shield_holder_bonus |
| owner_points_redemption | The redeemable points follow the account's payment record and age: where a returned payment was posted on the ... | factor held_points_rule |
| owner_points_redemption | The home store credit follows where the open repair order was written and the tier: where it was written at th... | factor home_store_redemption_credit |
| owner_points_redemption | The frequent visit credit follows the account's payment history and tier: where at least frequent_visit_paymen... | factor frequent_visit_redemption_credit |
| owner_points_redemption | The amounts are assembled in this order: first every bonus rate this policy sets out is added into one rate an... | assembly (result) |
| owner_points_redemption | A record falls within the last twelve whole months when fewer than twelve whole months separate its date from ... | counting convention (window bindings) |
| owner_points_redemption | The redemption credit is fixed only after the records carry the points earned for every repair order on the ac... | prerequisite sentence |
| owner_points_redemption | The redemption credit is not fixed until the month-end points expiry run for the latest calendar month whose l... | prerequisite sentence |
| owner_points_redemption | The redemption is booked as one points redemption of the redeemable points for the redemption credit, together... | booking (target tool) |
| owner_points_redemption | Where the account carries no labor charge there is no open repair order and no redemption credit. | absent-record / zero guard (plain binding) |
| comeback_labor_credit | For a comeback on a commercial fleet account, this policy sets the comeback credit, and only for such an accou... | overwrite replaced_by |
| comeback_labor_credit | Comebacks are reviewed when a repair order is paid: the paid repair order is the repair order of the latest pa... | baseline |
| comeback_labor_credit | The original repair is the latest customer-pay parts replacement recorded on the same unit, and its labor char... | baseline |
| comeback_labor_credit | Wherever a record is chosen as the latest of its kind and two such records share that date, the one listed fir... | tie rule (LATEST bindings) |
| comeback_labor_credit | Whole months are counted from one date to another, a whole month being complete on the same day of a later mon... | counting convention (window bindings) |
| comeback_labor_credit | The repeat falls inside the store's repair warranty when the repeat labor charge's line date is on or before t... | baseline |
| comeback_labor_credit | The comeback credit is the credit basis times the covered labor share, rounded half up to the cent; it is owed... | baseline |
| comeback_labor_credit | The credit basis is the repeat labor charge. | baseline |
| comeback_labor_credit | The covered labor share is comeback_labor_covered_pct. | baseline |
| comeback_labor_credit | On a commercial fleet account, the covered labor share follows the age of the original repair: where the origi... | factor aged_repair_share |
| comeback_labor_credit | On a commercial fleet account, the credit basis follows where the two repairs were done: where the original re... | factor original_store_basis |
| comeback_labor_credit | On a commercial fleet account, the wear deduction follows the miles between the repairs and the unit's mainten... | factor wear_deduction_rule |
| comeback_labor_credit | On a commercial fleet account, the declined-work share follows the original repair order's declined estimate d... | factor declined_work_share |
| comeback_labor_credit | On a commercial fleet account, the shop fee refund follows the fees the customer already paid on the original ... | factor repeat_fee_refund |
| comeback_labor_credit | On a commercial fleet account the credit is assembled in this order: first the credit basis is multiplied by t... | assembly (result) |
| comeback_labor_credit | On any other account the credit is the repeat labor charge times comeback_labor_covered_pct, rounded half up t... | assembly (result) |
| comeback_labor_credit | The comeback credit is booked against the repeat labor charge as credit_reason comeback_repair. | booking (target tool) |
| comeback_labor_credit | Where no payment has been received on the account, or the paid repair order carries no customer-pay labor char... | absent-record / zero guard (plain binding) |
| comeback_labor_credit | On every account, an original repair line that carries no customer-pay labor charge is a parts sa... | absent-record / zero guard (plain binding) |
| early_payment_discount | For a fleet invoice paid in full, this policy sets the early-payment discount, and only for such an invoice; i... | overwrite replaced_by |
| early_payment_discount | The invoice reviewed is the repair order of the latest payment received on the account; its invoice date is th... | baseline |
| early_payment_discount | Wherever a record is chosen as the latest of its kind and two such records share that date, the one listed fir... | tie rule (LATEST bindings) |
| early_payment_discount | The invoice is paid in full when its charges, customer-pay and deductible alike, less every credit on it, less the payments received on it, plus ... | baseline |
| early_payment_discount | The early-payment discount is the discount rate times the discountable total, rounded half up to the cent, and... | baseline |
| early_payment_discount | The discount rate is early_pay_discount_pct. | baseline |
| early_payment_discount | The discount window is early_pay_discount_days calendar days. | baseline |
| early_payment_discount | The discountable total is the invoice's customer-pay labor and parts charges less the comeback, estimate overa... | baseline |
| early_payment_discount | The discount window follows how the invoice was paid and the terms: where the latest payment on the invoice wa... | factor ach_window_rule |
| early_payment_discount | The discount rate follows how the invoice's unit was bought and the terms: where the unit was bought under a F... | factor fleet_deal_rate |
| early_payment_discount | The prompt-payer addition follows the account's payment history and terms: where at least prompt_payer_payment... | factor prompt_payer_addition |
| early_payment_discount | The tenure addition follows how long the account has been open and the terms: where the account was opened at ... | factor account_tenure_addition |
| early_payment_discount | The discountable total follows how the invoice was paid and the unit's maintenance record: where the latest pa... | factor discountable_base_rule |
| early_payment_discount | The discount standing share follows the account's payment record: where a late fee was assessed on the account... | factor payment_standing_share |
| early_payment_discount | The discount is figured in this order: first every addition this policy sets out is added to the discount rate... | assembly (result) |
| early_payment_discount | No discount is given on an invoice whose customer-pay labor charges exceed the comeback, estimate overage and ... | absent-record / zero guard (plain binding) |
| early_payment_discount | A record falls within the last twelve whole months when fewer than twelve whole months separate its date from ... | counting convention (window bindings) |
| early_payment_discount | The early-payment discount on an invoice is not fixed until the records carry the comeback credit owed on ever... | prerequisite sentence |
| early_payment_discount | The discount is booked against the invoice's latest customer-pay labor charge as credit_reason early_payment_discount. | booking (target tool) |
| early_payment_discount | Where no payment has been received on the account, or the paid repair order carries no customer-pay labor char... | absent-record / zero guard (plain binding) |
| repeat_repair_estimate | This policy prices the written estimate for a diagnosed concern line whose failure repeats the latest customer... | scope / shared selection (plain binding) |
| repeat_repair_estimate | The line estimated is the line of the latest diagnostic fee charged on the account, its posted labor rate is t... | baseline |
| repeat_repair_estimate | The earlier repair is the latest customer-pay parts charge recorded on the same vehicle, together with the lab... | baseline |
| repeat_repair_estimate | Wherever a record is chosen as the latest of its kind and two such records share that date, the one listed fir... | tie rule (LATEST bindings) |
| repeat_repair_estimate | The estimate is the labor amount plus the parts amount, rounded half up to the cent. | baseline |
| repeat_repair_estimate | The labor amount is the repair hours times the labor rate, less the tier's labor_discount_pct of that product,... | baseline |
| repeat_repair_estimate | The repair hours are the hours of the earlier repair's latest labor charge. | baseline |
| repeat_repair_estimate | The labor rate is the posted labor rate on the diagnostic fee. | baseline |
| repeat_repair_estimate | The parts amount is the earlier repair's parts list price less the tier's parts_discount_pct. | baseline |
| repeat_repair_estimate | The labor rate follows where the two repairs were written, the estimate's repair order being written at the st... | factor rate_lock_rule |
| repeat_repair_estimate | The repair hours follow the diagnosis and the earlier repair's labor: where the diagnostic fee was charged for... | factor diagnosis_overlap_hours |
| repeat_repair_estimate | The repeat allowance follows how recent the earlier repair is: where the earlier repair's line date is no more... | factor repeat_labor_allowance |
| repeat_repair_estimate | The maintained-vehicle allowance follows the vehicle's Kessler Care plan and the miles since the earlier repai... | factor maintained_vehicle_allowance |
| repeat_repair_estimate | The parts price index follows the age of the earlier repair: where the earlier repair's line date is at least ... | factor parts_price_index |
| repeat_repair_estimate | The parts volume discount follows the account's customer-pay parts purchases: where the account's customer-pay... | factor parts_volume_discount |
| repeat_repair_estimate | The estimate is figured in this order: first the repair hours are multiplied by the labor rate and the tier di... | assembly (result) |
| repeat_repair_estimate | A record falls within the last twelve whole months when fewer than twelve whole months separate its date from ... | counting convention (window bindings) |
| repeat_repair_estimate | The estimate is recorded as the customer's own authorized decision on the diagnosed concern line, dated on the... | booking (target tool) |
| repeat_repair_estimate | Where the account carries no diagnostic fee, or the vehicle on it has no earlier customer-pay parts charge, th... | absent-record / zero guard (plain binding) |
| repeat_repair_estimate | Where the diagnosis date is on or before the day comeback_warranty_months calendar months after the earlier re... | absent-record / zero guard (plain binding) |
| diagnostic_credit | For a commercial fleet account, this policy sets the diagnostic credit, and only for such an account; on any o... | overwrite replaced_by |
| diagnostic_credit | The diagnostic fee credited is the latest diagnostic fee charged on the account, and the line is its repair or... | baseline |
| diagnostic_credit | Wherever a record is chosen as the latest of its kind and two such records share that date, the one listed fir... | tie rule (LATEST bindings) |
| diagnostic_credit | The authorized estimate is the estimate amount of the latest authorized decision on that repair order and conc... | baseline |
| diagnostic_credit | The diagnostic credit is the diagnostic fee times the diagnostic credit share, rounded half up to the cent, an... | baseline |
| diagnostic_credit | On every account the repair counts as authorized on the date of the latest authorized decision on the diagnose... | overwrite replaced_by |
| diagnostic_credit | The diagnostic credit share is diagnostic_credit_pct. | baseline |
| diagnostic_credit | On a commercial fleet account, the diagnostic credit share follows the account's twelve-month spend and the si... | factor spend_scaled_share |
| diagnostic_credit | On a commercial fleet account, the away-store share follows where the diagnosis was done and the maintenance r... | factor away_store_share_rule |
| diagnostic_credit | On a commercial fleet account, the decision share follows how long the customer took to authorize: where the a... | factor decision_speed_share |
| diagnostic_credit | On a commercial fleet account, the diagnostic standing share follows the account's payment record: where a lat... | factor diagnostic_standing_share |
| diagnostic_credit | On a commercial fleet account the credit is figured in this order: first the diagnostic credit share is applie... | assembly (result) |
| diagnostic_credit | On any other account the credit is the diagnostic fee times diagnostic_credit_pct where the tier's diagnostic_... | assembly (result) |
| diagnostic_credit | A record falls within the last twelve whole months when fewer than twelve whole months separate its date from ... | counting convention (window bindings) |
| diagnostic_credit | A diagnostic credit on a line whose vehicle carries an earlier customer-pay parts repair with its store repair... | prerequisite sentence |
| diagnostic_credit | The diagnostic credit is fixed only after the records carry the early-payment discount owed on every fleet inv... | prerequisite sentence |
| diagnostic_credit | The diagnostic credit is booked against the diagnostic fee as credit_reason diagnostic_applied_to_repair. | booking (target tool) |
| diagnostic_credit | Where the account carries no diagnostic fee there is no diagnostic credit. | absent-record / zero guard (plain binding) |

## Round 2 notes (audit revision_1 items)
- C-1: EOC covers every account (scope dropped); CLC and DGC price other accounts exactly as their restated base text (branch in result); PRP/OPR/MEPE price 0 for every account whose tier earns no points, which equals base.
- C-2: generic assembly sentences (classes in a fixed order) in all 8 rules.
- C-3/C-8: CLC store-basis tier 2 redesigned; duty_share_rule -> downtime_allowance_rule; REE parts_warranty_rule -> parts_volume_discount.
- C-4: no split payer remains; REE overwrite [] holds (coverage priority untouched).
- C-5: OPR waits on the billing-month entry of the latest month whose last day falls on or before the redemption date; MEPE's entry carries its month as billing month.
- C-6: DGC docstring and every docstring free of ordering words.
- C-7: PRP paid-in-full gate; CLC warranty gate; DGC latest-decision window via declared overwrite; tie sentence in every rule.
- C-9: vehicle/store selectors moved into the factor sentences that use them (EOC owner courtesy, REE rate lock, DGC away share).
- C-10: rolling 'last twelve whole months' convention stated in every policy that windows; whole-month month-end convention stated in every rule.
- Tools: half-up cents helper (class static method), positive amounts / whole points / YYYY-MM enforced, source row must be a labor (or diagnostic fee) row of the same account and repair order.

## Round 3 notes (audit revision_2 items)
- N-1: OPR <- MEPE is action form ("... has been made"), fallback_reason: a run expiring nothing books no entry; MEPE states such a run is made without an entry.
- N-2: CLC downtime allowance removed (lost time is POLICY_NOT_COVERED); replaced by repeat_fee_refund (method, added input).
- N-3: REE prices nothing inside the earlier repair's store warranty (base comeback rule honoured; service_evt_comeback added to REE's refs); DGC's wait on the authorization carved to out-of-warranty repeats.
- N-4: CLC store-basis tier 2 = original + half the excess; REE rate_lock relabelled parameter.
- N-5: tools enforce the line-letter set, the source row's line, numeric parsing of points and amounts; module docstring states what is enforced.
- Zero-amount class: floors (overage credit 0.01, at least one point, comeback 0.01 when owed, discount 0.01 inside the window), returned-payment share 0.25, EPD no-labor guard.
- Rounding: every money RND is RND(x + 0.000001, 2); exact-tie probe passes.

## Round 4 notes (audit revision_3 items)
- R-1: MEPE rule: a run not made on its month's last day is made on the day it is made, aging points and counting windows to that day; entry dated that day with the month the run is for; never more than the points balance on file. Rule, compute (NOW-keyed) and tool ('dated today') agree.
- R-2: exact decimal half-up helper; non-finite, exponent-form, comma and non-integer inputs return Error strings in every money/points tool.
- R-3: all floors removed (PRP one point, CLC both branches, EPD); zero cases carved by plain record tests on the blocked side (OPR <- PRP: labor net of credits >= 1.00; EPD <- CLC: original line carries customer-pay labor; DGC <- EPD: fleet invoice with labor exceeding credits by >= 10.00) and made exact in the depended-on rules (PRP earns nothing under 1.00; EPD gives nothing under a 10.00 margin; CLC owes nothing without repeat labor or, on fleet, without original labor).
- Rounding ruling: RND(x + 0.000000001, 2); owner_plan_bonus_pct 0.15 -> 0.16 (T0 redemption 441.56) and maintained_share_high 0.9 -> 0.88 (T1 estimate 2847.19) move every scored, baseline and sensitivity figure more than 1e-6 off a half cent.

## Round 5 notes (audit revision_4 item)
- R-4: the parts-sale test (an original line with no customer-pay labor charge is not a repair the store performed and carries no repair warranty) holds on every account in CLC's rule and compute (original_labor > 0 inside in_warranty, both branches). Class sweep: REE prices nothing where the earlier line carries no customer-pay labor (parts sale) and DGC's wait on the authorization is carved to earlier repairs with a customer-pay labor charge; no other policy keys on a store-performed repair. Task values unchanged.

## Round 6 notes (render_source render_r1 F1-F4)
- F1/F2: 'paid in full' counts every charge, deductibles included, in the points and discount rules and computes.
- F3: one booking row everywhere - CLC repeat labor charge = latest customer-pay labor charge (amount, date, odometer, store, unit read from it); EOC and EPD book against the latest customer-pay labor charge; CLC original labor and REE earlier repair stated as line totals, matching their sums.
- F4: OPR held_points_rule reads its own enrollment_age_months; mechanical sweep found no other factor reading another factor's binding.
- Gold values unchanged in both tasks.

## Round 7 notes (policy_kb SRC-1, SRC-2; seed only)
- SRC-1: Silverado plan KC-2404183 odometer_at_sale 66,150 -> 47,850 (expiration_odometer 122,850), consistent with RO 250312 at 61,200 a year later.
- SRC-2: every Kessler Care plan in both worlds carries its plan ledger (visits loaded at sale + visits redeemed with RO, store, odometer in date order); visits_remaining = loaded - redeemed: KC-2408317 2 (4 redeemed), KC-2409266 7 (5 redeemed), KC-2404183 6 (6 redeemed). find_maintenance_plan_ledger added to both golds after find_maintenance_plans (later step numbers +1). Charter/tools byte-identical; scored values unchanged.

## Round 8 notes (policy_kb SRC-3..SRC-6; seed/persona only)
- SRC-3 (T0): retail deal holds follow reservation + hold days + extensions (KHB-24-21873 -> 2024-04-18, 1 extension; KTD-23-20946 -> 2023-06-16, 1 extension).
- SRC-4 (T1): fleet deals hold_expires_date = reservation + 14 (2022-03-15, 2021-02-22); title applications 2022-03-18, 2021-02-25 (within 30 days of delivery).
- SRC-5 (T1): customer profile and fleet account opened 2021-01-11 (before the net-terms deal); tenure 70 whole months on 2026-11-11 (tier unchanged).
- SRC-6 (T0): RO 262245 described as front and rear brake pads and rotors (wear items outside the Factory Basic warranty); customer pay stands.
- Scored values unchanged.
