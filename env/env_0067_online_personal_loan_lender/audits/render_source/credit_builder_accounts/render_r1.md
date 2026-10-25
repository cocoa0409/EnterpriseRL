# Renderer findings — product builder (d=credit_builder_accounts), render round 1 (saved verbatim by the coordinator)

Renderer agent ac44317da4685f756 scanned the source first and STOPPED with 0 documents written. Its report, verbatim:

All references are to `env/env_0067_online_personal_loan_lender/tasks/credit_builder_accounts/builder.extended.yaml` unless another file is named. The window findings depend on the compute helpers in `skills/erl-task-instantiate/scripts/check_compute.py`:
- `within_months` keeps a row when 0 ≤ `MONTHS(date, NOW)` < N, so a row dated today counts.
- `MONTHS` only counts a month once the same day of the month is reached, and never treats a shorter month's last day as that day.

**S1. `builder_ext_late_fee_charge`, factor `lf_base`: debit-card branch condition.**
- Rule: "Where debit card payments have been credited toward the late due date, the fee is figured on the monthly payment less the total of those debit card payments, net of every debit card chargeback (return code CB) booked on the account, instead of on the monthly payment, and never on less than zero." The next sentence opens "Where no debit card payment has been credited toward the late due date and that due date is the account's maturity date, …"
- Compute: `lf_dc_credit` is debit-card payments toward `next_due_date` less every CB return on the account. `lf_base` takes the debit-card branch only `if lf_dc_credit > 0`.
- Example: payments were credited but the net is zero or negative.
  - Net zero on the maturity due date: the rule gives the monthly payment less zero; the compute gives the final installment.
  - Net negative (a hypothetical 20.00 payment toward the due date and a 50.00 chargeback on an older one): the rule gives the monthly payment plus 30.00; the compute gives the monthly payment.

**S2. `builder_ext_returned_payment_fee_charge`, factor `rf_history`: `== 0` where the sibling policies use `<= 0`.**
- Rule: "When no payment on the account other than this one was returned in the 12 whole calendar months before today (…), the fee is multiplied by the first-return share."
- Compute: `rf_other_returns` is the 12-month count less 1, and `rf_history` is `K('first_return_share') if rf_other_returns == 0 else (… == 1 …) else K('full_share')`.
- Example: if the most recent return, not yet charged, is 12 or more whole months old, the count is −1. The compute then gives the full share (1.0); the rule gives the first-return share (0.5). `hl_first`, `hr_first`, `rr_first` and `gw_history` use `<= 0` and are fine.

**S3. Every "N whole calendar months before today / before the assessment date" window: unclear whether a row dated today counts.**
- The parentheticals pin only the far end ("a … dated on the same day of the month N months earlier falls outside them"). "Before today" reads naturally as leaving today out, but the compute counts rows dated today.
- The base measure did say this outright ("today and the 364 days before it"); the extended wording dropped it.
- Sharpest case, `builder_ext_goodwill_late_fee_credit` (`gw_used`). Rule: "when the plan's courtesy waivers have all been granted on the account in the 12 whole calendar months before today (…)". The goodwill credit is figured only after the made-good relief, and that relief books a courtesy waiver dated today.
  - Example: a plan with one courtesy waiver per 12 months, after a same-day made-good relief. The compute refuses the credit; the "excludes today" reading grants it.
- Same exposure:
  - `rr_used`.
  - `lf_prior_late` and `lf_returns`: "returned in the 3 whole calendar months before the assessment date", and a payment returned today is plausible on that day.
  - The 12-month counts `hl_other_late`, `rf_other_returns`, `rr_other`, `gw_other_late` and `ad_ap_returns`.
  - The cross-product counts: `ad_line_returns`, `ad_loan_returns`, `ad_loan_late`, `ad_pos_returns`, `ad_pos_late`, `gw_loan_late`, `rr_line_n`.

**S4. Month-end convention of "open N months or more" is not stated (`MONTHS(open_date, NOW)`).**
- Affected sentences:
  - `lf_pct`: "that has been open 12 months or more … open fewer than 12 months".
  - `hl_season` and `rr_season`: "An account open 12 months or more … one open at least 6 months …".
  - `rf_seasoning`: same wording.
  - `gw_tenure`: "An account open 24 months or more … at least 12 but fewer than 24 months …".
- Examples where the compute disagrees with the end-of-month reading:
  - Opened 2025-08-31, today 2026-02-28: `MONTHS` gives 5, so the account is not "open at least 6 months", though the six-month mark is arguably 2026-02-28.
  - Opened 2024-02-29, today 2025-02-28: `MONTHS` gives 11.
- The rule never says when a month counts as complete if the opening day is missing from the later month.

**S5. `builder_ext_goodwill_late_fee_credit`, factor `gw_base`, second tier.**
- Rule: "When no payment was returned in that month but an AutoPay debit was presented toward the due date the late fee is for, the credit is figured on the late fee plus every returned-payment fee charged in the 3 whole calendar months before today."
- (a) Conflicting definition of "AutoPay debit". The same policy defines it by amount ("A goodwill credit for a borrower whose AutoPay debit (a returned payment whose amount equals the monthly payment) …"). `gw_autopay_toward` instead counts posted payments with `payment_channel='autopay_ach'`. A one-time payment equal to the monthly payment toward that due date is an AutoPay debit by the rule's definition but not by the compute.
- (b) Window boundary defined elsewhere. This "3 whole calendar months before today" window has no same-day boundary note. The only one ("(a return dated on the same day of the month 3 months earlier falls outside them)") sits in factor `gw_autopay`'s sentence, and a factor document may not borrow from another. The prerequisite sentence's 3-month window has no boundary note either.

**S6. Tool docstring contradicts the rule in an edge case.**
- `task_tools.py`, `confirm_early_closure_8372931d`: "savings_applied_amount: … a positive amount with 2 decimal places".
- `builder_ext_early_closure_settlement` rule: "When the savings applied come to 0.00, the early closure is still confirmed with nothing applied to the loan."
- This is likely unreachable, since an active account has a loan balance above zero, but the two disagree.

**S7. `builder_ext_early_closure_settlement`: day counts not pinned (lower severity).**
- (a) Count convention. "the calendar days from the oldest unpaid due date through the closing date" has no stated rule, unlike the base's "counted in calendar days starting the day after …". The compute uses `DAYS(next_due_date, NOW)`, the plain difference. A from-through reading could add one day.
- (b) Factor `cc_lead`, second tier. Rule: "the interest days count 30 days for each whole monthly payment past due before the oldest unpaid due date". The compute uses `int(amount_past_due / monthly_payment) * 30`, which includes the oldest unpaid installment itself. "Before the oldest unpaid due date" could also be read as leaving that installment out, which gives 30 days fewer.

I'm only noting, not raising, the stale base parameter texts the brief says to carry unchanged, for example `closing_interest_method` "days from the last due date paid through the closing date".
