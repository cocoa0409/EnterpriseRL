# plan — employer_instant_pay_disbursements (category disburse), M=2
Draw (draw_counts.py --tasks 2):
- task 0: prerequisite_problems=1 (2 problems), factor_counts [4, 6]
- task 1: prerequisite_problems=3 (4 problems), factor_counts [5, 6, 4, 4]

Identifier band: phones 6465550100-199; tax_id_last4 3000-3999; other stated numbers start with 3;
surnames I-L; employer names first word I-L.

DSL constraints found (check_compute.py): history windows are whole months back from NOW (MONTHS<N);
filters exact-value only (keyword values may be expressions); no calendar-month aggregates;
single-date month/day tests via MONTHS against epoch literals; string compare/concat allowed.
Consequence: per-disbursement fees (calendar-month allowance position) and volume reviews are not
computable; rich computations available in this product: closure/early-closure fee, platform fee,
replenishment debit, employer funding deposit, alert-level election, (withdrawal).

Trigger rule: payouts are never written (card:card_load trigger); seeded payouts go only to
external_debit_card / bank_account; no tool writes a row whose base trigger lands in another category.

## Task 0 — closing the service (2 problems)
- ROOT disburse_ext_closure_fee (owner=user): the employer's own closure confirmation, booking the
  closure and its same-category consequence, the early closure fee (owner_ruling (a)). 6 factors.
- PREREQ disburse_ext_closing_month_fee (agent, state_due once closure requested): platform fee of
  the month in which the closure falls, debited before closure. 4 factors.
- Edge: value_input (early closure fee rests on the platform fee last debited).
- Tier Growth (minimum term 12), young service (< 3 complete months -> no volume review owed).
- Cross-difficulty: program agreement (EWA) / paycard program holding fields.

## Task 1 — funding shortfall (4 problems)
- ROOT disburse_ext_funding_deposit (owner=user): employer-initiated ACH credit restoring the funding level. 6 factors.
- disburse_ext_replenish_debit (agent, state_due): automatic replenishment debit. 5 factors.
- disburse_ext_platform_fee (agent, state_due on fee debit day): last month's platform fee. 4 factors.
- disburse_ext_alert_election (owner=user): employer's alert level election at the floor (changes the
  terms of its ACH debit authorization). 4 factors.
- Tier Core (auto replenish allowed), employer_ach_credit funding (no wire fee owed afterwards).

Status: both tasks closed; full final gate block green except check_traceability (only the six unlock tool names, expected before KB render).
