# premium_billing_and_grace — instantiate plan (M=2)

Draws (draw_counts.py --tasks 2):
- task 0: prerequisite_problems=1, factor_counts=[5,6]
- task 1: prerequisite_problems=2, factor_counts=[5,5,4]

Constraints noted: billing_reinstate / billing_lapse / billing_binder_expired trigger dental/vision/dhmo events
-> never written by any task tool. User-owned numeric writes available = customer payments only
(payment-method change, closure carry no number). Agent numeric writes = premium credits.

## Task 0 (household moved from AutoPay to Direct Bill after two returned bank payments; vision unit billed after its voluntary termination)
- root R0 billing_ext_grace_cure_payment (user tool submit_grace_cure_payment_5521c4c8; 5 factors)
  g_next(method), g_disc(param), g_fee(param), g_relief(param), g_hold(param, decides the held amount)
- prereq Q0 billing_ext_vision_term_credit (agent tool book_vision_term_credit_956578a0; 6 factors)
  vtc_month(param, multi-source), vtc_window(method), vtc_offset(method, cross vision), vtc_prior(param), vtc_int(param),
  vtc_recover(param, cross vision)
- edge R0 -> Q0 value_input on past_due, state form (credit posted against the coverage month of the invoice issued last).

## Task 1 (Annual Prepay household; son aged out 2025-11-30 with his rider; stale 2027 renewal invoice; renewal check returned; vision applied after the invoice)
- root R1 billing_ext_renewal_payment (user tool submit_renewal_payment_53926ce3; 4 factors)
  r_dental(param, dental, multi-source), r_rider(param, ortho), r_vbinder(method, vision), r_relief(param)
- prereq Q1b billing_ext_rider_end_credit (agent tool book_rider_end_credit_fb22198c; 5 factors)
  rc_months(method), rc_basis(param, multi-source), rc_dup(param), rc_int(param), rc_recover(param, cross vision)
- prereq Q1a billing_ext_dental_tier_credit (agent tool book_dental_tier_credit_2a6e4a9b; 5 factors)
  dtc_basis(param: prepay / exchange APTC / filed), dtc_window(method), dtc_dup(param), dtc_int(param), dtc_recover(param)
- edges R1 -> Q1a (negated 'not ... until'), R1 -> Q1b ('only after'); both value_input on bal, state form; credits commute.

Status: rework round 4 closed; full gate block green (see worklog.md).
