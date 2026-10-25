# plan — personal_loan_servicing (category loan), M=2

Draw (scripts/draw_counts.py --tasks 2):
- task 0: prerequisite_problems=1, factor_counts=[6, 4]
- task 1: prerequisite_problems=3, factor_counts=[6, 4, 4, 5]

User-owned writes the blueprint allows in this line: authorizing a new recurring debit (AutoPay enrollment) and
consenting to a refinance (refinance application). Every other write (fees, waivers, quotes) is a service action.

## Task 0 — refinance into a longer term (Renee Calloway, OH, Grade C, frozen 2026-10-20)
Tree: R (root, user) <- Q (agent).  edge R<-Q value_input, state form.
- Q `loan_ext_refi_payoff_quote` (4 factors): refinance-purpose payoff quote, scored payoff_amount.
  factors: quote window anchor (method), rate split on an AutoPay change since paid-through (method),
  uncleared extra-payment hold (parameter), re-quote cushion days (parameter).
- R `loan_ext_refi_application` (6 factors): refinance application, scored amount_financed (grossed up from Q's payoff).
  factors: fee form for a loan that is itself a recent refinance (method), remaining-term reduction (parameter),
  installment loyalty credit (parameter), AutoPay history credit (parameter), FlexLine credit (parameter, cross line,
  multi-source), Credit Builder credit (parameter, cross builder).

## Task 1 — bounced AutoPay, courtesy waiver of the late fee (Kendra Ashby, NY schedule B, Grade B, frozen 2026-09-24)
Tree: C (root, agent) <- L (agent), F (agent), A (user).  three value_input edges, state form; L, F, A commute.
- L `loan_ext_late_fee` (5): late fee for the installment left unpaid by the returned AutoPay debit.
- F `loan_ext_returned_fee` (4): returned-payment fee for the returned debit (cross line: same bank event).
- A `loan_ext_autopay_reenroll` (4): AutoPay enrollment on the new verified account, scored rate in force
  (completed Term Extension Modification base — cross hardship).
- C `loan_ext_courtesy_waiver` (6): courtesy waiver of the late fee, scored amount waived.

Gates per task, then final suite. Scratch: /tmp/personal_loan_servicing_0067/.
