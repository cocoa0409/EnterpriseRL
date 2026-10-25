# Renderer findings — product loan (d=personal_loan_servicing), render round 1 (saved verbatim by the coordinator)

Renderer agent a673a272ce9be7205 scanned the source first and STOPPED with 0 documents written. Its report, verbatim (line numbers refer to loan.extended.yaml at that time):

**1. `loan_ext_courtesy_waiver`: five factors only take effect through a sixth factor (the five point factors feed the waiver form).**
- Rule (3027-3029): "the waiver form decides how the amount waived is taken from the unpaid part; the courtesy share is courtesy_share_base plus every courtesy point that applies, added together and then held between zero and one".
- `c_share: "MN(1, MX(0, K('courtesy_share_base') + c_pt_autopay + c_pt_load + c_pt_depth + c_pt_pos + c_pt_reason))"` is a non-factor binding, yet only `courtesy_waiver_form` uses it (`result`, forms 1 and 2). The baseline is "The courtesy waiver covers the whole unpaid part", which never uses a share.
- So the five point factors (`autopay_restored_point`, `fee_load_point`, `installment_record_point`, `practicepay_point`, `return_reason_point`) change the result only through the waiver-form factor.
- Rendering is impossible either way. If the share definition goes in the computation document, that document must mention "courtesy points" and stops being silent about factors. If it goes in the waiver-form factor document, that document names the other factors. A point-factor document alone ("adds X to the courtesy share") modifies nothing in the computation document.

**2. `loan_ext_courtesy_waiver`: `c_fee_due` is a non-factor binding defined only by a factor's sentence.**
- `c_fee_due` (3101) is in no factor's bindings, so the computation document would have to cover it.
- Its `compute_basis` (3128) is the return-reason factor's sentence, "when it is dated on or after the due date of the installment the waived fee was charged for", and only `c_pt_reason` reads it.

**3. `loan_ext_autopay_enroll` departs from in-force base sentences without an `overwrite`.**
- Base `loan_evt_autopay` (1602-1604), not retired: "it never applies on top of a rate set by an active hardship plan or Servicemember Rate Cap Benefit - while such a plan is active the plan rate governs".
- Base `loan_cmb_hardship_and_benefits` (1906-1907): "A plan that sets its own rate (plan_interest_rate not empty) replaces the AutoPay-discounted rate while it is active".
- The extended `result` (2902) always sets rate base less discount and steps. Its rate base reads only a completed Term Extension Modification, so enrolling while a Temporary Rate Reduction Plan, a Servicemember benefit or a Term Extension Modification in trial is active yields two contradictory rates.
- Minor, same policy: the rule says "when the pre-plan interest rate equalled the base interest rate, the rate base is the modified rate itself", but the compute uses `a_tem_pre_rate >= a_base_rate` (2893). The rule never covers a pre-plan rate above the base rate.

**4. `loan_ext_returned_fee`: the first-return share breaks when the return being charged is old.**
- Rule (2677): "no returned payment on the loan in those months other than the one being charged".
- Compute (2715): `f_other_returns_12m: "COUNT(... within_months=12 ..., event_type='loan_payment_returned') - 1"`.
- If the latest returned payment (the one being charged) is 12 or more whole months before assessment, the count is -1. The share then drops to 1, whereas the rule grants `first_return_share_full` or `first_return_share_partial`. The rule itself allows late, catch-up returned-payment fees, so this case can arise.

**5. Window boundary not pinned in two first-time shares.**
- `loan_ext_late_fee` (2457): "looking at the 12 whole calendar months before the late fee's assessment date: no late fee charged on the loan in those months and 12 or more net installment payments in them".
- `loan_ext_returned_fee` (2676): "looking at the 12 whole calendar months before the returned-payment fee's assessment date".
- The compute (`within_months=12`, i.e. 0 ≤ months < 12) excludes a row dated exactly 12 whole months earlier. "The 12 whole calendar months before" reads naturally as including it. Every other window in the charter uses the unambiguous "fewer than N whole calendar months before".

**6. One convention sentence serves several factors, in all six policies.**
- The sentence is "Whole calendar months between two dates are the difference in calendar months, less one when the later date's day of the month is smaller than the earlier date's, so a month whose matching day does not exist is not yet complete on its last day." It appears once per rule.
- `loan_ext_refi_payoff_quote`: `compute_basis` homes it on `q_returns_12m` (hold factor). The cushion factor (`q_requotes`) and the issuing scope (`q_pt_recent`, `q_enroll_2m`, `q_cancel_2m`, `q_extra_1m`) also need it. The day-count convention "(quote date minus paid-through date)" likewise sits only in the baseline sentence, while the window and day-rate-split factors rely on "the days from A to B".
- `loan_ext_refi_application`: homed on `r_refi_age`; also needed by the payment-record (24 months), AutoPay (12 months) and FlexLine (12 months) credits.
- `loan_ext_autopay_enroll`: homed on `a_loan_months`; also needed by the debit-record step.
- `loan_ext_courtesy_waiver`: homed on `c_last_courtesy`; also needed by the fee-load and PracticePay points.
- `loan_ext_late_fee` and `loan_ext_returned_fee`: not quoted by any `compute_basis`, yet four factors in each depend on it.
- This is lower severity than items 1–5: the skill tolerates a repeated definition, so it could be rendered by restating the sentence in each document. Your brief lists it as a defect class, so I'm reporting it for your call.

**7. Minor wording edges.**
- `loan_ext_refi_application` (2185): "That amount is rounded to the cent and then rounded up to the next whole dollar." The compute is a ceiling (`int(r_needed) + (1 if r_needed > int(r_needed) else 0)`), which leaves an exact whole-dollar amount unchanged; "next whole dollar" can be read as adding one.
- `loan_ext_autopay_enroll`: the rule says "the borrower enrolls in person", while the `enroll_autopay_4dda8507` docstring says it "Records one AutoPay enrollment on the loan, dated today, by phone". A rendered page would show both and read as contradictory.
