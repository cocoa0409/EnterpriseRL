# plan.md — meal_account_and_benefits (env_0078), M=2  (instantiator; revision 3)

## Draw (draw_counts.py --tasks 2)
- task 0: prerequisite_problems=3 (4 problems), factor_counts=[5,5,5,5]
- task 1: prerequisite_problems=3 (4 problems), factor_counts=[5,6,6,5]

## Thin-charter finding (recorded)
Only meal_transactions.amount is a computable numeric write among the claimed events (deposit, refund,
transfer_out/in); each computation reads one meal account (plus declared enroll reads). Factors use the
published NSLP prices by campus level / CEP (enrolled campus = cross-difficulty enroll), the district's
2026-27 calendar, the account's purchases, uncleared check / card deposits, returned checks and the
repayment-plan terms; plan terms beyond size and returned checks are tagged R6 (AMENDMENT 1).

## Task 0 — Ferreira household (frozen 2026-10-21 10:15:00 CDT)
root P0 meals_ext_prepayment_quote  USER deposit_meal_prepayment_ffe018a7 (Lucia, Ridgecrest MS)   5
  <- P1 meals_ext_departed_charge_cover  transfer_departed_charge_cover_80639818 (Tomas inactive -> Lucia), on Lucia  vi (action)  5
       <- P2 meals_ext_sibling_idle_netting transfer_idle_sibling_balance_b810dc58 (Mateo, Pecan Grove CEP -> Lucia), on Mateo vi (action) 5
  <- P3 meals_ext_inactive_repayment  USER pay_inactive_meal_installment_c0dba3e7 (Rafael inactive, owes)  sg (state)  5
 gold (r4): netting 6.15, cover 85.45, repayment 22.45 (USER), prepayment 88.80 (USER)

## Task 1 — Oyelaran household (frozen 2026-10-22 14:40:00 CDT)
root Q1 meals_ext_cep_balance_refund (Esther, Cypress Hollow Elementary = CEP in 2026-27) agent  5
  <- Q2 meals_ext_collection_repayment USER (Samuel, active-account repayment plan) sg (action) 6
  <- Q4 meals_ext_graduate_rollover (Grace graduated 2026-05-28 -> Samuel), on Samuel, sg (action) 6
       Q4 <- Q2 vi (action)
  <- Q3 meals_ext_departure_rollover (Daniel moved_out_of_state -> Samuel, youngest non-CEP student), on Samuel, sg (action) 5
       Q3 <- Q4 vi (action)
 gold (r5): repayment-plan payment 17.64 (USER), graduate rollover 76.96, departure rollover 88.80, CEP refund 20.40

## Status
- Round 1 and round 2: superseded (see worklog.md).
- Revision 3 (REWORK round 3): every computation rebuilt; both tasks rebuilt.
- Revision 4 (REWORK round 4): coordinator ruling O-12 applied (forecast at the parent's stated purpose); one serving-day count per computation; methods on milk and second meals; final gate block run; see worklog.md.
- Revision 5 (REWORK round 5): P-01r, P-08, P-09, F-07 and the task-1 persona item closed; task 0 figures unchanged; see worklog.md.
- Revision 6 (REWORK round 6): renderer findings F1-F4 closed; figures unchanged; see worklog.md.
