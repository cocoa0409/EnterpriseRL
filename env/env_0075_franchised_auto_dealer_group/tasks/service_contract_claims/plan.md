# service_contract_claims — instantiation plan (env_0075, category vsc, M=2)

Draw (draw_counts.py --tasks 2):
- task 0: prerequisite_problems=2, factor_counts=[5, 6, 4]
- task 1: prerequisite_problems=2, factor_counts=[5, 6, 5]

## Architecture (why this shape)
- The only customer-owned write in this charter is the holder's signed cancellation (lifecycle
  active->cancelled `by: user`; the cancellation triggers `vsc:vsc_refund_calculated` in base).
  So each task's owner=user problem is the holder's own cancellation, booked by one user tool that
  records the signed request, moves the contract to cancelled and books the triggered refund
  calculation (the scored amount). Two user tools, split by an exact record test on the reason
  the holder states (task 0: holder keeps the vehicle `customer_request`; task 1: `total_loss`).
- Claim writes are the agent's: a component line that re-decides a wrong denial (the holder paid
  on customer pay, so every input is on the service repair-order lines), a rental line, and an
  audit recovery (partial reversal) of an overpaid line.
- A claim can only be paid on an active contract, so every claim the contract owes must be booked
  before the cancellation (state-form prerequisite sentences on the refund side).

## Trees
Task 0 (Quintero, 2022 Honda CR-V, Kessler Shield Select sold on the deal, 58 days old):
- R0 `vsc_ext_kept_vehicle_refund` (user, 6 factors) — root
- B0 `vsc_ext_waiting_denial_reimbursement` (agent, 5 factors) — A/C repair denied for the
  waiting period although the contract was sold on the purchase deal; holder paid it.
- A0 `vsc_ext_rental_reimbursement` (agent, 4 factors) — loaner days the holder paid on that claim.
- edges: R0<-B0 value_input (free look needs no claim paid; fee tier), A0<-B0 state_gate
  (rental only with a paid component line under the same claim number), R0<-A0 state_gate.
Task 1 (total loss, Powertrain-family contract near its aggregate limit):
- R1 `vsc_ext_total_loss_refund` (user, 6) — root
- B1 `vsc_ext_maintenance_denial_reimbursement` (agent, 5) — lubricated repair denied for lack
  of maintenance that Kessler Care visits disprove; holder paid it.
- V1 `vsc_ext_overpaid_line_recovery` (agent, 5) — audit recovery of an overpaid earlier line.
- edges: B1<-V1 value_input (remaining aggregate limit), R1<-B1 state_gate.

(Factor tables, all-pairs method tables, T1/T2 tests, probe tables and the event list are kept
in the sections below and in each task's design_rationale; updated as the policies land.)

## Events written by task tools (base triggers)
- vsc_claim_paid (component_repair / rental): triggers [] (base) — stays in vsc.
- vsc_claim_reversed: triggers [] — stays in vsc.
- vsc_contract_cancelled: triggers vsc:vsc_refund_calculated (within category) — the user tool
  books that refund calculation row in the same call, as base says.
- vsc_refund_calculated: triggers [].
- No tool writes any other category.

## Scratch
/tmp/service_contract_claims_0075/ (authoring scripts; deleted before finishing).

## Resume (fresh relaunch, 2026-10-22) — design adopted; task-0 world re-tuned (see worklog)
Task 0 final: B0 = vsc_ext_waiting_denial_reimbursement (6 factors), A0 = vsc_ext_claim_rental_reimbursement (4),
R0 = vsc_ext_kept_vehicle_refund (5) -> multiset [6,4,5] = draw [5,6,4]. Holder Marcus Quintero, 2021 Hyundai Santa Fe,
Kessler Shield Exclusionary KS-4418263 sold 2026-08-21 on deal KHR-26-41087 (delivered 2026-08-28), frozen 2026-10-21.

### Task 0 factor table (tier taken / T1 = result with that factor's baseline alone; expected B0 1667.15, A0 45.00, R0 3780.75)
| policy | factor | effect | tier taken (evidence) | T1 | T2 (producible world where it alone moves result, others at baseline) |
|---|---|---|---|---|---|
| B0 | covered_labor_basis | method | T1 charged 482.76 < list 536.40 (Gold 10% labor discount, RO 446215 line A) | 1720.79 | any Gold/Silver/Platinum holder with a discounted labor row |
| B0 | covered_parts_basis | parameter | T1 charged 1151.78 < list 1212.40 (Gold 5%) | 1727.77 | Gold/Platinum holder, parts on the covered line |
| B0 | diagnostic_credit_share | parameter | T1 credited in full (diagnostic_applied_to_repair 149.00) | 1816.15 | Silver holder (50% credit) -> tier 2 alone |
| B0 | visit_deductible_rule | method | T1 RO at KHR = selling store, Exclusionary disappearing deductible | 1567.15 | per-visit level off the selling store with a contract deductible already billed on the RO -> tier 2 (100 - 100 = 0) alone |
| B0 | shop_supplies_share | method | T2 supplies 39.43, other customer-pay labor on line B -> 39.43 x 482.76/657.09 = 28.97 | 1638.18 | any RO with a supplies fee |
| B0 | hazwaste_fee_share | method | T2 air_conditioning, other labor -> 4.95 x 482.76/657.09 = 3.64 | 1663.51 | cooling repair with a hazardous-waste fee |
| A0 | rental_window_start | method | T2 loaner out 09-08 = diagnosis day, claim line denied 09-09 -> start 09-09 | 90.00 | loaner out the day after diagnosis -> tier 1 alone |
| A0 | rental_window_end | method | T2 loaner back 09-14 not before line A last labor 09-13; 09-13 < RO last labor 09-14 -> end 09-13 | 90.00 | loaner returned before line A finished -> tier 1 |
| A0 | free_courtesy_days | parameter | T1 dealer_courtesy, Courtesy Loaner - Compact 3 days + 1 bonus, Gold active | 225.00 | non-rewards holder on a courtesy loaner -> tier 2 |
| A0 | rental_day_amount | parameter | T2 charged daily_rental 45.00 < Exclusionary 50.00 | 50.00 | service_contract_allowance loaner with 40.00 allowance -> tier 1 |
| R0 | mileage_reading_tier | parameter | T2 RO odometer 41590 not above certified 42950 (near-miss); Kessler Care visit 2026-10-20 at 42996 above it | 3781.95 | holder certifies below a later RO reading -> tier 1 |
| R0 | term_miles_start | parameter | T1 deal delivered 08-28 after sale 08-21, delivery odometer 41236 > 41180 | 3777.11 | home-delivered deal -> tier 2 |
| R0 | elapsed_term_measure | method | T1 Kessler Shield Exclusionary contract form: 61 days -> whole 30-day periods 60 | 3779.81 | Preferred/Select contract -> tier 2 (started period counts whole) |
| R0 | unusable_days_credit | parameter | T1 delivered 7 days after sale -> 7 credited days | 3767.02 | standalone contract -> 30 waiting days credited |
| R0 | cancel_fee_standing | parameter | T1 54 days from delivery <= 60 and latest denied line (CLM-4471208) later paid (after B0) | 3730.75 | (multi-source) cancellation with no re-decided denial and an active Kessler Care plan -> tier 2 |
All-baseline: B0 1797.80, A0 350.00, R0 3714.88 (each != expected). Lesser-of shape (R0): time share 0.970975 vs mileage share 0.970667 sit 0.0003 apart, so every time-side and mileage-side factor flips the min on its own (A.6 min-of-caps T1/T2 both shown).
Multi-source: visit_deductible_rule T1 (store record AND tier param), free_courtesy_days T1 (loaner basis AND rewards account), cancel_fee_standing T1 (date window AND ledger re-decision). Cross-difficulty: service (B0 all, A0 end/free days), loaner (A0), purchase/maintenance (R0).

### Method factors — all-pairs (distinguishing input per pair)
- covered_labor_basis: T1 min(charged labor, standard) | T2 min(list labor - comeback credit, standard) | T3 standard (hours x capped rate). T1/T2: charged amount vs list amount + comeback credit; T1/T3: charged amount + min pick; T2/T3: comeback credit subtraction + min pick.
- visit_deductible_rule (round 2): T1 none | T2 deductible less contract deductibles the store billed on the RO, floor 0 | T3 deductible once. T1/T2, T1/T3: T2/T3 > 0 when nothing was billed; T2/T3: the billed-deductible input (an added operand).
- rental_window_start: T1 loaner out_date | T2 date of the claim's latest denial | T3 diagnosis line date — three different records.
- rental_window_end: T1 loaner return_date | T2 covered line's last labor date | T3 RO's last labor date — three different records.
- elapsed_term_measure (round 2, contract form): T1 floor(days/30) x 30 | T2 ceil(days/30) x 30 | T3 days. T1/T2: floor vs ceiling of the same count (61 -> 60 vs 90); T1/T3 and T2/T3: the rounding operation.
Factor independence: no factor binding reads another factor's binding (shared selections ro, covered_line, labor_charged, ro_labor_all, standard_labor, diag_day, loaner_basis, delivered_late, deal_delivery, request_day, certified are plain bindings).

### Probe table (task-0 reads)
| read | decoy / edge | outcome |
|---|---|---|
| B0 waiting denials / denied claim / ro / group (LATEST on this contract) | second contract of the customer | SUM/COUNT/LATEST are holding-scoped |
| " | paid component line on same claim | already_repaid=1 -> 0.00 (paid once) |
| " | standalone contract (purchase_deal_id empty) | sold_on_deal=0 -> 0.00 (out of scope) |
| " | two unpaid waiting denials | only the latest is priced per call; accepted DSL residue (worlds seed one) |
| B0 covered_line (diag fee line) | line B rows, payment/points rows | excluded by line_letter / event_type |
| B0 XSUMs on RO 446215 | RO 447318 (plan visit) | no service rows (plan work is never billed in service) |
| B0 supplies/hazwaste proportion | ro_labor_all = 0 | guarded: proportion branch only when ro_labor_all > labor_charged >= 0 |
| A0 claim/ro (LATEST paid component line) | earlier paid claim | latest entry_date wins; B0 row is dated frozen day |
| A0 loaner CFIELDs keyed repair_order_number | none on RO | None -> start/end fall to diag/RO dates, free days 0, day amount tier 3 |
| A0 account tier/status | closed second service account | keyed status='active' |
| A0 charged rate | no daily_rental charge | None -> tier 3 |
| R0 request (submitted, customer_request) | declined earlier request | filtered by request_status |
| R0 ro_reading (vehicle_id) | other vehicle's ROs | filtered by vehicle_id; RO below certified -> near-miss |
| R0 visit_reading | none / plan absent | None -> tier 3 certified |
| R0 deal reads | standalone (no deal) | None -> run_from tier 3, credited tier 2 |
| R0 plan_status | cancelled plan on vehicle | keyed status='active' |
| R0 DAYS(window_from, request) | request before delivery (negative lag) | counts as within window (<= 60) |
| R0 MONTHS | month-end | MONTHS() whole calendar months; 08-21 -> 10-21 = 2 |

### Events written (base triggers)
- reimburse_waiting_denial_repair_5808cf06 -> vsc_claim_paid (component_repair) — triggers [] .
- pay_claim_rental_line_3f5378a0 -> vsc_claim_paid (rental) — triggers [] .
- accept_kept_vehicle_cancellation_d270783c -> vsc_contract_cancelled (triggers vsc:vsc_refund_calculated, booked in the same call) + vsc_refund_calculated (triggers []) + request completed.

## Task 1 — design (resume; draw prerequisite_problems=2, factor_counts=[5,6,5])
Predecessor sketch (B1 maintenance re-decision + V1 partial overpayment recovery + total-loss refund) re-examined:
- V1 dropped: base reverses a line paid in error IN FULL (the reverse_once gate sentence), and a partial audit recovery only
  supports 4 record-backed 3-tier ladders (rate ceiling, manufacturer contribution, visit deductible, hours) — 5 cannot be
  reached without an invented or padded ladder (XF A.4/F.22).
- Total-loss root dropped for a traded-vehicle root: total loss has the fee waived by base, leaving 2 loss-specific
  ladders; a trade at a group store gives three record-backed ones (measure day = trade date, reading = trade
  appraisal odometer, loyalty fee).
Final tree (vehicle 2020 Honda Pilot bought used at KTD on a deal with a Kessler Shield Exclusionary; RO at KHB, Silver):
- R1 vsc_ext_traded_vehicle_refund (user, 5 factors) — root; cancel_reason vehicle_sold_or_traded.
- B1 vsc_ext_maintenance_denial_reimbursement (agent, 6) — engine line denied lack_of_maintenance although Kessler Care
  visits fall inside the 12-month look-back; holder paid on customer pay.
- C1 vsc_ext_coverage_denial_reimbursement (agent, 5) — cooling line of the same RO denied component_not_covered although
  the coverage level covers cooling; holder paid.
- Edges: R1 -> B1 state_gate (state form); B1 -> C1 value_input on B1's deductible (per-visit deductible taken once per
  repair visit, base vsc_msr_deductibles_on_visit: the line settled first takes it; B1's sentence pins C1 first).
- No loaner on the RO (A0 must not be lit), no waiting-period denial (B0 not lit), request reason not customer_request (R0 not lit).

### Task 1 final (frozen 2026-10-22 10:05 EDT): Gabriel Navarro, 2020 Honda Pilot, KS-4426107 Exclusionary sold 2024-04-12 at KHB
C1 = vsc_ext_coverage_denial_reimbursement (5), B1 = vsc_ext_maintenance_denial_reimbursement (6), R1 = vsc_ext_traded_vehicle_refund (5)
-> multiset [5,6,5] = draw. Edges R1->B1 value_input (redecided_count), R1->C1 state_gate. Gold: C1 1080.91, B1 6783.37, R1 2035.27.

| policy | factor | effect | tier taken (evidence) | T1 | T2 (alone moves result, others at baseline) |
|---|---|---|---|---|---|
| C1 | cover_labor_rule | method | T1 RO 446908 labor charged 506.54 < list 533.20 (Silver 5%) | 1107.57 | comeback-credited line -> tier 2 |
| C1 | cover_parts_rule | parameter | T2 goodwill 45.00 on the line | 1125.91 | Gold holder (5% parts discount) -> tier 1 |
| C1 | cover_diag_share | parameter | T1 diagnostic credited 50% | 1166.91 | Gold holder (100% credit) -> tier 2 |
| C1 | cover_supplies_share | method | T1 only line A labor -> whole 40.52 | 1040.39 | RO with another concern line -> tier 2 |
| C1 | cover_waste_share | method | T1 cooling, only line A -> whole 4.95 | 1075.96 | A/C repair with other labor -> tier 2 |
| B1 | lube_labor_rule | method | T1 charged 2333.92 < list 2373.60 | 6823.05 | comeback credit -> tier 2 |
| B1 | lube_parts_rule | parameter | T2 goodwill 100.00 | 6883.37 | Platinum holder parts discount -> tier 1 |
| B1 | lube_diag_share | parameter | T1 50% credit | 6869.37 | full credit -> tier 2 |
| B1 | lube_visit_deductible | method | T1 RO at selling store KHB + disappearing deductible | 6683.37 | per-visit level off the selling store with a billed contract deductible -> tier 2 |
| B1 | lube_supplies_share | method | T2 49.95 x 2333.92/2530.00 = 46.08 | 6737.29 | single-line RO -> tier 1 |
| B1 | lube_waste_share | method | T2 4.95 x 2333.92/2530.00 = 4.57 | 6778.80 | single-line RO -> tier 1 |
| R1 | trade_measure_day | method | T1 (round 3) Kessler Care plan sold on the deal: sold-or-traded refund calculation 2026-09-28 | 1990.94 | no plan cancellation, GAP loan payoff recorded -> tier 2 |
| R1 | trade_reading | parameter | T1 (round 3) plan cancellation odometer 73684 > certified 73520 (near-miss RO 71700) | 2036.88 | no plan cancellation, RO above certified -> tier 2 |
| R1 | trade_miles_start | parameter | T1 delivered 2024-04-16 at 36893 > 36850 | 2032.98 | home-delivered deal -> tier 2 |
| R1 | trade_credit_days | parameter | T1 4 days sale-to-delivery | 2028.13 | standalone contract -> waiting days |
| R1 | trade_fee_rule | parameter | T1 latest denial (CLM-4452086) repaid -> 0.00 | 1985.27 | Silver holder, no re-decided denial -> 25.00 |
All-baseline: C1 1193.10, B1 6858.40, R1 1932.19. R1 lesser-of: time 0.509858 vs mileage 0.509453 (0.0004 apart; each side's factor flips/moves the min alone).
Multi-source: lube_visit_deductible T1 (store record AND coverage switch), trade_measure_day T1 (trade deal AND contract sale date AND request date).
Cross-difficulty: service (C1, B1 all; trade_fee_rule), purchase (trade_measure_day, trade_reading, trade_miles_start), maintenance (B1 scope, R1 measure-day tier 2).

### Method factors — all-pairs (task 1)
- cover_labor_rule / lube_labor_rule: T1 min(charged labor, standard) | T2 min(list - comeback credit, standard) | T3 standard. Pairs as task 0's covered_labor_basis (charged amount; comeback credit; min pick).
- lube_visit_deductible (round 2): T1 none | T2 deductible less contract deductibles billed on the RO, floor 0 | T3 deductible once.
- trade_measure_day: T1 new-vehicle deal contract date | T2 plan sold-or-traded cancellation date | T3 effective date — three different records.

### Probe table (task 1 reads)
| read | decoy / edge | outcome |
|---|---|---|
| C1 denial scope | denial of a group the level does not cover | group_switch_on 0 -> 0.00 (out of scope) |
| B1 denial scope | transmission/drive-axle/engine only; latest plan visit after the RO | visit_day > diagnosis -> out of scope (DSL keeps the latest visit only; world: no visit after RO 447652) |
| B1 visit window | MONTHS whole-month count; visit exactly 12 months before | MONTHS = 12 not < 12 -> out of scope (stated "fewer than ... whole calendar months") |
| C1 deductible (base, plain) | per-visit level with another paid line on the RO that took a deductible | visit_deductibles > 0 -> none (base measure; reimbursement tools record deductible_applied 0, audit O11) |
| reimbursement XSUMs | line B rows on RO 447652 | excluded by line_letter; used only as 'other labor' in fee shares |
| R1 trade deal (CFIELD variant New Vehicle Retail Purchase) | original used deal; a new-vehicle deal before the sale date or after the request | variant filter / date tests -> tier fails |
| R1 appraisal odometer | deal without appraisal ('' ) | guarded != '' -> next tier |
| R1 RO reading | other vehicle's ROs | vehicle_id filter; RO 71700 below certified (near-miss) |
| R1 plan cancellation | none / other reasons | cancel_reason filter -> None -> tier 3 |
| R1 fee | latest denial not repaid; account closed | status='active' keyed read; coverage-level fee |
| A0 (task 0) in task-1 world | paid component lines but no loaner | on_loaner guard -> 0.00 (not lit) |

### Events written (task 1)
- reimburse_coverage_denial_repair_73971dca / reimburse_maintenance_denial_repair_6315e699 -> vsc_claim_paid (component_repair) — triggers [].
- accept_traded_vehicle_cancellation_f71aca80 -> vsc_contract_cancelled (-> vsc:vsc_refund_calculated booked in the same call) + vsc_refund_calculated — triggers []. No tool writes another category.

## Round 2 (audit revision_1) — what changed and the re-probe
Earlier probe tables above are superseded where they conflict with this section.

### Read / anchor probe table (round 2; every read of the charter)
| read | decoy / edge | rule (round 2) | compute |
|---|---|---|---|
| re-decision line selection (waiting, maintenance, coverage) | two denials of one reason; same-day tie | latest by decision date, first in the claim history on a tie; older line out of scope | LATEST keeps the first row on a tie |
| re-decision already-repaid | latest line repaid, an older one not | 0.00 (latest only) | probe P1 -> 0.00 |
| covered concern line | second diagnosed concern line on the RO | out of scope (exactly one diagnosed line) | P6 -> 0.00 |
| coverage switch / lubricated groups | Powertrain A/C waiting denial; engine 'not covered' denial | out of scope | C7a -> 0.00; C7b -> 0.00 |
| prior authorization | covered-line labor closed before the decision date | out of scope (repair taken as begun before the claim number) | C7c -> 0.00 |
| term / waiting period | RO after expiration or above expiration odometer; waiting not over on a standalone contract | out of scope | in_term / waiting_over guards |
| customer-pay repair | declined repair; labor wholly credited back as a comeback | out of scope | labor_charged - comeback_credit > 0 guard (round 3) |
| deductible (waiting, maintenance) | per-visit off the selling store, nothing billed / a contract deductible billed / per-repair level | 100 / 0 / 100 | 100.0 / 0.0 / 100.0 |
| maintenance proof visit | visit after the failure; latest visit reinstated; second plan on the vehicle | latest non-reinstated visit of the plan sold on the contract's deal (round 3) must precede the diagnosis | C4.2 -> 0.00; plan keyed by purchase_deal_id |
| kept reading | older plan on the vehicle; reinstated visit; payment on another RO posted later | plan sold on the contract's deal (round 3); not reinstated; RO whose labor closed last, same-day tie first listed | 42996.0; 42950.0; 41590 |
| rental claim / agreement | several claims; second agreement on the RO; no daily-rental charge; window inside free days; Powertrain | (round 3) the claim of the latest component-repair line, paid or denied, with a paid component line; first-listed agreement charged daily rental; (round 4: no floor; a 0-day rental is carved out of the kept wait); no rental benefit | see round-3 probes |
| traded trade deal | (round 3) no longer read: no record ties a trade-in appraisal to the covered vehicle | — | C4r.1 probe |
| plan cancellation (traded, round 3 tier 1) | own-request cancellation listed first; second plan | plan sold on the contract's deal; refund calculation keyed on cancel_reason vehicle_sold_or_traded; latest, first listed on a tie | C4r.2 probe |
| fee 'latest denied line' | same-day denials | first in the claim history | LATEST tie rule stated |
| month counts | look-back MONTHS convention | stated: calendar-month difference less one where the later day-of-month is earlier | MONTHS() |
| zero / None / negative | ro_labor_all 0, absent reads, start after end | guarded shares; None -> fall-through; MX(0, ...) | clean |

Probe run (scratch probes.py over check_compute.build_env):
    P1 two waiting denials, latest repaid: 0.0 (rule: 0.00: scope is the latest denial only)
    P6 second diagnosed concern line: 0.0 (rule: 0.00: exactly one diagnosed line required)
    C7a Powertrain (no A/C cover) waiting denial: 0.0 (rule: 0.00: switch false)
    C7c labor closed before the decision: 0.0 (rule: 0.00: repair taken as begun before the claim number)
    C1 per-visit off selling store, nothing billed: 100.0 (rule: 100.0 (tier 2: 100 - 0))
    C1 per-visit, store already billed a contract deductible: 0.0 (rule: 0.0 (tier 2: 100 - 100))
    C1 per-repair level: 100.0 (rule: 100.0 once (tier 3))
    C6.1 loaner back 09-11 (window <= free days), holder charged: 45.0 (rule: >= 1 day: 45.00)   [round 4: floor removed; this world now computes 0.00 and the kept wait carves it out]
    C6.1 no daily-rental charge: 0.0 (rule: 0.00 and the kept wait does not name the claim)
    C6.1 Powertrain (no rental benefit): 0.0 (rule: 0.00 and the kept wait excludes levels with no rental benefit)
    C4.3 older fulfilled plan listed first (kept reading): 42996.0 (rule: 42996.0 from the active plan)
    C4.2 latest visit reinstated (kept reading): 42950.0 (rule: 42950.0 certified)
    C4.7 payment on another RO posted later (kept RO reading): 41590 (rule: 41590 (labor closed last))
    C4.2 visit after the failure (maintenance scope): 0.0 (rule: 0.00: the latest visit must precede the diagnosis)
    C7b engine line denied as not covered: 0.0 (rule: 0.00: lubricated groups are out of the coverage scope)
    C4.4 cancelled NVRP deal listed first (traded): 2035.27 (rule: 2035.27 unchanged)

### Recipe A4 — defining-sentence table (round 2, superseded by the round-3 table below; each rule sentence -> the baseline or the single factor that uses it)
| policy | # | sentence opens | role | bindings quoting it |
|---|---|---|---|---|
| waiting_denial_reimbursement | 0 | This policy applies to the contract's latest component repair line den... | scope (record tests; plain bindings) | sold_on_deal, waiting_denials, denied_claim, already_repaid, ro, denied_group, deny_day, deny_odometer, group_switch_on, ro_diag_day, diag_lines, in_term, lube_group, labor_close_day, begun_after_claim |
| waiting_denial_reimbursement | 1 | For a waiting-period re-decision line, the covered concern line is the... | assembly / plain selection | covered_line, labor_charged |
| waiting_denial_reimbursement | 2 | The standard waiting-period re-decision reimbursement is the covered c... | baseline (computation document) | labor_hours_billed, posted_rate, standard_labor, deductible_chosen |
| waiting_denial_reimbursement | 3 | For a waiting-period re-decision line, and only for such a line, the l... | factor covered_labor_basis | labor_list, comeback_credit, labor_reimbursed |
| waiting_denial_reimbursement | 4 | For a waiting-period re-decision line, and only for such a line, the p... | factor covered_parts_basis | parts_list, parts_charged, goodwill_credit, parts_reimbursed |
| waiting_denial_reimbursement | 5 | For a waiting-period re-decision line, and only for such a line, the d... | factor diagnostic_credit_share | diag_fee, diag_credit, diag_reimbursed |
| waiting_denial_reimbursement | 6 | For a waiting-period re-decision line, and only for such a line, the d... | factor visit_deductible_rule | ro_store, deductible_taken, billed_deductibles |
| waiting_denial_reimbursement | 7 | For a waiting-period re-decision line, the shop supplies fee reimburse... | factor shop_supplies_share | ro_labor_all, supplies_fee, supplies_reimbursed |
| waiting_denial_reimbursement | 8 | For a waiting-period re-decision line, the hazardous-waste fee reimbur... | factor hazwaste_fee_share | hazwaste_fee, hazwaste_reimbursed |
| waiting_denial_reimbursement | 9 | For a waiting-period re-decision line, and only for such a line, every... | assembly / plain selection | claims_net, limit_left, result |
| claim_rental_reimbursement | 0 | This policy applies to the rental benefit of the claim of the contract... | scope (record tests; plain bindings) | claim, ro, repair_paid, rental_agreement, charged_rental_days |
| claim_rental_reimbursement | 1 | A rental line is booked only after the records carry a paid component-... | prerequisite sentence (wait on vsc_ext_waiting_denial_reimbursement) |  |
| claim_rental_reimbursement | 2 | The standard rental is the coverage level's rental amount per day time... | baseline (computation document) | diag_day, ro_last |
| claim_rental_reimbursement | 3 | Rental days are counted from a start day: where the loaner went out af... | factor rental_window_start | loaner_out, denial_day, start_day |
| claim_rental_reimbursement | 4 | Rental days are counted to an end day: where the loaner came back befo... | factor rental_window_end | covered_line, loaner_back, covered_last, end_day, ro_diag_lines |
| claim_rental_reimbursement | 5 | Days the store gave free are not reimbursed: where the loaner was a de... | factor free_courtesy_days | loaner_basis, courtesy_days, bonus_days, account_tier, account_status, free_days |
| claim_rental_reimbursement | 6 | The amount per day follows what the loaner cost: where the loaner was ... | factor rental_day_amount | loaner_id, charged_rate, allowance, day_amount |
| claim_rental_reimbursement | 7 | For a rental line this policy pays, and only for such a line, the days... | assembly / plain selection | days_counted, days_already, days_paid, claims_net, limit_left, result |
| kept_vehicle_refund | 0 | This policy applies to a contract its holder cancels while keeping the... | scope (record tests; plain bindings) | request_day, certified |
| kept_vehicle_refund | 1 | The refund on such a cancellation is fixed only after the records carr... | prerequisite sentence (wait on vsc_ext_waiting_denial_reimbursement) |  |
| kept_vehicle_refund | 2 | The refund on such a cancellation is not computed until the claim of t... | prerequisite sentence (wait on vsc_ext_claim_rental_reimbursement) |  |
| kept_vehicle_refund | 3 | For a kept-vehicle refund, a contract cancelled within the coverage le... | assembly / plain selection | claims_net, deal_status, flat_look |
| kept_vehicle_refund | 4 | The standard kept-vehicle refund is the retail price times the unused ... | baseline (computation document) |  |
| kept_vehicle_refund | 5 | For a kept-vehicle refund, the unused mileage share is measured at a r... | factor mileage_reading_tier | ro_reading, plan_id, visit_reading, reading, visit_entry, visit_reinstated |
| kept_vehicle_refund | 6 | For a kept-vehicle refund, the term miles run from a starting odometer... | factor term_miles_start | deal_delivery, delivered_late, deal_odometer, deal_method, deal_distance, run_from |
| kept_vehicle_refund | 7 | For a kept-vehicle refund, the elapsed days of the term, the calendar ... | factor elapsed_term_measure | elapsed_days, elapsed_measured |
| kept_vehicle_refund | 8 | For a kept-vehicle refund, days of the term the holder could not use a... | factor unusable_days_credit | credited_days |
| kept_vehicle_refund | 9 | For a kept-vehicle refund, the cancellation fee follows how the cancel... | factor cancel_fee_standing | window_from, denied_claim, redecided_count, plan_status, cancel_fee |
| kept_vehicle_refund | 10 | For a kept-vehicle refund, and only for such a refund, the unused shar... | assembly / plain selection | mileage_share, term_days, used_days, time_share, unused_share |
| kept_vehicle_refund | 11 | For a kept-vehicle refund, and only for such a refund, the pro-rata re... | assembly / plain selection | result |
| maintenance_denial_reimbursement | 0 | This policy applies to the contract's latest component repair line den... | scope (record tests; plain bindings) | maint_denials, denied_claim, already_repaid, ro, denied_group, lube_group, ro_diag_day, plan_id, visit_day, visit_proof, visit_entry, visit_reinstated, deny_day, deny_odometer, group_switch_on, diag_lines, in_term, waiting_over, labor_close_day, begun_after_claim |
| maintenance_denial_reimbursement | 1 | For a maintenance re-decision line, the repaired concern line is the c... | assembly / plain selection | covered_line, labor_charged |
| maintenance_denial_reimbursement | 2 | The standard maintenance re-decision repayment is the repaired concern... | baseline (computation document) | labor_hours_billed, posted_rate, standard_labor, deductible_chosen |
| maintenance_denial_reimbursement | 3 | For a maintenance re-decision line, and only for such a line, the labo... | factor lube_labor_rule | labor_list, comeback_credit, labor_repaid |
| maintenance_denial_reimbursement | 4 | For a maintenance re-decision line, and only for such a line, the part... | factor lube_parts_rule | parts_list, parts_charged, goodwill_credit, parts_repaid |
| maintenance_denial_reimbursement | 5 | For a maintenance re-decision line, and only for such a line, the diag... | factor lube_diag_share | diag_fee, diag_credit, diag_repaid |
| maintenance_denial_reimbursement | 6 | For a maintenance re-decision line, and only for such a line, the dedu... | factor lube_visit_deductible | ro_store, deductible_taken, billed_deductibles |
| maintenance_denial_reimbursement | 7 | For a maintenance re-decision line, the shop supplies fee repaid follo... | factor lube_supplies_share | ro_labor_all, supplies_fee, supplies_repaid |
| maintenance_denial_reimbursement | 8 | For a maintenance re-decision line, the hazardous-waste fee repaid fol... | factor lube_waste_share | waste_fee, waste_repaid |
| maintenance_denial_reimbursement | 9 | For a maintenance re-decision line, and only for such a line, every am... | assembly / plain selection | claims_net, limit_left, result |
| coverage_denial_reimbursement | 0 | This policy applies to the contract's latest component repair line den... | scope (record tests; plain bindings) | cover_denials, denied_claim, already_repaid, ro, denied_group, group_switch_on, deny_day, deny_odometer, ro_diag_day, diag_lines, in_term, lube_group, waiting_over, labor_close_day, begun_after_claim |
| coverage_denial_reimbursement | 1 | For a coverage re-decision line, the repaired concern line is the conc... | assembly / plain selection | covered_line, labor_charged |
| coverage_denial_reimbursement | 2 | The standard coverage re-decision repayment is the repaired concern li... | baseline (computation document) | labor_hours_billed, posted_rate, standard_labor, ro_store, deductible_chosen, visit_deductibles, deductible_taken |
| coverage_denial_reimbursement | 3 | For a coverage re-decision line, and only for such a line, the labor r... | factor cover_labor_rule | labor_list, comeback_credit, labor_repaid |
| coverage_denial_reimbursement | 4 | For a coverage re-decision line, and only for such a line, the parts r... | factor cover_parts_rule | parts_list, parts_charged, goodwill_credit, parts_repaid |
| coverage_denial_reimbursement | 5 | For a coverage re-decision line, and only for such a line, the diagnos... | factor cover_diag_share | diag_fee, diag_credit, diag_repaid |
| coverage_denial_reimbursement | 6 | For a coverage re-decision line, the shop supplies fee repaid follows ... | factor cover_supplies_share | ro_labor_all, supplies_fee, supplies_repaid |
| coverage_denial_reimbursement | 7 | For a coverage re-decision line, the hazardous-waste fee repaid follow... | factor cover_waste_share | waste_fee, waste_repaid |
| coverage_denial_reimbursement | 8 | For a coverage re-decision line, and only for such a line, every amoun... | assembly / plain selection | claims_net, limit_left, result |
| traded_vehicle_refund | 0 | This policy applies to a contract its holder cancels because the vehic... | scope (record tests; plain bindings) | request_day, certified |
| traded_vehicle_refund | 1 | The refund on a traded-vehicle cancellation is not computed until the ... | prerequisite sentence (wait on vsc_ext_maintenance_denial_reimbursement) |  |
| traded_vehicle_refund | 2 | The refund on a traded-vehicle cancellation is fixed only after the co... | prerequisite sentence (wait on vsc_ext_coverage_denial_reimbursement) |  |
| traded_vehicle_refund | 3 | For a traded-vehicle refund, a contract cancelled within the coverage ... | assembly / plain selection | claims_net, deal_status, flat_look |
| traded_vehicle_refund | 4 | The standard traded-vehicle refund is the retail price times the unuse... | baseline (computation document) |  |
| traded_vehicle_refund | 5 | For a traded-vehicle refund, the term is used up to a measuring day: w... | factor trade_measure_day | trade_contract_day, trade_appraisal_day, plan_id, plan_cancel_day, measure_day |
| traded_vehicle_refund | 6 | For a traded-vehicle refund, the unused mileage share is measured at a... | factor trade_reading | appraisal_odometer, appraisal_deal_day, ro_reading, reading |
| traded_vehicle_refund | 7 | For a traded-vehicle refund, the term miles run from a starting odomet... | factor trade_miles_start | deal_delivery, delivered_late, deal_odometer, deal_method, deal_distance, run_from |
| traded_vehicle_refund | 8 | For a traded-vehicle refund, days of the term the holder could not use... | factor trade_credit_days | credited_days |
| traded_vehicle_refund | 9 | For a traded-vehicle refund, the cancellation fee follows the holder's... | factor trade_fee_rule | denied_claim, redecided_count, account_tier, cancel_fee |
| traded_vehicle_refund | 10 | For a traded-vehicle refund, and only for such a refund, the unused sh... | assembly / plain selection | mileage_share, term_days, elapsed_days, used_days, time_share, unused_share |
| traded_vehicle_refund | 11 | For a traded-vehicle refund, and only for such a refund, the pro-rata ... | assembly / plain selection | result |

### XF recipe re-check (round 2)
- A1/A2/A3: factor independence re-scanned (no factor binding reads another factor's binding; elapsed_days moved into the kept elapsed factor); shared selections plain; assembly in result only.
- A4: table above — every rule sentence maps to the baseline, one factor, the scope, a prerequisite, or assembly; no sentence is used by two factors.
- A5: supplies/waste shares relabelled method (proportional allocation); deductible T2 adds an operand (billed deductibles); kept elapsed T1 floor vs T2 ceiling vs T3 raw.
- A6: T1 unchanged on both worlds (all figures identical); T2 per factor in the tables above (deductible T2 world: per-visit level off the selling store with a billed contract deductible).
- A7: no factor id inside a tool name (sweep).
- B8/B10: compute_basis quotes verbatim; rounding sentences = RND placement = tool half-up cents helper.
- B9/B12: probe table above.
- B11: framing clauses — the prior-authorization reading is stated as a record convention ("which the records take as ..."), no fact asserted that no record holds.
- C13/C14: every replaced_by names its own case, names its sibling cases, and restates base for every other case (19 overwrites).
- D15/D16: waits are record tests mirroring their resolvers' scopes; no other product makes a write owed at once that moves these reads (share tools are read-only outside identity/handoff).
- E17/E18/E19: tool bodies enforce formats (amount > 0 on paid lines, >= 0 on refunds; days >= 1; odometer >= 0; enum and date formats) and half-up rounding; events unchanged; no 0.00 paid line can be booked.
- F22: elapsed method keyed on the contract form (coverage level), not on who arranged financing; deductible ladders base-faithful.
- G26: proof text swept in both tasks (closure, necessity quotes, traces, tier_taken, rationale scope paragraph).

## Round 3 (audit revision_2) — what changed and the re-probe
- [SUPERSEDED by round 4] RED-C6r.1 (0.00 deadlocks): the refund waits on the re-decisions (kept <- waiting, traded <- maintenance, traded <- coverage) carve out, by plain record tests, the cases where the resolver computes 0.00: a deductible falling on the line (each resolver's own nil-deductible set: selling store + disappearing deductible, deductible chosen 0, or per-visit with the deductible already billed / already taken on the RO) and no aggregate limit left (claims paid less reversals not below the limit). In-scope lines also require customer-pay labor not wholly credited back as a comeback, so the total before the deductible is above zero. The rental wait carries the same limit test; the rental pays at least one day where the first-listed agreement charged daily rental, so it cannot compute 0.00 inside the wait.
- RED-C6r.2 (rental scope match): the rental policy and the kept wait select the claim by the same test (the claim of the contract's latest component-repair line, paid or denied, same-day tie first listed) and the agreement by the same test (the first agreement the loaner records list for that repair order, charged daily rental).
- RED-C5r: the rental replaced_by restates base for every rental the policy does not price (any other claim, any agreement after the first, an uncharged loaner, a rental from outside the group).
- RED-C4r.1: the traded refund no longer reads purchase deals for the measuring day or the reading (no field ties an appraisal to the covered vehicle); it reads the sold-or-traded cancellation of the Kessler Care plan sold on the contract's purchase deal (tier 1) and a loan payoff on the GAP waiver sold on that deal (tier 2). Task 1's world gains the plan's 2026-09-28 sold-or-traded cancellation (request, cancelled visit, 0.00 refund calculation under the retail-value deduction); measuring day and reading are unchanged, so gold is unchanged.
- RED-C4r.2: plan reads (maintenance proof, kept reading, traded tiers) key on the plan sold on the contract's purchase deal; the cancellation read keys on cancel_reason vehicle_sold_or_traded.
- RED-C4r.3: "the repair order whose labor was closed last" states its tie rule (same day: the first listed in the service records) in kept and traded.
- [SUPERSEDED by round 4: epsilon 0.000000001] Rounding: every rule rounding sentence says "rounded half up to the cent"; every money RND in compute is RND(x + 0.000001, 2) on non-negative amounts; tools keep the pure-Python half-up helper.
- F0-3 / F1-1: lines_decided trace lines replaced by billed_deductibles; ROUND 2 rationale paragraphs replaced by accurate ROUNDS 2-3 paragraphs; closure why_false texts restate the full waits; task-1 deal / plan read necessities, seed_consistency and rationale world rows updated; worklog round-2 plan line for RED-C2 corrected.

### Round-3 probe table (scratch copies of the task worlds; rule column = round-3 rule)
| probe | compute | rule |
|---|---|---|
| C6r.1 small repair off the selling store, deductible 100 | waiting result 0.00; waiting wait blocks=False; rental wait blocks=False | 0.00 and neither wait blocks (deductible falls: carved out) |
| C6r.1 limit exhausted (40000.00 paid) | waiting 0.00; waits block=False/False | 0.00 and both waits carved out (no limit left) |
| C6r.2 uncharged agreement listed first | rental 0.00; rental wait blocks=False | 0.00 and the wait does not block (same first-listed test) |
| C6r.2 waiting claim repaid earlier, later claim paid | rental claim CLM-4479999, rental 0.00; rental wait blocks=False | both select CLM-4479999 (no loaner): 0.00, wait does not block |
| rounding exact tie: hazwaste 4.95 x 482.76/965.52 = 2.475 | 2.48 | 2.48 (half up) |
| C4r.1 trade of another vehicle on a closed NVRP deal | 2035.27 | 2035.27 unchanged (deals no longer read) |
| C4r.2 earlier own-request cancellation calc listed first | 2035.27 | 2035.27 (reason-keyed read) |
| C4r.3 two ROs with last labor the same day | ro_reading 73600 | first listed in the service records (RO 449000 here) |
| month-end: visit 2025-08-31, diagnosis 2026-08-30 | visit_proof 1 | 1 (12 calendar months less one: 11 < 12) |
| task 0 opening / after waiting / after rental | waits block (True, True) / (False, True) / (False, False) | both unmet at the opening, each clears once its resolver writes |

### XF recipe re-check on the touched policies (round 3)
- A1-A3: no factor binding reads another factor's binding (sweep); trade_measure_day and trade_reading read the plan separately (plan_id / reading_plan).
- A5/A6: trade_measure_day tiers: plan refund-calculation date | GAP loan payoff date | effective date (three records); T1 figures unchanged; T2 for tier 2 needs a GAP waiver world.
- B8-B12: rule == compute re-checked for every edited sentence; probes above; tie rules stated (latest component line, first-listed agreement, labor closed last, plan refund calculation).
- C13: 19/19 replaced_by name scope and siblings and restate base for every other case.
- D15: waits are record tests; none evaluates another policy's computation; every wait is satisfiable in every world in its own scope (zero-amount cases carved out).
- E19: no paid line of 0.00 is ever required.
- Residue: the GAP tier is declared and read but no task world seeds a GAP waiver (tier 2 is a producible case, not exercised by gold).

### Recipe A4 — defining-sentence table (round 3)
| policy | # | sentence opens | role | bindings quoting it |
|---|---|---|---|---|
| waiting_denial_reimbursement | 0 | This policy applies to the contract's latest component repair line den... | scope (record tests) | sold_on_deal, waiting_denials, denied_claim, already_repaid, ro, denied_group, deny_day, deny_odometer, group_switch_on, ro_diag_day, diag_lines, in_term, lube_group, labor_close_day, begun_after_claim |
| waiting_denial_reimbursement | 1 | For a waiting-period re-decision line, the covered concern line is the... | assembly / plain selection | covered_line, labor_charged |
| waiting_denial_reimbursement | 2 | The standard waiting-period re-decision reimbursement is the covered c... | baseline (computation document) | labor_hours_billed, posted_rate, standard_labor, deductible_chosen |
| waiting_denial_reimbursement | 3 | For a waiting-period re-decision line, and only for such a line, the l... | factor covered_labor_basis | labor_list, comeback_credit, labor_reimbursed |
| waiting_denial_reimbursement | 4 | For a waiting-period re-decision line, and only for such a line, the p... | factor covered_parts_basis | parts_list, parts_charged, goodwill_credit, parts_reimbursed |
| waiting_denial_reimbursement | 5 | For a waiting-period re-decision line, and only for such a line, the d... | factor diagnostic_credit_share | diag_fee, diag_credit, diag_reimbursed |
| waiting_denial_reimbursement | 6 | For a waiting-period re-decision line, and only for such a line, the d... | factor visit_deductible_rule | ro_store, deductible_taken, billed_deductibles |
| waiting_denial_reimbursement | 7 | For a waiting-period re-decision line, the shop supplies fee reimburse... | factor shop_supplies_share | ro_labor_all, supplies_fee, supplies_reimbursed |
| waiting_denial_reimbursement | 8 | For a waiting-period re-decision line, the hazardous-waste fee reimbur... | factor hazwaste_fee_share | hazwaste_fee, hazwaste_reimbursed |
| waiting_denial_reimbursement | 9 | For a waiting-period re-decision line, and only for such a line, every... | assembly / plain selection | claims_net, limit_left, result |
| claim_rental_reimbursement | 0 | This policy applies to the rental benefit of the claim of the contract... | scope (record tests) | claim, ro, repair_paid, rental_agreement, charged_rental_days |
| claim_rental_reimbursement | 1 | A rental line is booked only after the records carry a paid component-... | prerequisite sentence (wait on vsc_ext_waiting_denial_reimbursement) |  |
| claim_rental_reimbursement | 2 | The standard rental is the coverage level's rental amount per day time... | baseline (computation document) | diag_day, ro_last |
| claim_rental_reimbursement | 3 | Rental days are counted from a start day: where the loaner went out af... | factor rental_window_start | loaner_out, denial_day, start_day |
| claim_rental_reimbursement | 4 | Rental days are counted to an end day: where the loaner came back befo... | factor rental_window_end | covered_line, loaner_back, covered_last, end_day, ro_diag_lines |
| claim_rental_reimbursement | 5 | Days the store gave free are not reimbursed: where the loaner was a de... | factor free_courtesy_days | loaner_basis, courtesy_days, bonus_days, account_tier, account_status, free_days |
| claim_rental_reimbursement | 6 | The amount per day follows what the loaner cost: where the loaner was ... | factor rental_day_amount | loaner_id, charged_rate, allowance, day_amount |
| claim_rental_reimbursement | 7 | For a rental line this policy pays, and only for such a line, the days... | assembly / plain selection | days_counted, days_already, days_paid, claims_net, limit_left, result |
| kept_vehicle_refund | 0 | This policy applies to a contract its holder cancels while keeping the... | scope (record tests) | request_day, certified |
| kept_vehicle_refund | 1 | The refund on such a cancellation is fixed only after the records carr... | prerequisite sentence (wait on vsc_ext_waiting_denial_reimbursement) |  |
| kept_vehicle_refund | 2 | The refund on such a cancellation is not computed until the claim of t... | prerequisite sentence (wait on vsc_ext_claim_rental_reimbursement) |  |
| kept_vehicle_refund | 3 | For a kept-vehicle refund, a contract cancelled within the coverage le... | assembly / plain selection | claims_net, deal_status, flat_look |
| kept_vehicle_refund | 4 | The standard kept-vehicle refund is the retail price times the unused ... | baseline (computation document) |  |
| kept_vehicle_refund | 5 | For a kept-vehicle refund, the unused mileage share is measured at a r... | factor mileage_reading_tier | ro_reading, plan_id, visit_reading, reading, visit_entry, visit_reinstated |
| kept_vehicle_refund | 6 | For a kept-vehicle refund, the term miles run from a starting odometer... | factor term_miles_start | deal_delivery, delivered_late, deal_odometer, deal_method, deal_distance, run_from |
| kept_vehicle_refund | 7 | For a kept-vehicle refund, the elapsed days of the term, the calendar ... | factor elapsed_term_measure | elapsed_days, elapsed_measured |
| kept_vehicle_refund | 8 | For a kept-vehicle refund, days of the term the holder could not use a... | factor unusable_days_credit | credited_days |
| kept_vehicle_refund | 9 | For a kept-vehicle refund, the cancellation fee follows how the cancel... | factor cancel_fee_standing | window_from, denied_claim, redecided_count, plan_status, cancel_fee |
| kept_vehicle_refund | 10 | For a kept-vehicle refund, and only for such a refund, the unused shar... | assembly / plain selection | mileage_share, term_days, used_days, time_share, unused_share |
| kept_vehicle_refund | 11 | For a kept-vehicle refund, and only for such a refund, the pro-rata re... | assembly / plain selection | result |
| maintenance_denial_reimbursement | 0 | This policy applies to the contract's latest component repair line den... | scope (record tests) | maint_denials, denied_claim, already_repaid, ro, denied_group, lube_group, ro_diag_day, plan_id, visit_day, visit_proof, visit_entry, visit_reinstated, deny_day, deny_odometer, group_switch_on, diag_lines, in_term, waiting_over, labor_close_day, begun_after_claim |
| maintenance_denial_reimbursement | 1 | For a maintenance re-decision line, the repaired concern line is the c... | assembly / plain selection | covered_line, labor_charged |
| maintenance_denial_reimbursement | 2 | The standard maintenance re-decision repayment is the repaired concern... | baseline (computation document) | labor_hours_billed, posted_rate, standard_labor, deductible_chosen |
| maintenance_denial_reimbursement | 3 | For a maintenance re-decision line, and only for such a line, the labo... | factor lube_labor_rule | labor_list, comeback_credit, labor_repaid |
| maintenance_denial_reimbursement | 4 | For a maintenance re-decision line, and only for such a line, the part... | factor lube_parts_rule | parts_list, parts_charged, goodwill_credit, parts_repaid |
| maintenance_denial_reimbursement | 5 | For a maintenance re-decision line, and only for such a line, the diag... | factor lube_diag_share | diag_fee, diag_credit, diag_repaid |
| maintenance_denial_reimbursement | 6 | For a maintenance re-decision line, and only for such a line, the dedu... | factor lube_visit_deductible | ro_store, deductible_taken, billed_deductibles |
| maintenance_denial_reimbursement | 7 | For a maintenance re-decision line, the shop supplies fee repaid follo... | factor lube_supplies_share | ro_labor_all, supplies_fee, supplies_repaid |
| maintenance_denial_reimbursement | 8 | For a maintenance re-decision line, the hazardous-waste fee repaid fol... | factor lube_waste_share | waste_fee, waste_repaid |
| maintenance_denial_reimbursement | 9 | For a maintenance re-decision line, and only for such a line, every am... | assembly / plain selection | claims_net, limit_left, result |
| coverage_denial_reimbursement | 0 | This policy applies to the contract's latest component repair line den... | scope (record tests) | cover_denials, denied_claim, already_repaid, ro, denied_group, group_switch_on, deny_day, deny_odometer, ro_diag_day, diag_lines, in_term, lube_group, waiting_over, labor_close_day, begun_after_claim |
| coverage_denial_reimbursement | 1 | For a coverage re-decision line, the repaired concern line is the conc... | assembly / plain selection | covered_line, labor_charged |
| coverage_denial_reimbursement | 2 | The standard coverage re-decision repayment is the repaired concern li... | baseline (computation document) | labor_hours_billed, posted_rate, standard_labor, ro_store, deductible_chosen, visit_deductibles, deductible_taken |
| coverage_denial_reimbursement | 3 | For a coverage re-decision line, and only for such a line, the labor r... | factor cover_labor_rule | labor_list, comeback_credit, labor_repaid |
| coverage_denial_reimbursement | 4 | For a coverage re-decision line, and only for such a line, the parts r... | factor cover_parts_rule | parts_list, parts_charged, goodwill_credit, parts_repaid |
| coverage_denial_reimbursement | 5 | For a coverage re-decision line, and only for such a line, the diagnos... | factor cover_diag_share | diag_fee, diag_credit, diag_repaid |
| coverage_denial_reimbursement | 6 | For a coverage re-decision line, the shop supplies fee repaid follows ... | factor cover_supplies_share | ro_labor_all, supplies_fee, supplies_repaid |
| coverage_denial_reimbursement | 7 | For a coverage re-decision line, the hazardous-waste fee repaid follow... | factor cover_waste_share | waste_fee, waste_repaid |
| coverage_denial_reimbursement | 8 | For a coverage re-decision line, and only for such a line, every amoun... | assembly / plain selection | claims_net, limit_left, result |
| traded_vehicle_refund | 0 | This policy applies to a contract its holder cancels because the vehic... | scope (record tests) | request_day, certified |
| traded_vehicle_refund | 1 | The refund on a traded-vehicle cancellation is not computed until the ... | prerequisite sentence (wait on vsc_ext_maintenance_denial_reimbursement) |  |
| traded_vehicle_refund | 2 | The refund on a traded-vehicle cancellation is fixed only after the co... | prerequisite sentence (wait on vsc_ext_coverage_denial_reimbursement) |  |
| traded_vehicle_refund | 3 | For a traded-vehicle refund, a contract cancelled within the coverage ... | assembly / plain selection | claims_net, deal_status, flat_look |
| traded_vehicle_refund | 4 | The standard traded-vehicle refund is the retail price times the unuse... | baseline (computation document) |  |
| traded_vehicle_refund | 5 | For a traded-vehicle refund, the term is used up to a measuring day: w... | factor trade_measure_day | plan_id, plan_cancel_day, measure_day, gap_payoff_day |
| traded_vehicle_refund | 6 | For a traded-vehicle refund, the unused mileage share is measured at a... | factor trade_reading | ro_reading, reading, reading_plan, cancel_odometer |
| traded_vehicle_refund | 7 | For a traded-vehicle refund, the term miles run from a starting odomet... | factor trade_miles_start | deal_delivery, delivered_late, deal_odometer, deal_method, deal_distance, run_from |
| traded_vehicle_refund | 8 | For a traded-vehicle refund, days of the term the holder could not use... | factor trade_credit_days | credited_days |
| traded_vehicle_refund | 9 | For a traded-vehicle refund, the cancellation fee follows the holder's... | factor trade_fee_rule | denied_claim, redecided_count, account_tier, cancel_fee |
| traded_vehicle_refund | 10 | For a traded-vehicle refund, and only for such a refund, the unused sh... | assembly / plain selection | mileage_share, term_days, elapsed_days, used_days, time_share, unused_share |
| traded_vehicle_refund | 11 | For a traded-vehicle refund, and only for such a refund, the pro-rata ... | assembly / plain selection | result |


## Round 4 (audit revision_3) — what changed and the re-probe
- [SUPERSEDED by round 5: action form] RED-C6r2 (all four members): the refund waits no longer carve out deductible-bearing lines. Each re-decision wait (kept <- waiting, traded <- maintenance, traded <- coverage) now carves out exactly the 0.00 cases: "the deductible taken on that line is less than the amount the line repays before the deductible (its labor, parts and diagnostic fee repaid and its shares of the repair order's shop fees)" and claims paid less reversals below the aggregate limit. Every positive repayment stays inside the wait, deductible or not. The kept rental wait (member b) follows the waiting wait's line through the same test and adds the rental's exact 0.00 case: "the rental days that claim's rental line pays (the window days, both counted, less the days the store gave free, within the rental days left on the claim) are above zero".
- Zero-amount ruling: the rental's "never below one day where the holder was charged daily rental" floor is removed (rule and compute). A 0-day rental is now carved out of the wait instead of being paid.
- RED-C9 (rounding ruling): every money RND in compute is RND(x + 0.000000001, 2) on non-negative values; rules say "rounded half up to the cent"; the tools keep the integer half-up helper. Check: every RND argument evaluated for every scored, factor-sensitivity and all-baseline figure on both worlds (104 arguments) sits at least 0.000104 from a half cent.
- F0-4 / F1-2: the round-3 rationale sentences that called a deductible-bearing line a 0.00 case are rewritten to the exact carve-out; the stale "0.000001", "at least one day" and "max(1 ...)" proof text is swept; closure why_false texts say the deductible taken (0.00) is below the repayable amount.
- Gold unchanged in both tasks; every factor and baseline figure identical.

### Round-4 probe table (scratch copies of task 0's world)
| probe | (waiting result, rental result, waiting wait blocks, rental wait blocks) or figure | rule |
|---|---|---|
| RO off the selling store, deductible 100 (positive repayment) | (1567.15, 0.00, True, True) | 1567.15 owed: the waits block (both orders are no longer defensible) |
| exact 0.00: deductible 100 >= repayable amount | (0.00, 0.00, False, False) | carved out |
| rental: free days cover the window (no floor) | (0.00, 0.00, False, False) | rental 0.00 carved out |
| exact tie: hazwaste 4.95 x 482.76/965.52 = 2.475 | 2.48 | 2.48 (half up) |
| near tie: 4.95 x 1311.70/2064.52 = 3.1449998... | 3.14 | 3.14 (not moved by the 1e-9 epsilon) |

## Round 5 (audit revision_4) — RED-C10
- RED-C10 (all four members): the round-4 carve-outs priced the resolver's tiers inside the wait. No plain record test separates a re-decision (or rental benefit) that owes nothing from one not yet decided, because one that owes nothing books no line. The four refund waits are therefore stated in the action form, each with fallback_reason "A re-decision that repays nothing books no line, so no record state tells a decided line from an undecided one" (rental: "A rental benefit that pays nothing books no rental line ..."):
  1. kept <- waiting: "The refund on such a cancellation is fixed only after the contract's latest component repair line denied for the waiting period has been re-decided and whatever that re-decision owes the holder has been paid."
  2. kept <- rental: "The refund on such a cancellation is not computed until the rental benefit of the claim of the contract's latest component-repair line, paid or denied, has been settled and whatever rental it owes the holder has been paid."
  3. traded <- maintenance: "The refund on a traded-vehicle cancellation is not computed until the contract's latest component repair line denied for lack of maintenance has been re-decided and whatever that re-decision owes the holder has been paid."
  4. traded <- coverage: "The refund on a traded-vehicle cancellation is fixed only after the contract's latest component repair line denied as not covered has been re-decided and whatever that re-decision owes the holder has been paid."
- RED-C6r2 stays closed: every positive repayment or rental is owed by the completed action and so stays inside the wait; a re-decision owing 0.00 completes with no line (no 0.00 write, zero-amount ruling kept). The rental's own wait on the paid component line stays in the state form (a record test). Rounding ruling unchanged.
- Gold unchanged in both tasks; trees, kinds and gates unchanged; closure edges carry form action and the fallback_reason; rationale tree paragraphs, why_false texts and necessity quotes swept.

## Round 6 (audit revision_4/5) — RED-C11
- RED-C11 (all four members): each action-form wait now states, as plain record tests on recorded fields, exactly the scope under which its resolver re-decides, so an out-of-scope latest denial is plainly outside the wait and the sentence has one reading (no "re-decided" demand that no policy can satisfy):
  1. kept <- waiting: latest waiting-period denial (tie: first in the claim history) on a contract sold on its deal, group not internally lubricated with its switch true, diagnosis date and odometer within the term, one diagnosed concern line with customer-pay labor not wholly comeback-credited, closed on or after the decision.
  2. kept <- rental: the claim of the latest component-repair line (paid or denied; tie first listed) that carries a paid component-repair line or holds the line sentence 1 waits on, whose first-listed loaner agreement is a Kessler loaner charged daily rental, at a coverage level with rental amount per day and day limit above zero.
  3. traded <- maintenance: latest lack-of-maintenance denial on an engine, transmission or drive axle with its switch true, latest non-reinstated visit on the plan sold on the contract's deal within the look-back before the diagnosis, waiting period over or waived, within the term, one diagnosed concern line, labor as above.
  4. traded <- coverage: latest not-covered denial on a group not internally lubricated with its switch true, waiting period over or waived, within the term, one diagnosed concern line, labor as above.
- Conditions mirror the sentences at the same strength ("... outside those tests is outside the wait"); action form and fallback_reason kept (a re-decision owing nothing books no line). Rulings kept. Gold unchanged; both worlds sit inside every scope.

## Round 7 (audit revision_6) — RED-C11r
- kept <- rental: the wait now engages exactly on the rental policy's own record test — the claim of the contract's latest component-repair line (tie first listed) where that claim carries a paid component-repair line, its first-listed loaner agreement is a Kessler loaner charged daily rental, and the level's rental amount per day and day limit are above zero. The disjunct "or its latest line is the one the previous sentence waits on" is dropped, so an in-scope waiting re-decision owing 0.00 engages no rental wait. Ordering after the waiting re-decision rests on the rental policy's own state-form wait ("A rental line is booked only after the records carry a paid component-repair line under the same claim number.").
- Class sweep: no other wait carries a disjunct beyond its resolver's scope (traded <- maintenance / coverage and kept <- waiting mirror their resolvers exactly).
- Task 0: gold, order and figures unchanged; closure why_false for the rental edge explains it engages at the refund's handling time (after the 1667.15 line).

## Round 8 (audit revision_7) — RED-C12 / F0-5
- kept <- rental is keyed on record tests present at the opening: the claim of the contract's latest component-repair line, paid or denied (tie first listed), whose repair order's first-listed loaner agreement is a Kessler loaner charged daily rental, at a coverage level whose rental amount per day and day limit are above zero (action form and fallback_reason kept).
- The rental policy settles every claim inside that wait: with a paid component-repair line it books the rental line; with none, the benefit is settled with nothing owed and no line is booked (base: benefits only together with a covered component repair). Compute unchanged (repair_paid > 0 guard).
- Checks (probe8): task 0 opening — engaged True, no rental line, repair_paid 0 (unmet); 0.00 waiting re-decision world — engaged, settled at nothing owed, no line (one reading, no deadlock); after the 1667.15 repayment — rental owes 45.00. RED-C11/C11r stay closed (no wait reaches beyond what its resolver settles). Gold unchanged.

## Round 9 (renderer scan render_r1, F1-F5) — rule == compute at every edge
- F1 rental_window_start tier 2 now also tests loaner_out == diag_day (the rule's "the loaner went out on that day").
- F2 kept cancel_fee_standing / traded trade_fee_rule: "the contract's latest denied component-repair line ... was later paid as a component-repair line on the same claim number, repair order and component group"; compute reads denied_claim / denied_ro / denied_group / denied_day (component_repair denials only) and counts paid component-repair lines on that claim, RO and group dated after the denial (redecided_count, still the value_input gate).
- F3 waiting / maintenance / coverage already_repaid keys on claim number, repair order and component group (the ledger's claim-line grain), placed after ro and denied_group.
- F4 plan lookups (maintenance plan_id, kept plan_id, traded plan_id and reading_plan) and the traded GAP lookup run only when the contract was sold on a deal (empty purchase_deal_id -> None); each sentence says "(a contract sold on its own has no such plan / has none)".
- F5 kept term_miles_start / traded trade_miles_start tiers 1-2 apply only where the term counts from the sale date (P('term_start_basis') == 'sale_date'); "otherwise, including every term counted from the vehicle's in-service date, the term start odometer" — one reading with the in-service clause.
- Class sweeps: selectors ignoring claim/RO/group grain — only F2/F3 sites (rental's claim-level reads are claim-grain by rule); exact-match lookups on possibly-empty ids — only F4 sites (purchase-deal reads use the contract's own deal; loaner/service reads key on a non-empty RO); tier conditions the compute does not test — F1 plus the labor/parts tiers' "under an Owner Rewards ... discount" wording (removed from the three re-decisions' rule sentences and ladders; compute tests charged below list).
- Gold unchanged in both tasks; COMPUTE OK (history_rows_max 8 restored by keeping redecided_count a COUNT).

Probe (scratch copies of the task worlds):
| probe | compute | rule |
|---|---|---|
| F1 loaner out 09-07, diagnosis 09-08, denial 09-09 | start_day 2026-09-08 | 2026-09-08 (tier 3: loaner not out on the diagnosis day) |
| F2 latest denied line is a rental line on a claim whose engine line was paid | denied_claim CLM-4471208, redecided_count 0 | the latest denied component-repair line (CLM-4471208, not repaid) -> 0 |
| F3 steering line paid under the same claim as the denied cooling line | already_repaid 0, result 1080.91 | 0 and 1080.91 (grain: claim, RO, group) |
| F4 standalone contract and standalone plan | plan_id None, visit_proof 0, result 0.0 | no plan sold on the contract's deal: None, out of scope 0.00 |
| F5 Exclusionary Wrap (in-service term) sold on a late-delivered deal | run_from 0 | 0 (term start odometer; pre-sale miles count as used) |

## Round 10 (audit revision_9) — RED-R9a / RED-R9b
- RED-R9a (kept cancel_fee_standing, traded trade_fee_rule): rule now says "(a paid line entered on or after the day of that denial counts as later)"; compute redecided_count tests repaid_day >= denied_day; ladders updated.
- RED-R9b (rental_window_start tier 2): rule now says "the day of the claim's latest denial (by decision date; several lines denied on that same day share it)", matching denial_day = LATEST(... claim) in compute; ladder method updated.
- Gold unchanged in both tasks (dates differ; one denied line per claim).

| probe | compute | rule |
|---|---|---|
| R9a denial and repayment on the same day | redecided_count 1, fee 0.0 | counts as later paid: 1, fee 0.00 |
| R9b second denied line on the claim 09-11 | start_day 2026-09-11, result 0.0 | the claim's latest denial (09-11): window 09-11..09-13, 3 days - 4 free = 0.00 |

## Round 11 (seed-only, KB revision_1 SRC-1..3)
- SRC-1: task 0 seeds two authorized written estimates on RO 446215 (A 1634.54 on 2026-09-09, B 273.70 on 2026-09-12); gold reads find_service_repair_authorizations.
- SRC-2: task 1 plan KC-4431560 refund calculation 85.95 (published retail refund rules) + 85.95 refund paid to Fifth Third Bank 2026-10-06.
- SRC-3: purchase_transactions seeded for KHR-26-41087, KHB-24-40517, KHB-26-41862 (contract-day postings, deposit, applied deposit, down payment, lender funding; each closes at 0.00); gold reads find_purchase_transactions per deal. KHB-26-41862 payoff 23618.42 (18.42 negative equity posted).
- Charter and tools byte-identical; scored values unchanged.
