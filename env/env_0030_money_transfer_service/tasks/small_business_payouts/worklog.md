# small_business_payouts — instantiate worklog

- draw (--tasks 2): task 0 -> 1 prerequisite problem, factor counts [5, 6]; task 1 -> 3 prerequisite problems, factor counts [4, 5, 4, 4].
- task 0 closed: business_ext_period_subscription_charge (collect_overdue_subscription_325cf5bc, agent, 5 factors, 199.75)
  -> root business_ext_downgrade_termination_charge (schedule_plan_downgrade_6c5bcb1c, owner, 6 factors, 212.11).
  Per-task gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- headroom for task 1: balance withdrawal (owner), extra seat charge, upgrade proration settlement, return charge.
- task 1 closed: root business_ext_withdrawable_balance (withdraw_business_balance_ad66ed9d, owner, 5 factors, 22,853.39)
  <- business_ext_mid_period_seat_charge (charge_extra_seats_0d292d98, 4 factors, 6.67)
  <- business_ext_upgrade_proration_settlement (settle_upgrade_proration_4280c277, 4 factors, 69.55)
  <- business_ext_card_deposit_fee (charge_card_deposit_fee_e69fd8f7, 4 factors, 154.00); all edges value_input on the balance, state form.
- final gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK.
  check_traceability pending the published KB.
- round 2 (audit env/env_0030_money_transfer_service/audits/policy_task/small_business_payouts/):
  F-G1 fixed (past-due conjunct removed from months_charged_basis tier 1: rule, ladder, compute, basis; task 0 trace/sensitivity/tracing/rationale);
  acted on O-G2 (annual branch), O-G3 (loyalty fall-through), O-G4 (no charge outside commitment), O-G5 (incentive tier 2), O-G9 (card prerequisite sentence scope),
  O-T0-1/2/3 and O-T1-4 (rationale), O-T1-1 (KYB document rows in both tasks). Scored values unchanged. All gates green; traceability pending KB.
