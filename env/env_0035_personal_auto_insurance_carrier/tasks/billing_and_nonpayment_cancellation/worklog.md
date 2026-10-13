# Worklog — billing_and_nonpayment_cancellation (category billing, M=2)

## Draws (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=3, factor_counts=[5, 6, 4, 5]
- task 1: prerequisite_problems=1, factor_counts=[5, 4]

## Difficulty pre-check
- Writable billing events whose triggers stay inside billing: billing_installment_billed, billing_fee_charged,
  billing_fee_waived, billing_payment_received, billing_credit_applied, billing_endorsement_charge,
  billing_refund_issued, billing_writeoff, billing_plan_change, billing_payment_setup_update, billing_close.
- Excluded for task tools: billing_notice_of_cancellation (triggers billing_notice_issue -> auto:auto_cancel_pending),
  billing_notice_issue, billing_rescind, billing_cancel_nonpay, billing_reinstate (all trigger auto writes).
- Any policy whose subject includes billing_fee_charged inherits the late-fee grace gate (grace_elapsed), so only the
  late fee itself is claimed on that subject.
- Customer-owned writes in this line: payments from the customer's own card/account (and the no-loss statement,
  unusable here because reinstatement cannot be written).

## Task 0 (claimed)
Tree: root assisted payment (user) <- late fee charge, renewal down payment invoice, additional-premium bill (all
value_input, state form). Factor counts: assisted payment 5, late fee 5, renewal down payment 6, AP bill 4.
Tools: charge_late_fee_8c3b3141, bill_renewal_down_payment_49af2eee, bill_additional_premium_a7869908,
pay_balance_by_phone_6aa6e134 (owner=user).

Gold: late fee 3.80 (installment 6), additional-premium bill 96.38 (due 2026-10-20), renewal installment 1 515.23
+ policy fee 20.00, assisted payment 713.05 incl. representative fee 1.93 (debit_card). The three prerequisites commute
(all six orders replayed: identical values and terminal DB). Skip effects on the root: 709.25 / 616.56 / 178.41.
Revision: after task 1 claimed the installment-charge policy, task 0's seeded installment fees (flat 8.00) were
recomputed with it and every dependent payment, the 2025-08-05 notice minimum and the opening balance re-derived.

## Task 1 (claimed)
Tree: root term payoff (user, pay_term_payoff_2a94a5fa) <- installment charge on the installment 4 invoice
(invoice_installment_259ff7d9), value_input, state form. Factor counts: installment charge 5, payoff 4.
Gold: installment 4 premium 129.99 + charge 3.61 (due 2026-08-24); payoff 400.27 by bank_eft. Skip effect: 399.04.

## Closing
Coverage: 6 extended policies, task 0 = 4, task 1 = 2, disjoint; 6 task tools, each used by exactly one task.
Full gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (suite means branches 41.00,
steps 13.00; history max 104; branches max 52), GROUNDING OK, CACHE-DIFF INFO, SCOPE OK. check_traceability pending
the KB render. Per-task dossiers live in each task's design_rationale.

## Rework round 2 (audits/policy_task/billing_and_nonpayment_cancellation)
- F1 / T0-1: renewal rule now defines the expiring full-term premium as the billed term's full-term premium as last
  rated (latest auto additional/return premium transaction's full_term_premium_after in the term, else the term premium
  entry); compute reads it via XLATEST. Task 0 renewal premium re-seeded to 2148.70 (offer of 2026-09-20 quoted 1358.96
  before the driver add). Renewal down payment 649.39; assisted payment 847.37 (fee 2.09).
- T0-2: task 0 persona no longer names the renewal or its down payment.
- F3 / T1-1, F2 / O4, O5: payoff carries no installment fee; standard credit stated in the baseline; tenure rate
  replaces the prepaid-fee share; rule and persona no longer promise "nothing more to pay". Payoff 391.35.
- O1: no-fee-on-cure branch implemented. O2/O3: late fee tied to the installment whose grace just ended; baseline
  sentence says "standard". O6: tool returns say "resulting balance". O7: KY tiers 9.50 / 2.50 / 4.50; task 1 history
  re-seeded (installment 4 charge 3.42). O8: kept (weight-bearing, see reply). O9: raw parameter tokens replaced.
