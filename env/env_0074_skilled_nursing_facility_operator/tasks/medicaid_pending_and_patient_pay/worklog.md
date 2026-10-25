# worklog — medicaid_pending_and_patient_pay

## Step 0 (difficulty pre-check)
- Read: references (product_extended.yaml, task_tools.py, task.json), blueprint.yaml, products/medicaid.yaml, db_schema.json,
  share_tools.py (verify threshold = 2 matching details among dob/ssn_last4/phone/email/original_admission_date),
  XF_recipe.md (A1-F32, applied to every policy below), cross charters (private/bedhold/medicare/trust rules).
- Draw (draw_counts.py --tasks 2): task0 prerequisite_problems=2 factor_counts [5,4,4]; task1 prerequisite_problems=1 factor_counts [5,5].
- Base automatic clauses: approval triggers approved_ma_covered settlements; denial-final/hearing-upheld trigger
  denied_moved_to_private; true-up within trueup_days (30) of approval notice; credit refunded within refund_days (30);
  past-due notice once a charge is unpaid 30 days after the due day (10th); accruals only while pending/denied/fair_hearing;
  patient pay billed only while pending/eligible/fair_hearing.
- User-owned writes in this blueprint (signature, AR designation, withdrawal, hearing request) carry no computable
  figure; the representative's own payment is the customer write that carries a policy-computed amount.
  Both user problems are therefore payments the representative authorises over the phone (ACH), each on a
  different object and quantity (task 0: the portion of a billed actual month the representative owes after the
  payee transfer and credits; task 1: an advance payment for a coming pending month's estimate).
- DSL notes: CPARAM on private daily_rate_schedule returns a map (unusable) -> private rates are read from records
  (accrual daily_rate, private ledger daily_rate); windows run from NOW (MONTHS with day comparison);
  month strings built with ('%d' % y) + '-' + ('%02d' % m) when needed.

## Resume (successor agent, 2026-10-22)
- Read plan.md / worklog.md; extended.yaml had base only. ev.py reused.
- DESIGN REVISION (T1 link): the recorded T1 edge "HMA month count reads pending-accrual rows" is wrong on
  the calendar: the months a home maintenance allowance has run are calendar months since eligibility was
  requested, the current month is never accrued yet, so a count of accrual rows is off by the open month and a
  November estimate billed before October's accrual posts would contradict it. No other real link from a
  pending accrual to a coming month's estimate exists (accrual = private-rate pricing; patient pay = income
  rules). Also the accrual's rate-side factors (rate notice, isolation tier) need private schedule rates that
  no record or DSL read carries (CPARAM gives a map). => T1 P1a becomes the cost-of-care reduction of a closed
  pending month's estimate (base: patient pay never exceeds the month's cost of care; reason cost_of_care_cap),
  which creates a patient pay credit; P1b (root, user) = advance for the coming pending month = estimate less
  that credit (genuine value_input, the conversation a real business office has).
- T0 keeps the recorded eligible-stage tree (settlement -> true-up -> advance on the notice amount).
- Factor approach: every tier is a real charter rule (base or cross charter), record-derived; tiers that the
  world does not exercise are allowed (only the fall-through must be left).

## Resume 2 (third agent, 2026-10-22)
- Scratch: /tmp/medicaid_0074/pol/<policy>.yaml (one file per extended policy), merge.py (base verbatim + extended_policies).
- P0a written (medicaid_ext_actual_month_cost_cap, tool post_cost_of_care_reduction_89ef8a19, 4 factors):
  baseline = base literal (every calendar day at the Medicaid daily rate); factors: part_a_days_without_cost (method,
  medicare: benefit-day 1-20 days / lapsed-certification reversals), held_leave_days (method, bedhold x medicare),
  coinsurance_year_price (parameter, year of service: 2026/2025 CMS coinsurance), medigap_share (parameter, medicare
  plan letter + supplemental effective date). Assembly: Medicaid days x MA rate + coinsurance days x price x share/100.
- T0 October world fixed: Part A from 2026-09-28 (day 1), days 1-20 through 10-17, 10-18..10-20 days 21-23,
  hospital leave 10-21/10-22 on a Medicare-stay private hold, return 10-23 (interrupted stay), days 24-28 through
  last covered date 10-27, Medicaid days 10-28..10-31.
- DESIGN CHANGE (gate-forced, check_compute factor load-bearing): the plain true-up (estimate - notice amount) cannot
  carry 5 load-bearing record factors; P0b keeps its write (trueup_decrease on the latest estimate month) but the
  month's actual patient pay is the lesser of the notice amount and that month's cost of care (base: "patient pay
  never exceeds the month's cost of care"), so P0b carries 5 cost factors (Part A days, leave days, admission/closing
  days via the admission agreement, coinsurance year figure, Medigap percent). T0 resident is therefore a NEW
  admission 2026-09-02 straight into a Part A stay (Sept = admission month + Part A month).
- P0c factors (4): coming_month_patient_pay (param, notice dates), funds_account_applies (method, trust tier +
  payee benefits), allowance_paid_from_funds (param, CSA/FA/HMA, trust), premium_paid_from_funds (method, payee x QMB).
  T0 tier = Community Spouse Allowance (husband at home). Edges P0c<-P0a, P0c<-P0b value_input on case_credit (state form).
- check_extended: structure PASS (only task files missing); check_task_tools: TASK TOOL CONTRACT OK (3 tools).
- T0 world builder: /tmp/medicaid_0074/build_t0.py (seeded uuid4), evaluator eval_t0.py. Results: P0a 210.93,
  P0b 1870.75, P0c 556.02 (skip P0a -> 766.95, skip P0b -> 2426.77; P0a/P0b commute). All factor baselines move result.
- T0 story: Lorraine M. Kessler admitted 2026-09-02 from UPMC Harrisburg into a Part A stay (Plan L), MA application
  09-08 (POA son Daniel J. Kessler), approved 09-29 from 09-01, PP 2141.90; redetermination (Medigap premium rise)
  dated 11-04 sets 2125.70 from 12-01; center is SSA payee from Oct (Medicaid payee funds account, standing
  authorization for patient pay); Sept estimate 2250.50 unpaid (past-due notice 10-12); Oct/Nov paid (payee + ACH).
- Gate-driven fixes T0: reduction tools take adjustment_reason (Enum, schema closed set) because the base dedup gate
  adjust_once binds charge_entry_id + adjustment_reason; own-history reads switched to SUM (history floor of
  check_compute zeroes SUM/COUNT/MAX only); case balance in the advance read from the ledger sums; non-read noise rows
  (application signature request, bed-hold elections, trust requests) dropped for replay closure.
- TASK 0 per-task gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.

### Probe table (T0, probe_t0.py on scratch copies)
| read | decoy | result | verdict |
|---|---|---|---|
| CFIELD medicare plan letter (cost cap) | older closed episode with Plan F listed first | 1567.18 (gold 210.93) | first-match risk; world holds one episode; rule says "the resident's Medicare coverage" |
| LATEST estimated_pending month (true-up) | earlier 2026-08 estimate | 1870.75 unchanged | latest month kept |
| medicare reversals (cost cap) | extra hospital_day reversal in Oct | 0 | reversed non-uncertified day priced as Medicaid day (stated by rule: only lapsed-certification reversals dropped) |
| advance on opening world | prerequisites unresolved | 2637.70 (gold 556.02) | prerequisites load-bearing |

### Pairwise method-tier table (distinguishing input per pair)
- part_a_days_without_cost: both vs band-1-20-only (adds uncertified reversal input); both vs uncertified-only (adds band-1-20 input); band-1-20 vs uncertified (different input); any vs none (input vs 0).
- held_leave_days / leave_days_taken_out: Part A month (all held days, payer field ignored) vs private-only (day_payer filter) vs none.
- admission_or_closing_days: admission+closing (two date spans) vs admission (DAYS from first day) vs closing (DAYS to month end) vs none.
- benefit_routed_to_patient_pay: payee SSA deposit vs authorized pension deposit (different deposit source) vs nothing.
- case_balance_carried: owed (+balance) vs fresh credit (credit subtracted, refund-days date test) vs nothing.

## Task 1 (draw: prerequisite_problems=1, factor_counts [5,5])
- DESIGN CHANGE (realism/consistency): the three cost-of-care computations (actual-billed month, reconciled estimate
  month, pending estimate month) state one law in three scoped copies; each overwrite of the base clause "patient pay
  never exceeds the month's cost of care." names the two sibling scopes (XF C17). P1a = medicaid_ext_pending_estimate_cost_cap
  (5 factors, same five dimensions as the reconciled copy). P1b = medicaid_ext_pending_advance_payment (5 factors:
  allowance deducted with HMA months, interest counted (method: latest / one-third of 3 months), premiums counted
  (QMB / card not yet forwarded / case premiums), funds applied (non-Medicaid self-directed pension / non-Medicaid payee),
  pending balance carried). The plan's "move-out Dec 4" is dropped: a partial-month cap binding in December would
  make every estimate factor non-load-bearing (lesser-of); the resident is expected home later.
- Tools: post_pending_cost_of_care_reduction_7ee4a52a (agent), pay_pending_patient_pay_advance_fe3c809e (user).
  check_task_tools OK (5 tools); check_extended --task 0 OK with 5 policies.
- T1 builder/evaluator: build_t1.py / eval_t1.py (scratch). P1a 627.60, P1b 154.78 (skip P1a -> 782.38). Per-task gates green.
- Docstring sweep (XF D19/D23): ordering words removed (before/after), helper renamed; no datetime/time/random/uuid/secrets.
- XF B9 sweep (scratch): every compute_basis quote, baseline sentence and replaced_by verbatim in its own rule for all 5 policies.
- Residual risks for the audit: the cost-of-care law is stated in three scoped copies (actual-billed / reconciled / pending
  estimate months); the medicare ledger also bills the resident's Plan L/K coinsurance share that the patient pay cap
  counts as cost of care; the pending advance's estimate counts interest and verified premiums differently from the
  billed estimate (declared overwrite); CFIELD first-match reads (one coverage / agreement / funds account per world).
- Full suite (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  SCOPE OK (+ CACHE-DIFF INFO optional; TRACEABILITY runs after KB render).
ROUND 1: gates 7/7 green

## REWORK round 2 (audit revision_1: _difficulty.md F-01..F-13, 0.md T0-1..T0-4, 1.md T1-1..T1-4)
Plan (persisted before edits):
- F-01: cost of care no longer counts the resident's own Medicare coinsurance share. A Part A coinsurance day carries
  the booked daily coinsurance only where the Medicare coverage is QMB-verified (Medical Assistance pays it as
  crossover); with a non-QMB coverage it carries nothing (Medigap plan + resident, billed by the Medicare product);
  with no Part A coverage on file it is priced as a Medicaid day. The resident's own coinsurance share instead enters
  the pending advance's estimate as an incurred medical expense deduction (42 CFR 435.725(c)(4)(ii)) - real lever.
- Cost-of-care factors (P1 4 / P2 5 / P4 5): coinsurance_day_cost (param), held_days_counted (param, bed-hold tier
  reserved-day limits via CPARAM on the month's booking), part_a_days_without_cost (method), unheld_leave_days
  (method: declined / released holds, reservation dates), + stay-window (method; estimate months only: skilled
  admission = Medicare coverage start equal to the qualifying discharge [F-09], departure via bed-hold ended by a
  hospital discharge elsewhere or a case closing).
- F-02: P2/P4 declare the base partial-month sentence (sibling-aware replaced_by restating it for out-of-scope months).
- F-03/F-08: P5 estimate standard = base formula incl. VA and tier allowance; allowance factor removed.
- F-04: P3/P5 declare the refund clause (a fresh credit is applied to the coming month, capped at it).
- F-05/F-07/F-08 P3: coming-month patient pay plain (notice in effect); payee benefit in the standard; factors
  amount_kept (param, payee tiers), authorized_pension (param), payee_benefit_month (method), balance_carried (method).
- P5 factors: projected_coinsurance (method), premiums_counted (param), interest_counted (param), funds_applied
  (param), balance_carried (method).
- F-10 generic assembly sentences; F-11 tie/absent/first-match statements; F-12 interest rounding stated;
  F-13 docstrings; O-02 tool bodies enforce 2-decimal half-up positive amounts (static helper); seeds reproducible.

### Round 2 - items closed
- F-01 / T0-2 / T1-2: coinsurance days priced at what Medical Assistance bears (QMB crossover -> booked coinsurance; not QMB -> 0; no coverage -> daily rate); the resident's own share enters the pending advance as an incurred-medical-expense deduction (pending_projected_coinsurance). Year-price and Medigap-share factors removed (merged).
- F-02 / T0-1: P2 and P4 retire the base partial-month clause with sibling-naming replaced_by restating it for every other month; P1 is outside it (actual-notice months are not partial months).
- F-03: P5 standard = base estimate incl. VA protected amount and tier allowance (HMA within max months); base clause retired only for the advance.
- F-04 / T1-1: P3 and P5 retire the refund clause only for a fresh credit when a representative pays toward the coming month (credit capped at the month's figure); every other credit refunded under base (restated).
- F-05: every value-selecting ladder labelled parameter; methods redesigned: payee_benefit_applied (MX pick vs latest vs none), balance_carried (adds MN cap; credit tier differs from owed tier), projected_coinsurance (month days vs days-left input), unheld_leave_days (declined span vs released span), days_outside_stay (admission vs departure, departure reachable on pending cases through a bed-hold ended by a hospital discharge elsewhere); leave-day compound condition dropped.
- F-06: coinsurance fall-through is the Medicaid daily rate only where no Medicare coverage booked Part A days; held-day limits read the booking reservation's tier (CPARAM reserved days), no condition couples reserved days to private days.
- F-07: amount_kept reads only the funds-account tier (and case tier), payee benefit is in the standard so it moves alone (T2 2210.50); selections not duplicated.
- F-08: coming-month patient pay is plain (notice in effect, base); allowance is base in P5.
- F-09: skilled admission = coverage start of the booking coverage when equal to its qualifying discharge (no private-pay start date).
- F-10: one generic assembly sentence per policy. F-11: absent actual-charge branch stated; LATEST by service month where the rule says so; Medicare coverage read through the booking's coverage id or status active; funds account status active; declined/released holds stated as the first listed; payee tie rule stated. F-12: interest third rounding stated. F-13: docstrings rewritten (no fixed-reason claim, no ordering words); O-02 bodies enforce positive half-up cents via _Ledger.cents and render two-decimal strings.
- T0-4 / T1-4 / O-01: billed estimates now equal the base formula on the case figures (T1 1073.70 exactly; T0 2245.90 = approval figures). O-06: no pending accrual owed (documented). O-07: bed-hold charges posted on the statement day of the following month.
- O-03/O-05: prerequisite effects worded generically; P2's trueup replaced_by restates the base reconciliation for other months.

### Round 2 - probe table (probe.py, scratch)
| policy | decoy / absent record | result vs gold | verdict |
|---|---|---|---|
| actual cost cap / reconciliation | second Medicare episode (closed, QMB) listed first | unchanged | coverage read through the booking's coverage id |
| actual cost cap / reconciliation | booking of an earlier month | unchanged | month filter |
| actual cost cap | hospital_day reversal (not uncertified) | 0.00 (day priced as Medicaid day) | stated rule: only lapsed-certification reversals out |
| reconciliation | second declined hold of another month listed first | 1958.54 | rule reads the first listed declined hold (stated) |
| actual cost cap | bed-hold day reversed | unchanged | bookings counted by service month (reversals carry none) |
| actual cost cap | no October booking | 0.00 | held days then count (fall-through) |
| reconciliation | earlier estimate month | unchanged | latest by service month |
| approved advance | two payee benefits same day (tie) | unchanged | larger of latest and others |
| approved advance | no payee benefit | 2115.72 | benefit none, pension still applied |
| approved advance | second closed funds account listed first | unchanged | status active |
| approved advance | refund on the case | 382.22 | refunds count in the balance |
| pending cost cap | earlier closed Medicare episode listed first | unchanged | booking coverage id |
| pending cost cap | released hold of another month | unchanged | release date month test |
| pending advance | second closed coverage | unchanged | status active |
| pending advance | older reduction | 176.38 | balance includes it; latest reduction date unchanged |
| pending advance | no interest credit | 177.10 | fall-through 0 |

### Round 2 - T1 / T2 per factor (eval_t*.py, t2.py)
| factor | T1 (own world, alone at baseline) | T2 (alone live, others at baseline) |
|---|---|---|
| actual_coinsurance_day_price | 234.38 -> 0.00 | 28 coinsurance days, not QMB: 0 -> 234.38 |
| actual_part_a_days_out | -> 0.00 | 20 full + 4 uncertified: 0 -> 234.38 |
| actual_held_day_limit | -> 0.00 | 24 days on a private-pay hold: 0 -> 234.38 |
| actual_unheld_leave_days | -> 0.00 | 24 days after a declined hold: 0 -> 234.38 |
| reconciled_* (same law) | 809.10 / 0.00 / 1671.18 / 1958.54 / 1671.18 | same constructed worlds |
| approved_payee_benefit_applied | 332.22 -> 2051.52 | 2165.50 -> 446.20 |
| approved_authorized_pension | -> 548.22 | -> 1949.50 |
| approved_amount_kept | -> 287.22 | -> 2210.50 |
| approved_balance_carried | -> 275.20 | -> 2222.52 |
| pending_coinsurance_day_price | 1073.70 -> 0.00 | 28 coinsurance days: 0 -> 234.18 |
| pending_part_a_days_out | -> 514.02 | 20 full + 8 uncertified: 0 -> 234.18 |
| pending_held_day_limit | -> 793.86 | 28 private-hold days: 0 -> 234.18 |
| pending_unheld_leave_days | -> 793.86 | 28 days after a declined hold: 0 -> 234.18 |
| pending_days_outside_stay | -> 0.00 | admission 2026-10-29: 0 -> 234.18 |
| pending_projected_coinsurance | 177.38 -> 394.38 | 1073.70 -> 856.70 |
| pending_premiums_counted | -> 80.98 | -> 1170.10 |
| pending_interest_counted | -> 177.10 | -> 1073.98 |
| pending_funds_applied | -> 565.38 | -> 685.70 |
| pending_balance_carried_in | -> 565.38 | -> 685.70 |

### Round 2 - pairwise method-tier table (distinguishing input/operation)
- part_a_days_out: full+uncert vs full (adds uncertified reversal input) / vs uncert (adds band 1-20 input) / full vs uncert (different filters of one field: residual A.7 risk, recorded) / none.
- unheld_leave_days: declined (leave_start..return of the declined reservation) vs released (release_date..return, minus the release day) vs both (sum) vs none (domain includes worlds with holds outside the month, where the other formulas are nonzero).
- days_outside_stay: admission (DAYS first..admission) vs departure (DAYS departure..month end) vs both vs none (domain includes admissions before the month: other formulas nonzero).
- payee_benefit_applied: MX(latest, others-in-month) vs nothing (payments stopped; domain carries older benefits) vs latest.
- balance_carried / pending_balance_carried_in: +owed balance vs -MN(credit, month figure) vs nothing (domain includes old credits).
- projected_coinsurance: month days x rate x share vs days-left x rate x share (different input) vs none (domain includes ended coverages with days left).
- Scratch sweep: every compute_basis quote, baseline sentence, replaced_by and policy_source verbatim in its rule; no factor binding reads another factor's binding (sweep.py: 0 misses).
REWORK round 2: gates 7/7 green

## REWORK round 3 (audit revision_2) — item-by-item

Design decisions (cost-of-care family P1 actual-month review, P2 estimate reconciliation, P4 pending-month review):
- Standard pricing (baseline) now carries the Part A rule a new hire is given: full-coverage days (benefit days 1-20, net of
  reversals) carry no cost, coinsurance days (21-100, net) carry the highest daily coinsurance booked for the month; every other
  day at the Medicaid daily rate. Factors only vary that standard.
- Calendar-month exactness: XCOUNT/XSUM windows are rolling (MONTHS() day-adjusted), so no month test uses windows; every month
  read is an exact service_month filter, a single own-holding field, or a latest-by-date read guarded by an exact scope test.
- P1 does not retire the partial-month clause: a month carrying a partial_month charge or in which the case closed on discharge or
  death stays under it (P1 posts nothing; that clause, in force, reduces the charge). A leave with no bed held ends the stay and the
  return is a readmission (bed-hold readmission_right_after_hold), i.e. such months are partial months. Other unscoped months are
  computed exactly under the base cost clause: (calendar days - booked held days) x rate.
- P2/P4 scope = census identity: days in the center counted by the month's pending accrual + booked held days (net of reversals on
  the one reservation) + the latest declined/released spans + days before a skilled admission + days after a discharged-elsewhere
  bed's last held day = calendar days, and the month's held days on one reservation. Any second/absent/unrecognised record breaks
  the identity -> the month is priced exactly under the base rule at the accrual's days in the center x rate (P4 cap; P2 actual
  patient pay = lesser of notice amount and that cost). Base forces the accrual definition: "the days in the center times the
  private daily rate of the occupied room" (medicaid_evt_pending_balance), so accruals count every day in the center.

Items:
- R2-F-02 (P1 vs partial-month clause): P1 now names partial months (partial_month charge, case closed on discharge/death, leaves
  with no bed held) as staying under the in-force partial-month rule and posts no reduction for them (compute: result 0); P1 no
  longer conflicts and retires only the cost clause. Cost-clause siblings P1/P2/P4 carry ONE identical scope sentence naming the
  three cases; partial-month siblings P2/P4 carry one identical sentence restating the clause verbatim.
- R2-F-05: part_a_days_out is now a parameter (values: lapsed-certification days; days after the last covered date of a coverage
  under a timely review; both; none) - full-coverage days moved into the standard pricing, so no tier is a filter of the same sum
  over a nothing tier. coinsurance_day_price now has three operative values: 0 (coinsurance billed to the Medigap carrier/resident,
  none as crossover), the Medicaid daily rate (crossover with booked coinsurance above it), the booked coinsurance (fall-through =
  standard); the vacuous tier is gone.
- R2-F-06: held_day_limit removed. Replaced by *_privately_held_days (method): the reservation carrying the month's held days (one
  reservation by exact test) - a hold the resident pays in full -> leave start..last held day; a Medicaid reserved bed with a private
  extension -> private hold start..last held day; otherwise none (reserved days count; patient pay unchanged). Uses the bed-hold
  tier parameter resident_pays_all_held_days, the hold's own dates; no allowance re-derived. P5 funds tier 2: the latest payee
  benefit less the personal needs allowance (the allowance stays with the resident).
- R2-F-07: P5 credit cap now reads base_estimate (plain, the base estimate figure) - no factor in its chain. P3: one plain
  funds_tier / funds_authorization pair stated once ("The resident's funds account is the resident's account in status active");
  amount_kept reads the trust tier parameter medicaid_pna_retained.
- R2-F-09: admission no longer from the latest coverage episode alone - a skilled admission (latest coverage start = its
  qualifying discharge) is used only where the census identity holds; two-episode months, non-Medicare admissions, and any
  double-counted day break the identity -> base. Discharge elsewhere now counts days after the bed's last held day (end_date), so
  held days and departure days never overlap.
- R2-F-10: P3 and P5 assembly sentences generic (each schedule states where its figure enters; no factor quantity named); P5
  overwrite 1 replaced_by now "the base estimate figure as the schedules below change it".
- R2-F-11: declined/released holds read latest-by-date (leave start / release date), departure latest by end date, ties "the one
  posted first"; misreads (second record, later record) break the census identity -> base. P5 latest booked coinsurance filtered
  to the active coverage (plain active_coverage); premiums and days-left reads use the same id.
- Observations: O-06 closed (pending accruals seeded: task 0 September 25 days x 398.00 = 9950.00 posted 09-30, settled
  approved_ma_covered on the 10-02 approval; task 1 October 24 days x 398.00 = 9552.00, pending balance 9552.00). P3 framing clause
  about a "correction" removed. P3 VA payee: kept amount is the PNA only (VA amount is not paid into a payee account); new tier
  keeps PNA + the tier's allowances (community spouse / family / home maintenance) the payee pays out of the benefit.
- New P1 factor actual_unbillable_days_after_coverage (method; medicare base: "Without a delivered SNF ABN the center may not bill
  the resident for that care"): no notice recorded -> every day after the last covered date; notice delivered after its first
  non-covered date -> the days before delivery; otherwise none.

World changes: task 0 - released hold of 10-21 removed (October now a whole month); October Part A 22 days (benefit 26-47),
coinsurance 1193.50/3580.50, Plan L payment 3255.00, uncertified moved to 10-20/21 (recertified 10-22), Sept uncertified 09-18
(initial recertification late), covered_days_used 44, coinsurance_balance 1085.00; SNF ABN delivered 10-26 for 10-25 (option 2);
approval 2026-10-02, October charge billed 10-02; September accrual + settlement. Task 1 - October accrual, pending balance.
Gold: P1 521.74, P2 2245.90, P3 44.86 (task 0); P4 1073.70, P5 177.38 (task 1).

T1 / T2 table (T1 = own world, factor alone at baseline; T2 = producible world, factor alone off baseline, all others at baseline;
T2 world for cost caps: a month with 20 full-coverage days and notice patient pay 3500.00, plus 6 coinsurance days for the
coinsurance factor):
| factor | T1 gold -> baseline | T2 alone vs all-baseline |
|---|---|---|
| actual_coinsurance_day_price | 521.74 -> 0.00 | 2063.20 vs 761.20 |
| actual_part_a_days_out | 521.74 -> 0.00 | 913.76 vs 339.04 |
| actual_unbillable_days_after_coverage | 521.74 -> 234.38 | 626.40 vs 339.04 |
| actual_privately_held_days | 521.74 -> 0.00 | 913.76 vs 339.04 |
| reconciled_coinsurance_day_price | 2245.90 -> 1160.90 | 2350.56 vs 1048.56 |
| reconciled_part_a_days_out | 2245.90 -> 1958.54 | 913.76 vs 626.40 |
| reconciled_privately_held_days | 2245.90 -> 1671.18 | 1201.12 vs 626.40 |
| reconciled_unheld_leave_days | 2245.90 -> 1958.54 | 913.76 vs 626.40 |
| reconciled_days_outside_stay | 2245.90 -> 1671.18 | 1201.12 vs 626.40 |
| approved_payee_benefit_applied | 44.86 -> 1764.16 | 446.20 vs 2165.50 |
| approved_authorized_pension | 44.86 -> 260.86 | 1949.50 vs 2165.50 |
| approved_amount_kept | 44.86 -> 0.00 | 2210.50 vs 2165.50 |
| approved_balance_carried | 44.86 -> 275.20 | 1935.16 vs 2165.50 |
| pending_coinsurance_day_price | 1073.70 -> 0.00 | 2100.80 vs 798.80 |
| pending_part_a_days_out | 1073.70 -> 514.02 | 981.44 vs 421.76 |
| pending_privately_held_days | 1073.70 -> 793.86 | 701.60 vs 421.76 |
| pending_unheld_leave_days | 1073.70 -> 793.86 | 701.60 vs 421.76 |
| pending_days_outside_stay | 1073.70 -> 0.00 | 1820.96 vs 421.76 |
| pending_projected_coinsurance | 177.38 -> 394.38 | 856.70 vs 1073.70 |
| pending_premiums_counted | 177.38 -> 80.98 | 1170.10 vs 1073.70 |
| pending_interest_counted | 177.38 -> 177.10 | 1073.98 vs 1073.70 |
| pending_funds_applied | 177.38 -> 565.38 | 685.70 vs 1073.70 |
| pending_balance_carried_in | 177.38 -> 565.38 | 685.70 vs 1073.70 |

Pairwise method-tier table (distinguishing input per pair; "none" = fall-through, checked non-zero for the other formulas on its domain):
| factor | pair | distinguishing input / operation |
|---|---|---|
| *_privately_held_days | pays-in-full vs private-extension | leave_start_date vs private_hold_start_date |
| | pays-in-full vs none | none-domain (Medicaid reserved, no extension): leave start..last held day > 0 |
| | private-extension vs none | none-domain: private start falls back to leave start -> held days > 0 |
| actual_unbillable_days_after_coverage | no notice vs late notice | last_covered_date to month end vs first non-covered date to delivery date (ABN entry_date, from_date) |
| | no notice vs none | none-domain (notice on time / ended elsewhere): days after the last covered date != 0 |
| | late notice vs none | none-domain: delivery minus first non-covered date != 0 (on-time notice gives a negative span) |
| *_unheld_leave_days | both vs declined-only / released-only | adds the other reservation's span (release_date vs leave_start_date) |
| | declined vs released | leave_start_date..return vs release_date+1..return |
| | either vs none | none-domain spans of out-of-month or absent records are non-zero (unclipped tier formulas) |
| *_days_outside_stay | both vs admission-only / departure-only | adds the other date input |
| | admission vs departure | coverage_start_date vs bed-hold end_date |
| | either vs none | none-domain DAYS(first day, latest coverage start) / DAYS(last held day, next month) non-zero |
| approved_payee_benefit_applied, approved_balance_carried, pending_projected_coinsurance, pending_balance_carried_in | unchanged from round 2 (MX / MN cap on non-factor bindings) | |
(parameter factors: coinsurance_day_price, part_a_days_out, authorized_pension, amount_kept, premiums, interest, funds - distinct operative values, no shape test)

Decoy / absent-record probes (scratch copies, probe3.py):
| read | probe | outcome |
|---|---|---|
| P1 month's held reservation | second reservation with private days in October | one-hold test fails -> base (calendar - held) x rate, result 0.00 |
| P1 ended coverage | later coverage ended 2026-11-03 | coverage test fails -> base, 0.00 |
| P1 partial month | partial_month charge in October | result 0 (partial-month rule) |
| P1 advance notice | delivered on/before first non-covered date | none tier -> 234.38 |
| P1 advance notice | absent | no-notice tier, 7 days -> 2245.90 |
| P1 coinsurance payer | crossover charge present | price 217.00 (booked, below rate) |
| P1 lapsed / appeal | no coverage under_appeal; reversals of other months | month filter; appeal tier off |
| P2 declined leave | second declined leave in September, accrual 24 (consistent) | identity fails -> base, 0.00 |
| P2 declined leave | later declined leave in November | span 0, identity fails -> base |
| P2 declined leave | same-date duplicate (tie) | posted-first read, same 2245.90 |
| P2 accrual | absent | out of scope, days in center = calendar days -> base |
| P4 admission | coverage start not equal to qualifying discharge (non-Medicare admission) | identity fails -> base 0.00 |
| P4 declined leave | return absent | span to month end, identity fails -> base |
| P5 booked coinsurance | closed decoy coverage with later-posted 209.50 block | filtered to active coverage, 217.00 kept |
| P3 funds account | second account closed | status='active' filter |
| P3/P5 payee/pension/interest deposits | other-month / older deposits | windows and latest-by-date as round 2 (unchanged) |

Sweeps: compute_basis quotes, replaced_by, superseded clauses, baseline sentences and prerequisite sentences verbatim - 0 misses
(scratch sweep). Cost-clause replaced_by identical across P1/P2/P4; partial-month replaced_by identical across P2/P4. Stale-text
sweep of design_rationale, prerequisite_closure, necessity/objective/traces, seed_consistency: old figures (234.38, 2011.52, 332.22,
57.02, 09-29, 10-15/16, released hold, held_day_limit, latest booking, booking coverage, capped at the estimate, "no pending accrual")
removed; prerequisite conditions now "the month's cost of care" (no world values). Tool bodies/docstrings unchanged (contracts
unaffected).

Gates (full suite): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 3: gates 7/7 green

## REWORK round 4 (audit revision_3) — item-by-item

- R3-F-02 (P1 self-contradiction): P1 no longer calls a leave with no bed held a partial month. Its standard pricing takes out
  every day away with no bed held, counted EXACTLY for any number of leaves: for each kind (declined from the leave start;
  released from the day after the release; expired from the day after the last held day; each to the day before the return or
  the month's end) the compute counts reservations by exact date (XCOUNT on each day string of the month and of the following
  month, plus the totals and the unreturned count) and sums the days away; disjointness of one resident's leaves makes the sum
  exact (probe: two declined leaves in October + one in November + an expired hold returning 10-03 -> 1 + 2 + 2 = 5 days).
  P1 posts nothing only for a month the partial-month rule has settled or a record marks as discharge/death: a partial_month
  charge, a cost_of_care_cap reduction already posted, the case closed on discharge or death, the latest-ended Medicare coverage
  ended on discharged_from_center / hospital_transfer_no_return / resident_deceased, or a held bed's last held day where the
  hospital discharged the resident elsewhere. Base sentence that forces the remaining edge (a discharge or death of a resident
  with no coverage, bed-hold or partial-month entry and an open case): medicaid_case_maintenance "An eligible case is closed only
  when its patient pay balance and pending balance are both zero." - the medicaid records hold no other discharge record.
- R3-F-05 (part_a_days_out x3): removed. Lapsed-certification days (medicare base: provider liable) are now in the standard
  pricing of all three reviews with the full-coverage days. Replacement factors:
  P1 actual_hospice_share_start (parameter: a date - the month's first day where the hospice was elected before the month, the
  election date inside the month, none otherwise; from it the Medicaid days are priced at the tier's room-and-board share,
  base parameter hospice_room_board_pct_of_nf_rate, 42 USC 1396a(a)(13)(B));
  P2/P4: the round-3 unheld factor split into two real method factors - *_declined_hold_days (declined leave from its start;
  a reservation that ended with the payer's reserved days used and no private extension, from the day after its last held day)
  and *_released_hold_days (released reservation from the day after the release; a private hold ended unpaid or at its maximum,
  from the day after its last held day); both are guarded by the census identity (all four spans in it).
  *_privately_held_days relabelled as a parameter *_privately_held_start (a date: leave start / private hold start / none)
  feeding a fixed span formula, giving P1, P2 and P4 two parameters each.
- R3-F-06 (realism of unbillable days): removed. New P1 method actual_days_after_coverage follows the medicare base text:
  under an SNF ABN with option 1 or option 2 "the resident pays" for the continued care (those days are the resident's private
  days, not Medicaid days); while a timely expedited review is pending "the resident is not billed" (Medicare liability being
  decided); option 3, no notice or no ending -> none (the normal Medicaid takeover). Spans stop before a hospice election.
- R3-F-09 overlaps: (a) appeal days exist only in P1 and P1 prices a month only where the held reservation's last held day falls
  before the after-coverage span and before a hospice election inside the month, and no day away with no bed held falls in a
  month with an after-coverage span; (b) same guard; (c) P2/P4 price a month only where every Part A day of the month was booked
  by the coverage with the latest coverage start (two-episode months go to the base rule); unscoped months are computed exactly.
- Observation (Sept benefit numbering): unchanged base ambiguity; the reconciliation still prices 0.00 either way.
- Coordinator rulings: every half-up rounding in compute is RND(x + 0.000000001, 2) on non-negative values; task_tools.py rounds
  with an exact Decimal half-up helper; no scored, baseline or sensitivity figure is within 1e-6 of a half cent.

World changes: task 0 - September 21-100 block 4 days (09-24/25/29/30), the 09-26 Medicare-stay hold released 09-27 (back
09-29), September accrual 24 days (9552.00, settled); October Part A 21 days to the last covered date 10-23 (NOMNC 10-21,
recertified 10-19, no lapse), SNF ABN 10-21 option 1 for 10-24, hospice elected 10-25 (case on the Hospice Room and Board tier);
coinsurance and Plan L payments recomputed; covered days 44. Task 1 - the 10-18 home visit removed; 10-26 hospital stay on a
Medicare-stay hold released 10-27 (back 10-29); October Part A 22 days (benefit days 49-70, prior 48), accrual 22 days (8756.00).
Gold: P1 334.96, P2 2245.90, P3 231.64; P4 1073.70, P5 177.38.

T1 / T2 (T2 on scratch worlds: copies of the task worlds with records changed so only the named factor leaves its fall-through):
| factor | T1 gold -> baseline | T2 scratch world: result vs factor at baseline |
|---|---|---|
| actual_coinsurance_day_price | 334.96 -> 0.00 | coinsurance billed to the resident: 626.40 vs 0.00 |
| actual_hospice_share_start | 334.96 -> 234.38 | hospice elected 10-25 (full-coverage month, charge 3500.00): 726.98 vs 626.40 |
| actual_days_after_coverage | 334.96 -> 47.60 | option-2 notice for care from 10-24: 2925.28 vs 626.40 |
| actual_privately_held_start | 334.96 -> 0.00 | private-pay hold 10-08/09: 1201.12 vs 626.40 |
| reconciled_coinsurance_day_price | 2245.90 -> 1377.90 | coinsurance billed to the Medigap carrier: 1775.84 vs 907.84 |
| reconciled_privately_held_start | 2245.90 -> 1671.18 | Medicare-stay hold 09-26/27, accrual 28: 1482.56 vs 907.84 |
| reconciled_declined_hold_days | 2245.90 -> 1958.54 | declined leave 09-15..17, accrual 28: 1482.56 vs 907.84 |
| reconciled_released_hold_days | 2245.90 -> 1958.54 | Medicaid reserved bed released 09-21, back 09-24, accrual 26: 1482.56 vs 907.84 |
| reconciled_days_outside_stay | 2245.90 -> 1671.18 | skilled admission 09-03, accrual 28: 1482.56 vs 907.84 |
| approved_payee_benefit_applied | 231.64 -> 1950.94 | second payee deposit 64.20: 446.20 vs 2165.50 |
| approved_authorized_pension | 231.64 -> 447.64 | self-directed account with authorization, pension 216.00: 275.20 vs 446.20 |
| approved_amount_kept | 231.64 -> 186.64 | Medicaid payee account, no authorization: 491.20 vs 446.20 |
| approved_balance_carried | 231.64 -> 275.20 | November charge unpaid: 2692.10 vs 446.20 |
| pending_coinsurance_day_price | 1073.70 -> 0.00 | coinsurance billed to the resident: 1820.96 vs 0.00 |
| pending_privately_held_start | 1073.70 -> 514.02 | private-pay hold 10-26/27, accrual 29: 2380.64 vs 1820.96 |
| pending_declined_hold_days | 1073.70 -> 793.86 | declined leave 10-22, accrual 30: 2100.80 vs 1820.96 |
| pending_released_hold_days | 1073.70 -> 793.86 | Medicaid reserved bed released 10-21, back 10-24, accrual 27: 2380.64 vs 1820.96 |
| pending_days_outside_stay | 1073.70 -> 0.00 | skilled admission 10-06, accrual 26: 3220.16 vs 1820.96 |
| pending_projected_coinsurance | 177.38 -> 394.38 | active Plan K coverage, 2 days left: 856.70 vs 1073.70 |
| pending_premiums_counted | 177.38 -> 80.98 | active coverage with 100 days used, no card forwarded: 1170.10 vs 1073.70 |
| pending_interest_counted | 177.38 -> 177.10 | 0.28 interest credited 10-31: 1073.98 vs 1073.70 |
| pending_funds_applied | 177.38 -> 565.38 | standing authorization with a 388.00 pension: 685.70 vs 1073.70 |
| pending_balance_carried_in | 177.38 -> 565.38 | November estimate unpaid: 2147.40 vs 1073.70 |

Pairwise method-tier table (methods only; parameters choose values/dates):
| factor | pair | distinguishing input |
|---|---|---|
| actual_days_after_coverage | ABN option 1/2 vs pending review | ABN from_date (first non-covered date) vs under_appeal coverage's last_covered_date |
| | either vs none | none-domain (option 3 / no notice): spans from those dates are non-zero |
| *_declined_hold_days | declined vs ran-out | leave_start_date vs end_date+1 of a payer_days_used_no_extension reservation |
| | both vs single | adds the other reservation's span |
| *_released_hold_days | released vs private-ended | release_date+1 vs end_date+1 of an unpaid/max reservation |
| *_days_outside_stay | admission vs departure | coverage_start_date vs bed-hold end_date |
| P3/P5 methods | unchanged from round 3 | |

Probes (scratch copies): P1 later option-3 notice on the same coverage -> none tier 47.60; same-date second notice (tie) -> posted
first, unchanged; declined leave 10-28..30 with an after-coverage span -> out of scope, base; later declined leave in November ->
not counted in October; October + November declined leaves -> October days counted exactly; election date on file but case not on
the hospice tier -> no share; cost_of_care_cap already posted -> 0; coverage ended on death -> 0; coverage under a timely appeal ->
review tier. P2 later released hold in November -> identity fails -> base; ran-out reservation with an unchanged accrual ->
identity fails -> base; second coverage episode starting 09-20 -> bookings test fails -> base. P4 accrual absent -> base at every
calendar day; second declined leave with a consistent accrual -> identity fails -> base.

Sweeps: compute_basis quotes, replaced_by, superseded clauses, baseline and prerequisite sentences verbatim (builder asserts and
check_extended); cost-clause replaced_by identical across P1/P2/P4, partial-month replaced_by identical across P2/P4. Stale-text
sweep of design_rationale, prerequisite_closure, objectives/necessity/traces, seed_consistency: round-3 figures and dates removed;
prerequisite conditions carry no world values.

Gates (full suite): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 4: gates 7/7 green

## REWORK round 5 (audit revision_4) — item-by-item
- R4-F-02 (P1 settled-partial test missed a funds-account record): P1 now also posts nothing for a month in which the resident's
  funds account records a discharge or death as the start of conveyance (trust_accounts.conveyance_trigger_date with
  conveyance_reason discharged or deceased, latest by trigger date per reason, any account of the resident). Rule sentence
  extended; trust added to P1's cross_category reads. Probes: conveyance on discharge 10-05 -> 0 (settled); conveyance in another
  month -> priced as before; a second, closed funds account with a death conveyance 10-12 -> 0.
- R4-F-09 (hospice share overlap): P1 prices a month with a hospice election inside it only where no Part A day is booked on or
  after the election day (latest booked to_date of the month), no day away with no bed held falls in the month, the held
  reservation ends before the election (round 4) and any after-coverage span starts before the election; otherwise the month is
  computed exactly under the base rule. Probes: election 10-10 with Part A booked to 10-23 -> base; declined leave 10-27..29 after
  the 10-25 election -> base; advance notice naming 10-27 after the 10-25 election -> base; seeded world unchanged (priced).
- T1/T2: unchanged figures; actual_hospice_share_start re-checked on the scratch full-coverage world (726.98 vs 626.40, others at
  baseline) under the new guard. Sweeps: compute_basis quotes verbatim (assert), stale text: task 0 step 8 necessity now names the
  conveyance check; design rationale header round 5.
- Gates (full suite): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 5: gates 7/7 green

## REWORK round 6 (audit revision_5) — item-by-item
- R5-F-02 (latest-record recognition of a month of discharge; members conveyance_discharged_on / conveyance_deceased_on,
  discharged_elsewhere_last_held, coverage_left_center) - coordinator DSL route applied: the actual-month review now covers only a
  resident who holds exactly one funds account and exactly one Medicare coverage episode, each counted in every status (sums of
  exact-status XCOUNTs over trust_accounts and medicare_coverages), and no bed-hold reservation ended because the hospital
  discharged the resident elsewhere (exact XCOUNT on end_reason). Plain record test in the rule, no purpose clause; for any other
  resident the review posts no reduction and the partial-month rule and the base cost-of-care rule apply as restated. Inside the
  scope the conveyance read and the ended-coverage read are single-record; the discharged-elsewhere read is dropped (none in
  scope). Tie rule stated as before ("the one posted first").
- Probes: second funds account (closed, with a 10-05 discharge conveyance) -> out of scope, 0; second account in status declined
  -> out of scope; no funds account -> out of scope; second coverage episode (not_eligible, or an active readmission episode) ->
  out of scope; no coverage episode -> out of scope; an old discharged-elsewhere hold -> out of scope; one account with a 10-05
  discharge conveyance -> in scope, settled partial month, 0; seeded world -> in scope, unchanged.
- T1 unchanged (task 0 world in scope: one account, one coverage, no discharged-elsewhere hold); T2 scratch worlds are copies of the
  task 0 world with the same single account and coverage, so they stay in scope (round-4/5 T2 figures hold). Stale text: task 0
  design rationale overrides line names the scope; header round 6. Other policies unchanged.
- Gates (full suite): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 6: gates 7/7 green

## REWORK round 7 (render_source render_r1: M1, M2, S1-S4) — item-by-item, whole class swept
- M1 (P5 pending_funds_applied floor): the rule and ladder now say the payee benefit less the personal needs allowance is "never
  below zero" (compute MX kept). Class sweep of every floor/cap: P1 days in the center of an unpriced month and the days away with
  no bed held now state "never fewer than zero"; all other MX/MN already stated (Medicaid days, estimate floors, base estimate,
  credit caps, funds total, advance, lesser-of actual patient pay, hospice days capped by the share days).
- M2 (P1 hospice share, inside-the-month branch): rule now reads "where the case is on that tier and the hospice election date
  falls inside the month" (= ladder and compute).
- S1 (P5 grouping): "100 less the larger of 20 and the total of the benefit days already used ... and the days from the first day
  of the current month to the first day of the coming month"; prior SNF days "none where not recorded".
- S2 (tie sentences): P3 and P5 now carry "Where two records share the latest date a schedule reads by, the one posted first is
  read." (LATEST/XLATEST keep the first row met = posted first, as in P1/P2/P4).
- S3 (P2/P4 tie broken differently): rule now states "Where a hold that ended unpaid and one that ended at its maximum share the
  latest end date, the one that ended unpaid is read" - exactly the compute's choice.
- S4 (P3 coming patient pay edges): rule states "or nothing where the case carries no estimate charge either; a current notice with
  no effective date recorded counts as taking effect after the first day of the coming month". Same class in P2 notice patient pay:
  rule and compute now both treat a missing effective date as taking effect after the month's first day.
- Class "branch conditions stated in the rule": status gates the rules named but compute did not apply are now computed and
  stated - P2 (status eligible), P3 (status eligible), P4 (status pending), P5 (status pending): any other status gives nothing.
  Other unstated edges now stated: P5 missing requested eligibility date (allowance months from the coming month), missing booked
  coinsurance (nothing), case figures not recorded count as zero (P3 allowances, P5 figures).
- Probes: P2/P3 on a pending case -> 0; P4/P5 on an eligible case -> 0; P5 payee benefit 30.00 -> funds 0; P1 election inside
  the month on the standard tier -> no share; P3 notice without effective date -> latest actual charge; P2 the same -> October
  charge; P3 notice after the coming month with no charges -> nothing; P2 unpaid and maximum holds with equal end dates -> unpaid
  read. Gold and every factor_sensitivity figure unchanged (COMPUTE OK); T2 scratch worlds unaffected (statuses eligible/pending).
- Sweeps: compute_basis quotes and baseline sentences verbatim (asserted); stale text: none of the changed sentences is quoted in
  task proof text.
- Gates (full suite): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 7: gates 7/7 green

## REWORK round 8 (policy_kb revision_1: SRC-3; SRC-1/2/4 placement notes not routed; SRC-5 trust-conditional; KB-1..4 renderer-side)
- SRC-3: the pending refund overwrite (P5, replaced_by and rule) now applies the credit "up to the base estimate figure" - the same
  cap pending_balance_carried_in states and computes (MN(credit, base_estimate)). Class sweep: the approved refund overwrite (P3)
  said "the figure that month will carry"; it now reads "up to the patient pay the coming month will carry", the cap
  approved_balance_carried states and computes (MN(credit, coming_patient_pay)). No other overwrite states a cap. Compute unchanged,
  gold and sensitivities unchanged (COMPUTE OK); no proof text quoted the old phrase; compute_basis and replaced_by verbatim
  (asserted).
- Gates (full suite): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 8: gates 7/7 green

## REWORK round 9 (policy_kb revision_3: SEED-1..6, SRC-6; bounded exhaustive seed pass against published docs)
- SEED-1 (class: hospital absences vs the interrupted-stay window, both tasks): each Medicare-stay hospital leave that kept one
  episode was three midnights. It is now two midnights, with the resident back by the third day, and the hold is released the day
  it began. Task 0: hold 1431d92d starts and is released 09-26, back 09-28, 1 held day (398.00, paid by check 10-20). Task 1: hold
  0342fd8c starts and is released 10-26, back 10-28, 1 held day (398.00, open). The single-episode scope and the "latest coverage"
  tests stay honest: one episode, no new coverage. Knock-on records:
  - Task 0, September Part A: days_21_100 block of 5 days (benefit days 21-25), coinsurance 271.25 / 813.75 (Plan L 25/75) and
    their payments. covered_days_used 45. September accrual 25 days x 398.00 = 9950.00, with settlement 9950.00.
  - Task 1, October Part A: 23 days (benefit days 48-70; prior SNF days 47), 2495.50 per party. covered_days_used 21,
    coinsurance balance 4557.00. Accrual 23 days = 9154.00, pending balance 9154.00.
- SEED-2 (class: standing trust transfers and their Medicaid mirrors): standing transfers now post on the charge's due day (the
  10th), for the published memo amount.
  - Task 0: the October transfer is 1954.50 on 10-10 (2245.90 less the 291.40 ACH that already names it, within 1999.50 less the
    45.00 allowance). The rep_payee_transfer mirror is now dated 10-10. The November transfer falls due 11-10, after the frozen
    time, so it and its mirror were removed. Case balance 4491.80.
  - Task 1: the November transfer (due 11-10) was removed. The November Medicaid payment is now the daughter's 250.00 check on
    11-03, and the October ACH is dated 10-12. Funds balance 1568.28, case balance 823.70. The persona now says she sent 250.00
    toward November and the rest is open.
- SEED-3: task 0 October block numbered benefit days 25-45. With September at 20 + 5 booked less the 09-18 lapse (24 net), the
  docs now produce 25-45, so the row stands as published.
- SEED-4 (class: coinsurance charge vs reversal timing): task 1's uncertified reversal (10-20/21) and its two 217.00 coinsurance
  adjustments are now posted 11-02, after the 10-31 charge, so the 23-day charges plus adjustments are what the Medicare record
  test produces. Task 0 has no same-day reversal against a charge: the 09-18 reversal is 10-01, after the 09-30 charges.
- SEED-5 (class: held-day booking dates): each booking is posted the day the leave ends (task 0 09-28 and 10-10, task 1 10-28).
- SEED-6: task 0 trust_resource_notice rows were added. 10-03 at 1999.50 and 11-03 at 2044.65, the balance the Medicaid-tier
  notice level was reached at; neither is read as a deposit (probe). Task 1 is a Non-Medicaid tier, so no notice is owed.
- SRC-6: BLUEPRINT-KNOWN, between the two frozen base charters. The medicaid base "representative payee transfer day" (5th)
  conflicts with the trust base standing-authorization transfer "on the charge's due day" (10th). Seeds follow the published trust
  rule. P3 no longer lists rep_payee_transfer_day among its baseline params (the only extended-yaml change); no extended rule states
  a transfer day.
- Seed pass (every cross-product row in both worlds, re-priced by docs/medicare, docs/bedhold, docs/trust; all match):
  - Task 0 medicare:
    - coverage c93e594f: Plan L, ended 10-23, 45 used
    - d3815e80: days 1-20, 09-03..09-23
    - 2025814d: 09-18 reversal, 10-01
    - c1c29e78: days 21-25, 09-24..09-30 less the 09-26/27 leave
    - 891e49e7 / 2e7b7dee: 271.25 / 813.75
    - e71b8a2d / d520c52b: payments
    - db36f95c: days 25-45, 10-01..10-23
    - b19c1599 / aef07b1d: 1139.25 / 3417.75
    - 2fb5ace0: SNF ABN option 1, 10-24
    - 93b946d4: carrier remittance
  - Task 0 bedhold:
    - 72ee55a1: declined 09-15
    - 1431d92d: 09-26, released 09-26, back 09-28
    - b4dd9c19: 10-08/09, back 10-10
    - ledger: 6fdf0269, 8a13a8d6, 9e24c001 (1 day, 09-28), f331a9f6 (398.00), a034e0be (398.00 check), 91d1307b,
      d63f40f0 (2 days, 10-10), 144833d2 (796.00)
  - Task 0 trust:
    - account d74bfc32: balance 2108.85
    - deposits: efe11799 / 3aab3841 (pension 216.00), 5ebdc1ad / 103c6e98 (payee 1783.50), 8c9648b1 (64.20)
    - 5c635bf5: transfer 1954.50 on 10-10
    - 016b3769: interest, ADB 497.37, (497.37 - 50.00) x 0.4% x 31/365 = 0.15
    - 206810de / 7bf3bcc1: notices
  - Task 1 medicare:
    - coverage aa39092a: Plan K, prior 47, 21 used
    - e59be17b: days 48-70, 10-06..10-31 less 10-22 and 10-26/27
    - f6f4f530: reversal 11-02
    - cc663e57 / 7f087265: 2495.50 each
    - 32885e84 / dadd99b5: 217.00 each
  - Task 1 bedhold:
    - 9e439811: declined 10-22, back 10-23
    - 0342fd8c: released 10-26, back 10-28
    - ledger: ce934d5e, 83a92da1, 068e1af1 (1 day, 10-28), f85a88e5 (398.00)
  - Task 1 trust:
    - account 41a5c955: balance 1568.28
    - 8884e533: family check 1180.00
    - aef5a134: interest, ADB 913.55, (913.55 - 100.00) x 0.4% x 31/365 = 0.28
    - 72b3a666: pension 388.00, no transfer before 11-10
- Scored values moved: P3 (task 0 advance) and P5 (task 1 advance), because the case balances they carry changed. P1, P2 and P4
  did not move. Gold args, expected and baseline_result, every factor_sensitivity, the factor traces, prerequisite flips and
  skipped effects (task 0: skip A 2521.10, skip B 4432.04; task 1: skip 1389.08), business effects, persona (task 1), objectives,
  tracings, seed_consistency and design_rationale were regenerated from the ev harness. P2 privately_held_start T1 is now 1958.54.
  P3 approved_balance_carried now takes the "owed" tier.
- T1/T2: T1 equals the factor_sensitivity values (COMPUTE OK).
  - P2, P3 and P5 hold T2 on their own worlds (each factor alone live vs all-baseline differs).
  - P1 and P4 hold T2 on scratch copies with the month's charge raised to 12000.00:
    - P1: 9126.40 / 4669.98 / 4856.76 / 5144.12 vs 4569.40
    - P4: 9761.28 / 5484.12 / 5484.12 / 5484.12 / 6603.48 vs 5204.28
- Probes:
  - Notices removed, or set to 99999.00: P3 unchanged.
  - Task 1 without the 250.00 check: P5 = 565.38 (balance 0).
  - Released hold back one day later: released days out = 2 in both tasks.
- Sweeps: compute_basis / policy_source quotes are verbatim in the extended yaml (asserted). Stale-token scan of all proof,
  rationale, closure, trace and persona text is clean (old balances, accrual days, benefit days, hold dates, gold, skip figures).
- Rounding ruling unchanged: RND(x + 1e-9, 2), residue DSL-KNOWN. task_tools.py unchanged.
- Gates (full suite, after replay write-back): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK,
  GROUNDING OK, SCOPE OK.
REWORK round 9: gates 7/7 green
