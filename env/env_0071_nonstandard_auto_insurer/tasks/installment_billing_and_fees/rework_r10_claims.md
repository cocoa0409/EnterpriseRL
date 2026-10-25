# Rework round 10 claims

Closed items (details in worklog.md, round 10 section):
- CG-30 (scope now enforced in compute, not only stated)

## Auditor probes re-run (scratch copies)

### Probe 1: deposit, task 0 post-notice world, frozen 2026-12-12. Payment A 100.00 on invoice 3 returned; payment B 227.36 on invoice 3 standing.
- Record test, rule: "This schedule covers such a plan only while its most recent installment invoice has at most one payment posted against it".
- Record test, compute: `dep_scope_ok: COUNT('billing_transactions', event_type='billing_payment_received', related_invoice_id=LATEST('billing_invoices','billing_invoice_id', ...)) <= 1`. The count is 2, so the test is False.
- Result: `result: (...) if dep_scope_ok else 0`, giving deposit 0.00. As the rule now states, no endorsement deposit is figured; a payment toward the additional premium is an ordinary one-time payment of the amount the customer states, applied in payment_application_order.

### Probe 2: deposit, the same world with A and B both returned.
- Excluded by the same test: two payments are posted against invoice 3, so `dep_scope_ok` is False.
- Result: deposit 0.00, priced by base as above.

### Probe 3: makeup, task 1 world with an earlier 50.00 payment on invoice 3, also returned.
- Record test, rule: "This schedule covers a payment returned ... whose installment invoice, if it had paid one, has no other payment posted against it ... a payment recorded against an invoice counts as another payment unless it is the returned payment itself or a makeup referencing it".
- Record test, compute: `mk_scope_invoice_ok: mk_returned_invoice == None or COUNT(payments on mk_returned_invoice) - COUNT(payments on it referencing mk_returned_payment) <= 1`. The count is 2 - 0 = 2, so the test is False and `mk_scope_ok` is False.
- Result: `result: (...) if mk_scope_ok else 0`, giving makeup 0.00. No makeup is figured; the payment is an ordinary one-time payment of the amount the customer states.
- The direct-bill switch and switch down payment carry the same test as their scope ("as the records stood when the move was asked"), so the move's makeup wait is never engaged on such a world.

Scored worlds remain in scope; both tasks' scored values are unchanged.

Carried, not regressed: every item closed in rounds 1-9.
