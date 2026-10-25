# prepaid_maintenance_plans — instantiation plan (env_0075, band 3)

Scratch: /tmp/prepaid_maintenance_plans_0075/ . frozen_time for both tasks: `2026-10-21 10:15:00 EDT`.

## Draw (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=3 (4 problems), factor_counts=[4, 6, 6, 5]
- task 1: prerequisite_problems=1 (2 problems), factor_counts=[4, 4]

## Domain constraint that shapes the design
Every problem needs a 4-6 factor numeric computation. In the maintenance charter only three writes carry a
policy-computed number: the plan sale (purchase_price), the cancellation (refund amount booked by the
triggered refund_calculated entry) and the fleet substitution (the moved plan's expiration odometer, once
re-based). Redemption / reinstatement / expiry / refund payment record no policy-variable number (visit=1,
visits remaining, refund due), so they are NOT used as problems (no decorative computations).
The customer's own write must be numeric too, so the user tools are the plan contracts the customer signs
(retail plan contract, fleet plan addendum). Cancellation tools are split by plan family / reason so that
the fleet tree has two count-changing prerequisites.

## Tools (6, one per extended policy) — final names in task_tools.py
| task | tool (owner) | event(s) written (base triggers booked) | computes | policy |
|---|---|---|---|---|
| 0 root | sign_fleet_care_addendum_* (user) | maintenance_plan_sold -> maintenance_visits_loaded (maintenance only) | purchase_price | maintenance_ext_fleet_addendum_price |
| 0 | process_fleet_plan_cancellation_* (agent) | maintenance_plan_cancelled -> maintenance_visits_cancelled + maintenance_refund_calculated; request -> completed | amount | maintenance_ext_fleet_cancel_refund |
| 0 | process_total_loss_cancellation_* (agent) | same as above (reason total_loss) | amount | maintenance_ext_total_loss_refund |
| 0 | move_fleet_plan_* (agent) | maintenance_vehicle_substituted (triggers []) | expiration_odometer | maintenance_ext_fleet_transfer_odometer |
| 1 root | sign_care_plan_contract_* (user) | maintenance_plan_sold -> maintenance_visits_loaded | purchase_price | maintenance_ext_retail_plan_price |
| 1 | process_care_plan_cancellation_* (agent) | maintenance_plan_cancelled -> visits_cancelled + refund_calculated | amount | maintenance_ext_retail_cancel_refund |
No tool writes an event whose triggers leave the maintenance category (all maintenance triggers are
maintenance:*). No fee/bill rows anywhere.

## Task 0 tree (fleet business, Commercial Fleet Account - Net 30)
root: fleet addendum on newly delivered unit D (user signs)
- <- fleet cancellation of plan on sold unit B (value_input: fleet volume count)
- <- total-loss cancellation of plan on totaled unit A (value_input: fleet volume count)
- <- transfer of retired unit Z's plan onto its replacement C (state_gate: plan schedule current)
Fan-out; the three prerequisites do not read each other's writes -> commute (proved by run).

## Task 1 tree (individual, Owner Rewards)
root: retail plan contract on newly delivered car (user signs)
- <- retail cancellation of the plan on the traded-in car (value_input: trade-cycle loyalty credit)

(sections below are filled per policy: factor tables, all-pairs method tables, T1/T2, probes, events)

## REVISION (DSL gate finding, before any artifact used it)
check_extended forbids XCOUNT/EXISTS/CFIELD on the primary category, and COUNT/SUM/LATEST are scoped to
the computation's own holding. So a value_input edge can only carry a write made on the dependent
computation's anchor plan. Fleet tree redesigned as a chain on ONE plan (the plan of retired unit Z):
  transfer of Z's plan onto replacement C (value_input -> total-loss refund: unit + re-based odometer)
  -> total-loss cancellation of that plan (C was totaled) (value_input -> root: replacement credit)
  -> root: fleet addendum on new unit D, anchored on that plan (proxy holding, same plan name)
  + fleet cancellation of plan B (sold unit) as a state_gate on the root (signed requests processed first).
Tools unchanged (6). Factor counts: root 6, fleet cancel 6, transfer 5, total-loss 4.
Retail tree: root sale anchored on the traded car's plan X; retail cancel of X feeds trade-cycle credit.
All cancellation requests in both worlds are dated the frozen date (effective date = NOW for DSL spans).

## Final policy set (6) and trees
| policy | tool (owner) | factors | task |
|---|---|---|---|
| maintenance_ext_fleet_addendum_price | sign_fleet_care_addendum_ac106112 (user) | 6 | 0 root |
| maintenance_ext_fleet_cancel_refund | process_fleet_plan_cancellation_44bd9d69 (agent) | 6 | 0 |
| maintenance_ext_fleet_transfer_odometer | move_fleet_plan_badb11fe (agent) | 5 | 0 |
| maintenance_ext_total_loss_refund | process_total_loss_cancellation_8f67308a (agent) | 4 | 0 |
| maintenance_ext_retail_plan_price | sign_care_plan_contract_c0d53aa0 (user) | 4 | 1 root |
| maintenance_ext_retail_cancel_refund | process_care_plan_cancellation_e800fe25 (agent) | 4 | 1 |
Task 0 edges: root -> total_loss (value_input, replacement_credit); root -> fleet_cancel (state_gate,
maintenance_plans.status); total_loss -> transfer (value_input, loss_refund). Order: transfer, total-loss,
fleet cancel, root (fleet cancel commutes with the other two: it reads only plan B, service, purchase).
Task 1 edge: root -> retail_cancel (value_input, trade_credit).

## Events written by tools, with base triggers (XF 18)
| tool | events | base triggers | lands outside maintenance? |
|---|---|---|---|
| sign_fleet_care_addendum / sign_care_plan_contract | maintenance_plan_sold | -> maintenance:maintenance_visits_loaded (booked by the same call) | no |
| process_*_cancellation (3 tools) | maintenance_plan_cancelled | -> maintenance:maintenance_visits_cancelled, maintenance:maintenance_refund_calculated (both booked) | no |
| move_fleet_plan | maintenance_vehicle_substituted | [] | no |
Also: request_status -> completed on maintenance_cancellation_requests (intake row of the same category).
No fee/bill rows; maintenance has no money row other than refund entries.

## All-pairs method tables (XF 5: distinguishing input per pair)
- unit_basis (fleet addendum): T_a = plan_price_usd - retail_value_per_visit_usd (FCM on unit); T_b = visits_included x retail_value_per_visit_usd (no FCM, delivery odometer > demo_miles_threshold); T_c = plan_price_usd.
  a/b: a subtracts V from list, b multiplies V by visit count (no list); a/c: a adds input V; b/c: b drops list, uses V x N.
- retail_basis (retail plan): same three shapes, tier b keyed on a Certified Pre-Owned deal instead of delivery miles.
- usage_share (fleet cancel): T_a = MN(visit share, mile share to highest RO check-in); T_b = MN(visit share, day share from effective date); T_c = visit share.
  a/b: mile input (RO odometer, expiration_odometer) vs day input (dates); a/c and b/c: added second input + min pick.
- loss_share (total loss): T_a = price x average(visit share, mile share); T_b = price x average(visit share, day share); T_c = standard refund (visit share / retail value). a/b mile vs day input; a/c, b/c added second share + averaging. (Revised from a greater-of pick: check_compute showed history not load-bearing under the max.)
- closing_reading_source (transfer): T_a = trade appraisal odometer on the replacement's closed deal; T_b = highest RO check-in of retired unit; T_c = latest plan-visit odometer. Three different records.
- starting_reading_source (transfer): T_a = highest RO check-in of replacement; T_b = odometer at delivery - delivery distance (home delivery); T_c = odometer at delivery. a/b different record; b/c added subtraction input.
- retail_refund_basis (retail cancel): T_a = pro rata (price x unused / included); T_b = MX(retail-value amount, pro rata); T_c = retail-value amount (price - used x V). a/b max pick adds RV; a/c different formula; b/c max pick adds pro rata.

## T1 / T2 per factor (T1 = task world, factor alone at baseline moves result; T2 = producible world, factor alone off baseline)
Task 0 (figures from /tmp scratch run, handling-time worlds):
| policy | factor | gold | T1 baseline-substituted | T2 world |
|---|---|---|---|---|
| addendum | unit_basis | 756.03 | 848.13 | any world: FCM unit vs none (other factors at 0) |
| addendum | account_standing | 756.03 | 784.05 | Net 30, no late fee, no other credits |
| addendum | new_unit_enrollment | 756.03 | 796.03 | unit delivered <=30 days, other factors baseline |
| addendum | account_tenure | 756.03 | 786.03 | account >=96 months |
| addendum | loss_replacement | 756.03 | 816.03 | total-loss cancellation in window |
| addendum | credit_utilisation | 756.03 | 776.03 | open balance <= 25% of limit |
| fleet cancel | usage_share | 311.89 | 351.02 | RO check-in > interval past last visit |
| fleet cancel | replacement_fee | 311.89 | 286.89 | fleet deal delivered <=30 days |
| fleet cancel | filter_visits | 311.89 | 356.89 | visit 6 redeemed |
| fleet cancel | recent_visit | 311.89 | 326.89 | last visit 31-90 days |
| fleet cancel | discount_recapture | 311.89 | 394.21 | plan sold below list < 12 months |
| fleet cancel | fleet_standing | 311.89 | 291.89 | Net 30 >= 60 months |
| total loss | loss_share | 495.67 | 408.00 | unit delivered on Kessler deal < 12 months |
| total loss | loss_courtesy | 495.67 | 470.67 | fleet account no late fee |
| total loss | replacement_purchase | 495.67 | 465.67 | delivered deal <= 30 days |
| total loss | plan_relationship | 495.67 | 485.67 | unit with RO lines |
| transfer | closing_reading_source | 42650 | 44870 | trade-in on replacement deal |
| transfer | starting_reading_source | 42650 | 37794 | replacement with RO check-in |
| transfer | account_transfer_allowance | 42650 | 41650 | Net 30 |
| transfer | unused_visit_allowance | 42650 | 41150 | 3-5 visits unused |
| transfer | booking_delay | 42650 | 40650 | replacement delivered > 60 days |
No min/max-of-caps masking: the only MN/MX are the share picks (inputs are not factors) and guards.

## Probe table per read (XF 9) — decoys / absent / None / ties / month-end
| read | decoy or edge case | stated rule outcome | DSL outcome |
|---|---|---|---|
| CFIELD purchase fleet deal status=delivered (unit being enrolled, fee/bonus deal) | closed deal C (decoy) | only the delivered-status agreement counts | filter status=delivered excludes C |
| same | no delivered deal | allowance/fee tier "no such agreement" | guard -> 99999 days -> fall-through |
| same | two delivered fleet deals | rule names "the agreement of the unit being enrolled"; DSL takes the first match | residue (DSL first match); world has one |
| CFIELD purchase fleet deal status=closed (replacement) | delivered deal D (decoy) | only the closed agreement that took the trade-in | filter status=closed |
| CFIELD trade_in_allowance | 0.00 / empty | tier a needs allowance above 0.00 | float(x or 0) > 0 |
| EXISTS warranty FCM on unit | voided basic coverage on C (decoy), expired FCM | only an active FCM on the enrolled unit | filters variant+status+vehicle_id |
| XCOUNT service late fees 12 months | late fee 2025-07-18 (15 months, near-miss) | "fewer than 12 whole months" excludes it | within_months=12 -> MONTHS 15 excluded |
| same | month-end: fee dated 2025-10-31 vs pricing 2026-10-21 | whole months = 11 -> counts | MONTHS() = 11 -> counts (same convention) |
| XMAX service odometer_in by vehicle | no RO for the unit | B: no check-in -> share tier b/c; total loss: odometer_at_sale used | XMAX -> 0.0; guards use > comparisons |
| LATEST plan visit odometer | no redemption | odometer_at_sale | `or F('odometer_at_sale')` |
| same | same-day tie of two redemptions | first row kept (LATEST keeps first) | residue: world has none |
| COUNT cancellations within 3 months on anchor plan | cancellation 3+ months old | excluded | within_months=3 |
| SUM visits (loaded/redeemed/reinstated) | reinstated visit | added back as unused | SUM reinstated added |
| redemption later reinstated (filter visit / latest visit) | reinstated visit 6 | rule says "redeemed" (DSL cannot net per visit) | residue: world has no reinstatement |
| DAYS share denominators | sale_date == expiration_date | impossible (term_months > 0) | n/a |
| CFIELD purchase status for plan's deal | standalone plan (empty deal id) | no unwound test | guard `if F('purchase_deal_id')` |
| CFIELD service credit_limit 0 (retail tier) | utilisation credit | "no credit limit earns none" | guard utilisation_limit > 0 |
| refund below 0.00 | large deductions | floored at 0.00 | MX(0, ...) |
| total-loss refund above price | big credits | never exceeds purchase_price | MN(price, ...) |

# ROUND 2 (supersedes the round-1 factor, T1/T2 and probe tables above)
Audit revision_1 items and closures are listed in worklog.md. Trees unchanged in shape:
task 0: transfer (value_input) -> total-loss refund (value_input) -> fleet addendum; fleet cancel = state_gate on the addendum.
task 1: retail cancel (value_input) -> retail price. Tools and events unchanged (events table above still holds).

## Factor sets (counts per draw: task 0 {6,6,5,4}, task 1 {4,4})
| policy | method factor(s) | parameter factors |
|---|---|---|
| fleet_addendum_price (6) | unit_basis | account_standing (multi-source), new_unit_enrollment, account_tenure, loss_replacement, service_spend |
| fleet_cancel_refund (6) | usage_share | net_terms_fee, filter_visits, discount_recapture, fleet_tenure_refund, unit_service_history |
| fleet_transfer_odometer (5) | closing_reading_source, starting_reading_source | account_transfer_allowance, unused_visit_allowance, booking_delay |
| total_loss_refund (4) | loss_share | loss_courtesy (multi-source), replacement_purchase, plan_relationship |
| retail_plan_price (4) | retail_basis | owner_rewards, new_owner_enrollment, trade_cycle (multi-source) |
| retail_cancel_refund (4) | retail_refund_basis | trade_up_fee, bundle_recapture_rate, rewards_refund |

## All-pairs method tables (XF 5) — every tier takes record inputs
- unit_basis / retail_basis: T_a = price x max(months share, miles share) [FCM expiry date, FCM expiration_odometer, delivery odometer]; T_b = price x months share [FCM expiry date]; T_c = price. a/b: miles input + max pick; a/c, b/c: record-derived multiplier.
- usage_share: T_a = min(visit share, mile share to highest RO check-in); T_b = min(visit share, day share); T_c = visit share.
- loss_share: T_a = price x avg(visit share, mile share to max(check-in, delivery odometer)); T_b = price x avg(visit share, day share); T_c = standard refund.
- closing_reading_source: T_a = retired unit's highest RO check-in; T_b = highest odometer on a claim under its Factory Basic warranty; T_c = last recorded visit reading (MAX redemption odometer, odometer_at_sale floor). Three record sources.
- starting_reading_source: T_a = replacement's highest check-in; T_b = delivery odometer - delivery distance; T_c = delivery odometer.
- retail_refund_basis: T_a = price x unused/included (financed plan); T_b = min(retail value, price x day share) (unfinanced, term > half run); T_c = retail value. T_b != T_c whenever price x day share < retail value (few visits used late in term); T_a != T_b (different inputs and tier keys).

## T1 / T2 (gold / factor-at-baseline; T2: additive or multiplicative into an unconstrained sum -> producible single-factor world)
task 0 addendum 515.57: unit_basis 848.13, account_standing 536.15, new_unit_enrollment 555.57, account_tenure 545.57, loss_replacement 575.57, service_spend 535.57; all-baseline 1029.00.
task 0 fleet cancel 331.89: usage_share 371.02, net_terms_fee 316.89, filter_visits 376.89, discount_recapture 414.21, fleet_tenure_refund 311.89, unit_service_history 316.89; all 448.34.
task 0 transfer 43130: closing 44870, starting 38274, transfer allowance 42130, unused visits 41630, booking delay 41130; all 35514.
task 0 total loss 498.96: loss_share 408.00, courtesy 473.96, replacement_purchase 468.96, relationship 488.96; all 343.00.
task 1 retail cancel 421.05: retail_refund_basis 295.22, trade_up_fee 346.05, bundle_recapture_rate 435.03, rewards_refund 401.05; all 214.20.
task 1 retail price 269.50: retail_basis 591.04, owner_rewards 284.06, new_owner_enrollment 299.50, trade_cycle 319.50; all 699.00.

## Date anchors
Cancellation policies (fleet, total-loss, retail) are scoped to a request processed on its own request date; every span (free look, day share, months in force, fee/bonus windows, tenure) ends on the effective date = the processing day = NOW. A later-processed request is outside the policy (base terms). Both worlds' requests are dated 2026-10-21. Delivery spans use MX(0, DAYS(...)) so a future delivery can never land on a generous tier.

## Probe table per read (round 2, run on scratch copies of the task worlds)
| read | decoy / edge | rule outcome | DSL outcome / probe result |
|---|---|---|---|
| plan redemption entries (MAX odometer, COUNT in 12 months) | redemption later reinstated | rule counts redemption entries "reinstated or not" for readings and activity | same; probe (B visit 6 reinstated): 376.89 |
| filter deduction | reinstated visit | net visits used (redeemed - reinstated) | SUM - SUM; probe: filter 0 at 5 net |
| last recorded visit reading | no redemption | odometer_at_sale (stated in fleet cancel and transfer rules) | MX(MAX, odometer_at_sale); probe B no visits: 376.89 |
| total-loss unit reading | replacement with no check-in | max(check-in, delivery odometer on its deal) | probe: 488.96 (reading 14, not the retired unit's 12400) |
| total-loss unit deal | cancelled deal on the same vehicle listed first | only delivered or closed deals | status filters; probe: 498.96 = gold |
| addendum unit (delivered fleet agreement) | second delivered agreement | outside the policy (single-agreement scope) | n/a in scope |
| addendum unit | no delivered agreement | outside the policy | n/a |
| transfer replacement (closed fleet agreement) | second closed agreement / move onto another unit | outside the policy (base keeps the odometer) | n/a in scope |
| retail vehicle (delivered deal) | second delivered deal; plan name differs from the replaced plan | outside the policy (base price) | n/a in scope |
| late fees in 12 whole months | 2025-07-18 (15 months, near-miss); month-end 2025-10-31 (11 whole months) | excluded / included | within_months via MONTHS: probe month-end case moves addendum 575.57 -> 596.15 (opening world) |
| vehicle price charges (bonus, trade-up fee) | charge reversed | net of reversals | XCOUNT posted - XCOUNT reversed; probe: bonus 0 -> 468.96 |
| warranty FCM on the unit | voided Factory Basic on C; expired FCM | active FCM on the scoped unit only | variant + status + vehicle filters |
| Factory Basic claims (closing tier b) | coverage of another owner | customer filter applies | CFIELD adds customer_id |
| proxy holding (addendum / retail price) | other plans of the customer | the rule names the plan read (the plan on the most recent signed total-loss request / the replaced plan) | target_holding_id = that plan; a sold-vehicle cancellation earns no total-loss credit |
| request processed later than its date | effective date before today | outside the cancellation policies | n/a |
| refund below 0 / above price | large deductions / credits | floor 0.00 / total-loss cap at purchase_price | MX(0, ...) / MN(price, ...) |

# ROUND 3 (audit revision_2: F-PAYTYPE, F-UNREACH, F-FIRST; task 0 PASS kept)

## Defining-sentence table (XF A4): each rule sentence -> the baseline, the single factor that uses it, or its non-computational role

| policy | sentence (opening words) | owner |
|---|---|---|
| fleet_addendum_price | This policy prices a Kessler Care Fleet 12-Visit plan addendum that a … | unit_basis |
| fleet_addendum_price | For a fleet addendum within this policy's scope, and only for such an … | scoped overwrite (replaced_by) |
| fleet_addendum_price | For the same fleet addendum this policy also replaces the price of a p… | scoped overwrite (replaced_by) |
| fleet_addendum_price | The pricing date is the day the addendum is signed.… | scope / terms (no compute) |
| fleet_addendum_price | A fleet plan addendum is priced from the addendum's basis price, which… | baseline |
| fleet_addendum_price | The fleet addendum price is that basis price rounded half up to the ce… | baseline |
| fleet_addendum_price | Where a rate applies to the addendum it reduces the basis price once; … | assembly / plain |
| fleet_addendum_price | The addendum's basis price follows the factory maintenance coverage of… | unit_basis |
| fleet_addendum_price | The account standing rate reads the customer's service account: a Comm… | account_standing |
| fleet_addendum_price | The new-unit enrollment allowance counts the calendar days from the de… | new_unit_enrollment |
| fleet_addendum_price | The fleet tenure credit counts the whole months from the opening date … | account_tenure |
| fleet_addendum_price | The total-loss replacement credit reads the customer's most recent can… | loss_replacement |
| fleet_addendum_price | The fleet service spend credit adds up the labor and parts amounts cha… | service_spend |
| fleet_addendum_price | The fleet addendum price is fixed only after every Kessler Care plan o… | prerequisite sentence |
| fleet_addendum_price | A fleet plan addendum is not written until every Kessler Care Fleet 12… | prerequisite sentence |
| fleet_addendum_price | The addendum is written for the store on the agreement of the unit bei… | scope / terms (no compute) |
| fleet_cancel_refund | For a Kessler Care Fleet 12-Visit plan cancelled for a reason other th… | scoped overwrite (replaced_by) |
| fleet_cancel_refund | Because the request is processed on its request date, every span this … | scope / terms (no compute) |
| fleet_cancel_refund | The fleet cancellation refund is the plan's purchase_price times the f… | baseline |
| fleet_cancel_refund | The fleet refund share is the plan's unused visits (visits loaded, les… | baseline |
| fleet_cancel_refund | Deductions that apply are subtracted from, and credits that apply are … | assembly / plain |
| fleet_cancel_refund | The fleet refund share depends on how the unit was used: where the uni… | usage_share |
| fleet_cancel_refund | The fleet cancellation fee follows the net terms of the customer's ser… | net_terms_fee |
| fleet_cancel_refund | The filter-visit deduction reads the plan's net visits used (visits re… | filter_visits |
| fleet_cancel_refund | The volume discount recapture rate applies to a plan sold below plan_p… | discount_recapture |
| fleet_cancel_refund | The fleet tenure refund credit counts the whole months from the openin… | fleet_tenure_refund |
| fleet_cancel_refund | The unit service credit counts the labor lines charged with pay type c… | unit_service_history |
| total_loss_refund | For any Kessler Care plan cancelled because its vehicle is a total los… | scoped overwrite (replaced_by) |
| total_loss_refund | Because the request is processed on its request date, every span this … | scope / terms (no compute) |
| total_loss_refund | The total-loss refund is the plan's standard refund rounded half up to… | baseline |
| total_loss_refund | The standard refund is, for a plan whose refund_method is pro_rata_unu… | baseline |
| total_loss_refund | Credits that apply are added to the rounded refund, and the total-loss… | assembly / plain |
| total_loss_refund | The total-loss share method looks at the plan's unit and its Kessler p… | loss_share |
| total_loss_refund | The total-loss courtesy credit reads the customer's service account: a… | loss_courtesy |
| total_loss_refund | The replacement purchase bonus counts the vehicle price charges posted… | replacement_purchase |
| total_loss_refund | The plan relationship credit reads the plan and its unit: a plan sold … | plan_relationship |
| total_loss_refund | The total-loss refund on a plan is worked out only after the plan stan… | prerequisite sentence |
| fleet_transfer_odometer | This policy re-bases a fleet plan whose unit is no longer registered t… | assembly / plain |
| fleet_transfer_odometer | For a Kessler Care Fleet 12-Visit plan moved, within this policy's sco… | scoped overwrite (replaced_by) |
| fleet_transfer_odometer | The moved plan's expiration odometer is the replacement unit's startin… | baseline |
| fleet_transfer_odometer | The miles left are the plan's expiration_odometer less the retired uni… | baseline |
| fleet_transfer_odometer | The retired unit's closing reading is the plan's last recorded visit r… | baseline |
| fleet_transfer_odometer | Mileage allowances that apply are added to that sum.… | scope / terms (no compute) |
| fleet_transfer_odometer | The retired unit's closing reading follows the latest evidence of its … | closing_reading_source |
| fleet_transfer_odometer | The replacement unit's starting reading follows its own records: where… | starting_reading_source |
| fleet_transfer_odometer | The transfer mileage allowance reads the customer's service account: a… | account_transfer_allowance |
| fleet_transfer_odometer | The remaining-visit mileage allowance reads the plan's unused visits (… | unused_visit_allowance |
| fleet_transfer_odometer | The booking-delay allowance counts the calendar days from the replacem… | booking_delay |
| retail_plan_price | This policy prices a replacement purchase: a Kessler Care Essentials, … | retail_basis |
| retail_plan_price | For a replacement purchase within this policy's scope, and only for su… | scoped overwrite (replaced_by) |
| retail_plan_price | The pricing date is the day the plan is signed, and every plan paramet… | scope / terms (no compute) |
| retail_plan_price | A replacement purchase is priced from the retail basis price, which is… | baseline |
| retail_plan_price | The retail plan price is that retail basis price rounded half up to th… | baseline |
| retail_plan_price | Where a rate applies to the plan it reduces the retail basis price onc… | assembly / plain |
| retail_plan_price | The retail basis price follows the factory maintenance coverage of the… | retail_basis |
| retail_plan_price | The Owner Rewards rate reads the customer's service account: Kessler O… | owner_rewards |
| retail_plan_price | The new-owner enrollment allowance counts the calendar days from the d… | new_owner_enrollment |
| retail_plan_price | The trade-cycle credit reads the replaced plan's cancellation entries … | trade_cycle |
| retail_plan_price | The retail plan price is fixed only after every Kessler Care Essential… | prerequisite sentence |
| retail_plan_price | The plan is written for the store on the deal of the vehicle being cov… | scope / terms (no compute) |
| retail_cancel_refund | For a Kessler Care Essentials, Plus or Premium plan cancelled for a re… | scoped overwrite (replaced_by) |
| retail_cancel_refund | Because the request is processed on its request date, every span this … | scope / terms (no compute) |
| retail_cancel_refund | The retail cancellation refund starts from the retail-value amount, wh… | baseline |
| retail_cancel_refund | The fee and any deductions that apply are subtracted from the refund a… | assembly / plain |
| retail_cancel_refund | The retail refund method looks at how the plan was paid for and how mu… | retail_refund_basis |
| retail_cancel_refund | The retail cancellation fee follows the customer's latest vehicle purc… | trade_up_fee |
| retail_cancel_refund | The bundle discount recapture rate applies to a plan sold on a Kessler… | bundle_recapture_rate |
| retail_cancel_refund | The Owner Rewards refund credit reads the customer's service account: … | rewards_refund |

Notes on the table: "scope / terms" sentences carry no quantity; a scope sentence that also selects a record (the
unit being enrolled, the replacement unit, the vehicle being covered) feeds a plain shared binding, never a factor;
"Mileage allowances that apply are added to that sum" is the transfer's generic assembly sentence. No quantity used
by one factor is defined in a baseline sentence, and no factor's quantity is defined outside its own ladder sentence.

## Round-3 changes
- F-PAYTYPE: fleet addendum spend credit and fleet refund unit-service credit filter pay_type = customer_pay in rule and compute (XSUM/XCOUNT eq filter); deductible lines on covered work excluded. Class sweep: every other service-line read counts any line on purpose and says so (check-in odometers: "repair-order check-in"; relationship credit: "at least one repair-order line"; late fees: event type), so no other rule names a pay type.
- F-UNREACH: retail trade_cycle second condition = how the replaced plan was bought (its own purchase_deal_id resolving to a Kessler deal record) -> 50.00 / bought on its own 25.00 / no entry 0. Every tier reachable inside the scope (the scope fixes the vehicle-being-covered deal, not the replaced plan's purchase). Class sweep: P1 (enrollment, standing, tenure, replacement, spend), P2, P3, P4, P6 tiers all reachable inside their scopes (no tier restates a scope condition).
- F-FIRST: "the replaced plan" = the plan named on the customer's most recent signed sold-or-traded request (by request date); a same-date tie, or none, takes the purchase out of the policy.
- Rounding: every rule's rounding sentence says "rounded half up to the cent"; tool docstrings say the same; tool bodies use the pure-Python half-up helper class `_Fmt` (no float round); odometers half-up to whole miles; dates cut to YYYY-MM-DD. (Round 4: the compute's RND now carries the half-up tie offset; see ROUND 4 below — the float-tie residue noted in round 3 is closed.)

## Round-3 probe table (scratch copies of the task worlds)
| read | decoy / edge | rule outcome | probe |
|---|---|---|---|
| P2 unit labor lines | two service_contract_deductible labor lines on the F-250 | not counted | 331.89 (= gold) |
| P1 12-month spend | 4000.00 warranty_deductible labor line | not counted | 575.57 opening world (= unchanged) |
| P5 trade_cycle | replaced plan bought on its own, cancelled today | tier b 25.00 | 294.50 |
| P5 trade_cycle | replaced plan with signed request but no cancellation entry yet (opening) | tier c 0 | 319.50 |
| P5 replaced plan | second same-name plan with an older sold-or-traded request (2026-06-10) | the most recent request names the replaced plan (today's) | holding = KC-305118 -> 269.50 |
| P5 replaced plan | two requests on the same most recent date | outside the policy (base price) | n/a |
| P5 replaced plan's deal | deal record absent (empty purchase_deal_id) | bought on its own | guard -> tier b/c |
| tool bodies | refund 332.025 / price 0.125 | half up | 332.03 / 0.13 |
Previous rounds' probe rows (plan.md ROUND 2 table) re-run unchanged: reinstated visit 376.89, no redemptions 376.89, replacement without check-in 488.96, cancelled deal first 498.96, reversed vehicle price 468.96, month-end late fee 596.15.

# ROUND 4 (audit revision_3: F-HALFUP; both tasks PASS, nothing else changed)
- Every money RND in compute is now RND(x + 0.000000001, 2), so it matches the rules' "rounded half up to the cent" at exact half-cent ties:
  - P1 result
  - P2 share_amount, recapture_amount, result
  - P3 standard_refund (both branches), loss_refund (both branches), result
  - P5 result
  - P6 basis_day_amount, method_amount (pro rata), bundle_recapture, result
- The offset is far below one cent. Every amount it rounds is non-negative, or sits inside MX(0, ...) where the floor makes the side of a negative value irrelevant. P4 keeps int() "in whole miles" on integer inputs. Tool bodies keep the _Fmt half-up helper.
- Exact-tie probe (task 1 world with a 4th visit used): pro rata 664.05 x 4/8 = 332.025 -> 332.03 (float round gave 332.02); refund 338.05 = rule.
- Gates re-run: COMPUTE OK with every expected, baseline and factor_sensitivity figure unchanged (gold 43130, 498.96, 331.89, 515.57, 421.05, 269.50).
- Zero-amount edges (recipe 19): the only waits on writes are the two cancellation edges (P1 <- P3, P1 <- P2 gate, P5 <- P6) and the move (P3 <- P4). A refund calculation of 0.00 is a legal maintenance row ("0.00 when the computation yields no refund"), and the tools refuse nothing, so a 0.00 refund still books the cancellation the wait reads. The move's computation is an odometer, never a money row. No wait can stall on a refused 0.00 write.
- Round-2/3 probe rows unchanged: none of their figures sits on a tie.

# ROUND 5 (audit revision_4: F-EPS; both tasks PASS, nothing else changed)
- Coordinator ruling applied at all 12 money rounding points, the same members as in ROUND 4: RND(x + 0.000000001, 2).
- The 1e-9 offset is above float error and below the spacing of any decimal with at most 8 places, so exact ties round up and finite-decimal non-ties stay put.
  - Probes: 332.025 -> 332.03 (tie); the auditor's 526.9849996 -> 526.98 (non-tie, now equal to the rule); 434.2105 -> 434.21.
- Distance check: gold was replayed for both tasks. Every RND argument behind the scored, baseline and factor-sensitivity figures sits at least 0.00139 from a half cent, well over the 1e-6 bound.
- Values within 1e-9 below a half cent are DSL-KNOWN residue under the ruling.
- Zero-amount ruling:
  - No floor creates an amount where the rule owes nothing: the only floors are MX(0, ...) on refunds, and P3 caps at purchase_price.
  - The waits on the cancellation writes (P1 <- P3, P1 <- P2 gate, P5 <- P6) read the cancellation status/entry, which the cancellation books even at a 0.00 refund. That is a legal row in the schema, and no tool refuses it, so nothing in a wait depends on a refusable 0.00 write and no carve-out is needed.
- Gates re-run 7/7; gold unchanged (43130, 498.96, 331.89, 515.57, 421.05, 269.50).

# ROUND 6 (render scan F1-F5; both tasks PASS, gold unchanged)
- F1 (and class): the fleet addendum and retail plan prices take the rate once, then subtract the credits, then floor a result below 0.00 at 0.00, then round half up at the end. Compute: RND(MX(0, x) + 1e-9, 2). The floor creates no amount where nothing is owed. Class sweep: only these two prices subtract credits; every refund already floors.
- F2: the total-loss refund adds credits to the rounded refund, then floors at 0.00, then caps at purchase_price, in that order at the end. This matches the existing compute MN(price, MX(0, RND(...))). Siblings already say "floored at 0.00 at the end".
- F3: the replacement credit now reads the total-loss cancellation entry of the plan named on the customer's most recent signed total-loss request (by request date, then registration time). That is a record test, and the plan it names is the computation's holding. Class sweep: the retail price already names the replaced plan; every other policy reads its own plan.
- F4 (and class): every overwrite now restates the in-force outcome outside its scope, and "the base price" is no longer used:
  - fleet addendum: plan_price_usd less fleet_volume_discount_pct at the threshold;
  - fleet cancel: base pro rata less the fee;
  - total loss: refund_method with no fee;
  - retail cancel: retail value less the fee.
  - The retail price and transfer overwrites already did this.
- F5: last_visit_reading joined the usage_share bindings.
- F5 class sweep (mechanical): every remaining plain binding that only one factor reads is one of two kinds:
  - That factor's baseline quantity, defined in baseline.rule: P2 visit_share, P3 standard_refund, P6 retail_value_amount, P4 last_visit_reading and rep_delivery_odometer.
  - The scope's record selection: P4 rep_vehicle, from the scope sentence "the unit delivered on the customer's single ... agreement".
- No factor reads another factor's binding.
- Probes re-run on scratch copies: gold, baseline and sensitivity figures are unchanged (COMPUTE OK). F1 probe (replaced plan Essentials 2-Visit, ToyotaCare vehicle with 25000-mile limit, credits 80.00 exceeding the reduced price): 0.00 before and after the cancellation, never negative.

# ROUND 7 (seed-only cross-product pass: S-0a, S-0b, S-1a; charter and tools byte-identical)
- S-0a: RO 362877 now carries its early-payment discount: a credit of 4.17 against labor line A on 2026-09-30.
  - Basis: 3.0% of 139.13; paid in full by ACH 15 days after the invoice, inside the window.
  - The open balance is now 672.60.
  - Same class swept: RO 364520 was paid 23 days after its invoice and RO 361902 was paid late, so neither is owed a discount; RO 363114 is unpaid. Task 1 has no repair orders.
- S-0b: KCV-26-30418 now carries its full ledger, reconciling to a balance of 0.00 at closing:
  - deposit 2500.00 ACH, 2026-07-29;
  - contract-date postings on 2026-08-06: vehicle price 52480.00, filing 18.00, sales tax 3936.00, title/registration 85.50;
  - deposit applied 2026-08-12;
  - payment 54019.50 ACH, 2026-09-08.
  - Its trade-in fields are cleared: no published rule posts a positive trade allowance, and nothing reads them.
  - Same class: the Tacoma ledger and the Highlander ledger were already complete. The 2023 RAV4 deal's ledger is unread residue, outside every window.
- S-1a: KTD-23-30962 hold_expires_date changed 2023-03-18 -> 2023-03-16. Same class: every other hold is correct (Tacoma 10-08, Transit 08-12, Highlander 10-06).
- Probes on the patched worlds:
  - replacement-purchase bonus: 1 net charge within 1 month and 2 within 3 months, so it stays 30.00;
  - relationship lines on C: 6 (was 5), so it stays 10.00;
  - spend: labor/parts only, so it stays 1082.63.
- COMPUTE OK. Every scored, baseline and sensitivity figure is unchanged.
