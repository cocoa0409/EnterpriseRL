# worklog payment_arrangement_agreements (category arrange, M=2)

## Step 0 draw (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=1, factor_counts=[6, 4]
- task 1: prerequisite_problems=3, factor_counts=[4, 4, 4, 6]

## Step 0 pre-check findings (difficulty level)
- Holding = arrangements; every computation needs an EXISTING arrangement row at handling time (check_compute
  evaluates F/P/SUM on target_holding_id), so arrange_offer (create) cannot carry a scored computation; problems
  act on standing offers (offered) and running agreements (active).
- DSL date windows are month windows anchored on the handling date (within_months) plus equality filters;
  rules are written in those terms (billing_period equality, "the month ending on the handling date", N-month counts).
- Prerequisite value edges can only run between problems on the SAME agreement (SUM/COUNT/F are scoped to the
  holding); cross-agreement edges are state gates.
- User-owned writes in this charter: acceptance (offered->active) and early payoff. Task 0 takes payoff, task 1
  takes acceptance.
- Known deviation recorded honestly: the installment, payoff and default tools write arrange_ledger entries whose
  charter triggers derive a service-side bill line; the tools write only arrange tables and never the service row.

## Claimed scopes
- task 0 (Vance): root early payoff (user) <- missed installment booking (value_input).
- task 1 (Wexler): root balance transfer of a new agreement <- member acceptance (user, value_input) <- default of
  the member's other agreement (state_gate, portfolio history) <- installment billed on today's bill on that other
  agreement (value_input).

## task 0 closed
- policies: arrange_ext_missed_installment_amount (6 factors), arrange_ext_early_payoff_balance (4 factors)
- tools: book_missed_installment_8c48d67e (agent), pay_off_payment_agreement_d76d2954 (user)
- gold: missed installment 3 (2026-09) = 50.57; payoff = 134.45 (83.88 if the miss is skipped)
- per-task gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK
- fixes: helper functions in task_tools.py were read as tools -> inlined; empty-string FK values -> None;
  capital/deposit ledgers dropped (unread rows broke closure); ledger read widened to customer_id.

## task 1 closed
- policies: arrange_ext_installment_billed_amount (4), arrange_ext_default_rebill_amount (4),
  arrange_ext_acceptance_arranged_amount (6), arrange_ext_balance_transfer_amount (4)
- tools: bill_agreement_installment_2bd16d35, record_agreement_default_c78cb15c, accept_payment_agreement_6d07adca (user),
  move_balance_into_agreement_3b3ea9ff
- gold: installment 2 = 65.95; default rebill = 69.10 (183.59 without the installment); arranged on acceptance = 613.16;
  transfer = 359.27 (565.58 without the acceptance)
- revisions: missed rule generalised to "latest installment whose grace has ended" (tier grace differs); capital reads
  scoped to the service account's patron class; tenant check set to 229.99 to avoid a half-cent result.

## final gate run (no --task)
EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / CACHE-DIFF INFO / SCOPE OK
check_traceability.py not run: the KB for this difficulty is not published yet.

## round 2 (policy-task audit rework)
- D-F1/T0-F1: half-up rounding implemented exactly in every result binding; task 0 gold 50.58 / 134.46.
- D-F2/T1-F1: default no longer applies deposit, deposit interest or payable capital credits; new factors read latest-bill
  capital retirement and correction credits and a carried credit balance; task 1 default 105.37.
- D-F3 (T0-F2, T1-F4): window/count factors relabelled parameter; payoff window now in months (credit_window_by_circumstance).
- D-F4a/T0-F3: deposit-interest credit moved to the January bill (interest_payout_month 1); payoff window reaches it.
- D-F4b/T1-F5: deposit set-aside = next later installment per the deposit tier (90.00); seed holds the 180.00 first
  installment; task 1 arranged amount 605.66.
- T1-F2/T1-O1: persona believes the plan is set and asks only for the past due to go onto it; acceptance is a passive branch.
- T1-F3: transfer = arranged amount on acceptance less hold-backs (474.36; 512.71 without the acceptance); sentinel removed.
- Observations closed in passing: D-O2, D-O3, D-O4, D-O5, D-O6, D-O7/T1-O2, D-O9, D-O10, T1-O4.

## round 3 (policy-task audit rework, revision_2 findings)
- R2-F1 task 0: October capital-retirement credits (138.62 2026-10-01, 58.90 2025-10-01) removed; one 69.24 general
  retirement credit on the December 2025 bill (2025 resolution, bill credit, payment month 12); capital opened_date
  1997-06-30 (June allocation); credit_months_medical 10 -> 11 so the medical window reaches the December bill.
  Payoff 201.67 (151.09 without the miss).
- R2-F3 task 0: Credit Reestablishment Deposit per tier - reconnect_after_nonpay 2024-07-15, 460.00 in 3 installments,
  paid in full 2024-09-24, held 460.00, accrued_interest 0; January 2026 interest credit 9.52 (460 x 2.07%); monthly
  refund reviews from 2026-03-24 fail on 2+ late charges in the 18-month window. Balance 523.11.
- R2-F1 task 1: 22.40 October capital credit and the 46.30 Farm payable removed; capital rows dropped; default factor
  capital_credit_standing -> correction_timing_by_transfer; transfer factor capital_payable_held_back -> pledge_hold_by_age;
  2025 general retirement 142.51 seeded on the farm home's December 2025 bill (net payment 119.52).
- R2-F2: correction credits applied on both payment-record tiers, so all three correction_credit_share tiers are live.
- Deposit rows of task 1 (Farm usage_reassessment with reassessment_allowed false; tenant deposit held since 2015
  past every good review) removed; acceptance factor deposit_owed_set_aside -> down_payment_by_standing; 40.00 card
  payment 2026-10-05 seeded. Calls now at steps 8/10/12/14.
- R2-O1: `unbilled` compute_basis added to payoff and default.
- Gold: task 0 50.58 / 201.67; task 1 65.95 / 127.77 / 573.16 / 488.16.
- Gates (no --task): EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK /
  CACHE-DIFF INFO / SCOPE OK; check_traceability.py not run (KB not published).
