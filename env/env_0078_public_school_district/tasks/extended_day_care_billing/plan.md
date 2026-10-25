# plan — extended_day_care_billing (category care), M=2

## Draw (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=3 (4 problems), factor_counts=[5,4,4,4]  -> >=2 value_input edges
- task 1: prerequisite_problems=1 (2 problems), factor_counts=[4,5]      -> >=1 value_input edge

## DSL limits found (decisive for design)
- compute reads only this care holding (F), its own event/intake tables (SUM/COUNT/MAX/LATEST, eq filters,
  within_months from NOW), and OTHER categories (CFIELD/CPARAM/EXISTS/X*). customers/students tables and
  the household's other care enrollments are NOT readable.
- => sibling position (household care portfolio) and the employee flag (customers) cannot be recomputed.
  Route: tuition-type quantities are re-pricings of a POSTED charge, which keep the sibling position and
  proration recorded on that charge as plain record inputs; the employee case is carried by taking the
  larger of the recorded rate basis discount and the meal-status discount (never lowers a charge).
- no date construction in DSL -> every scored value is money.
- the only customer numeric write in the charter is care_payment (owner=user per owner_ruling (b), PCI portal).

## Task 0 (Okafor household) — "past-due notice, pay the Creek Kids Club account off online today"
root R0 = care_ext_balance_payoff (owner=user, care_payment.amount)  [4 factors]
  <- A0 care_ext_rate_reprice_credit (agent, care_credit billing_correction on the mis-rated tuition month) [5]  value_input
  <- B0 care_ext_late_pickup_fee (agent, care_late_pickup_fee for a chargeable late pickup with no fee entry) [4] value_input
  <- C0 care_ext_late_fee_review_credit (agent, care_credit billing_correction on a late payment fee the
        re-priced tuition shows was not owed / owed at a lower stage) [4]  value_input (C0 <- A0 value_input too)
  topological order: A0, C0, B0, R0 (B0 commutes with A0/C0: disjoint rows, proved by replay)
cross-difficulty: meals (student's meal account status + effective date; household meal benefit application)

## Task 1 (Lindqvist household) — "registration hold: last year's Extended Day balance; pay it so I can register"
root R1 = care_ext_prior_year_settlement (owner=user, care_payment.amount on the closed 2025-26 enrollment) [4]
  <- D1 care_ext_notice_period_credit (agent, care_credit notice_period_adjustment on the final billed month) [5] value_input
cross-difficulty: enroll (district withdrawal / enrollment record), meals

## Factor sketch (to be finalised in the yaml; realism notes in worklog)
A0 reprice: meal-status discount (param, cross meals, multi-source OR household application), holiday-month
   rate (param, billing month), autopay tuition credit (param, ACH history), first-month proration method
   (method, waitlist+start day), late-start ... (see yaml)
B0 late pickup: per-minute rate by semester record (param), billing increment by lateness (method),
   after-hours surcharge (param), ... (see yaml)
C0 late-fee review: fee stage by unpaid-after-due-day (param), small-balance tier (param), measure of unpaid
   (method), ... (see yaml)
R0 payoff / R1 settlement / D1 notice credit: see yaml.

## Settled T0 design (on disk in care.extended.yaml)
- P1 care_ext_meal_rate_tuition_credit [4]: meal_status_discount(param,cross,multi-OR), status_count_date(method), holiday_month_share(param), recorded_sibling_discount(param)
- P2 care_ext_late_pickup_fee_schedule [5]: per_minute_rate_ladder, billing_increment(method), after_hours_charge, pickup_hardship_share(cross,multi-AND), notice_stage_charge
- P3 care_ext_late_fee_reassessment [4]: charge_size_base_fee, unpaid_amount_scale(method), repeat_month_addition, late_fee_hardship_share(cross)
- R0 care_ext_account_settlement_payment [4] owner=user: advance_share(multi-AND), advance_base_rule(method), advance_hardship_share(cross), autopay_relief
- edges: P3<-P1 (value_input, action), R0<-P1 (value_input, action), R0<-P2 (value_input, state), R0<-P3 (value_input, action)
- order: P1, P3, P2, R0. values: P1 51.84, P3 3.16, P2 70.00, R0 126.14 (frozen 2026-11-20 10:30:00 CST)

## Status
- [x] extended.yaml base copy + T0 policies
- [x] task_tools.py (T0 tools) + check_task_tools
- [x] tasks/0.json + per-task gates (all green; traceability: only unlock misses)
- [x] T1 policies/tools/tasks/1.json + gates (D1 40.00, R1 30.50)
- [x] XF_recipe tables in both worklogs; final gate block green except pre-render traceability (unlock tool-name misses only)

## REWORK round 2 (audit revision_1: task0=RED task1=RED; charter C-OVR-1,C-OVR-2,C-PRE-1,C-PRE-2,C-SCOPE-1,C-A1,C-A2,C-A6,C-A8,C-A9-1,C-REAL,C-COUNT)
Ruling: audits/render_source/realism_bar.md (R1-R5 accepted, X1-X4 struck). Design consequence applied: trees move off
rebates on posted charges (P1 meal re-price credit, P3 late-fee re-assessment, P4 advance) onto writes computed from raw
records whose published pricing has several keys.
New T0 (Okafor, active 2026-27 enrollment): root = current-year payment plan first payment (owner=user) [4];
  prereqs (all value_input, state form) = late pickup fee from the attendance log [4], late payment fee posted from the
  ledger [4], booked-day fee from a pending drop-in booking request [5].
New T1 (Lindqvist, closed 2025-26 enrollment): root = prior-year arrangement first installment (owner=user) [5];
  prereq = notice-period credit (value_input) [4].
Every factor R1/R2/R3/R5-shaped; no hardship cut on a penalty, no notice charge, no autopay, no tenure, no uplift;
A1 assembly-only coupling; A2 generic assembly sentences; A6 distinct method shapes; no re-pricing of posted components.
