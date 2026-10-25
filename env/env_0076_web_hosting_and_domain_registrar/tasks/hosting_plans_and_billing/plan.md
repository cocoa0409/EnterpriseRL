# plan — hosting_plans_and_billing (env_0076), M=2
Draw: task0 prereq=1 factor_counts=[5,4]; task1 prereq=1 factor_counts=[4,5].

## Constraints found in base (drive the design)
- Trigger rule: charges paid by account_credit and refunds to account_credit trigger account:*; hosting_sla_credit
  ALWAYS triggers account:account_service_credit -> never written. Payments card/paypal only; refunds to
  original_payment_method only.
- Cancellation / withdraw / reactivate / settings events carry no amount -> cannot be a problem (each problem needs a
  4-6 factor computation). Numeric writes in claim: renewal charge, upgrade charge, refund, service charge.
- Every tree needs an owner=user write -> the customer-own numeric writes are payments: the manual renewal
  ("a renewal the customer paid manually", base hosting_auto_renew_refund) and the upgrade purchase.
- value_input edges that exist in base: renewal -> upgrade (term dates, paid amount), auto-renew refund/rollback ->
  upgrade (term dates, paid amount), auto-renew refund -> renewal.

## Design (v2, final)
- task0: root = upgrade billed by the agent (5 factors); prereq = overdue renewal paid by the customer by hand
  (owner=user, 4 factors). Plan in renewal grace (term ended, still active, 3 declined auto-renew attempts).
  Edge upgrade -> renewal, value_input on the term dates/paid amount, state form ("term end date after today").
- task1: root = early renewal paid by the customer (user, 5 factors) <- auto-renew refund (agent, 4 factors); state form, negated.
Scratch: /tmp/hosting_plans_and_billing_0076/ ; verification scripts there.
