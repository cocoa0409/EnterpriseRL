# credit_builder_accounts — instantiation plan (M=2)

## Draws (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=3, factor_counts=[4,4,6,5]
- task 1: prerequisite_problems=3, factor_counts=[5,6,6,5]
=> 8 extended policies, each with its own task tool; 41 factors.

## Event budget (claimed builder event types with a scorable number)
late fee, returned-payment fee, early closure (+savings applied), payment, payment
allocation (interest portion of a posted payment), fee payment line, fee waiver,
closing-month dividend. Release is NOT a problem: CONF's rule pins release to no
earlier than the first business day after the closing date (so it is not owed on the call).

## Task 0 — early closure (Credit Builder 2400 Plan), root = CONF (owner=user)
- CONF builder_ext_early_closure_settlement (6 factors, on_request, user tool):
  borrower confirms the pending request; books closed_early + savings applied amount.
  waits on: late fee booked for every due date past grace (LATE, value_input, state form);
            returned-payment fee booked for every fee-bearing return (RET, value_input, state form);
            closing-month dividend credited through the closing date (DIV, state_gate, state form).
- LATE builder_ext_late_fee_charge (4 factors, state_due)
- RET  builder_ext_returned_payment_fee_charge (5 factors, state_due)
- DIV  builder_ext_closing_month_dividend (4 factors, state_due at closing)

## Task 1 — goodwill credit after catching up (Credit Builder 1800 Plan), root = WAIV
- WAIV builder_ext_goodwill_fee_credit (6 factors, on_request courtesy credit on a late fee)
  waits on: payments credited toward every past-due installment (PAY, state_gate);
            no unpaid returned-payment fee left on the account (FEEPAY, value_input).
- PAY  builder_ext_catch_up_payment (6 factors, owner=user): past-due installments + unpaid returned-payment fees.
- ALLOC builder_ext_payment_interest_split (5 factors): interest portion of the catch-up payment.
  waits on: the catch-up payment posted (PAY, value_input).
- FEEPAY builder_ext_fee_payment_from_payment (5 factors): part of the catch-up payment applied to the returned-payment fee.
  waits on: interest split booked on the payment (ALLOC, value_input).

## Task 1 — revised design (after budget analysis)
Event budget forced a change: a borrower-made catch-up payment cannot carry 5 load-bearing factors, so the
catch-up payment is seeded (made in the app this morning, allocation pending) and the tree is:
- WAIV builder_ext_goodwill_late_fee_credit (6, on_request, root): courtesy credit on the latest late fee.
  waits on: every posted payment split (ALLOC, state_gate); returned-fee relief booked (RRL, value_input);
            AutoPay enrolled (APDD, value_input).
- ALLOC builder_ext_payment_interest_split (5): interest portion of the pending catch-up payment.
- RRL builder_ext_returned_fee_relief (6, state_due): relief on the returned-payment fee once made good.
- APDD builder_ext_autopay_reenrollment (5, owner=user): borrower re-enrolls AutoPay; due day reset by rule.

## Round 2 rework plan (audit revision_1: CG-1..CG-8, task 0 findings 1-7, task 1 findings 1-8)
Redesign (both tasks rebuilt; factor floor and draws unchanged):
- Removed: builder_ext_closing_month_dividend (CG-2 deadlock, CG-4) and builder_ext_payment_interest_split (CG-1, CG-3, CG-4; its edge moved no scored value). Their tools are deleted.
- Task 0 [4,4,6,5] early closure: CONF root (user, 4: interest-paid-through anchor M, payment-relief hardship share, rate-setting hardship rate, ACH hold add-back), LATE (4, kept), HCRL early-closure late-fee relief (6, new), HCRR early-closure returned-fee relief (5, new). Edges: CONF<-LATE, CONF<-HCRL, CONF<-HCRR, HCRL<-LATE, all value_input (fees).
- Task 1 [5,6,6,5] goodwill: WAIV root (6), RRL (6), RET (5, moved from task 0, fresh one-time-payment return), APDD (user, 5, redesigned: return buffer as method proportional/flat/none, anchor relabelled parameter, reason R09/R01, FlexLine and loan buffers; AutoPay-history and stop-code tiers dropped). Edges: WAIV<-RET (vi), WAIV<-RRL (vi), RRL<-RET (vi), WAIV<-APDD (state_gate on WAIV's own AutoPay requirement, now scoped to borrowers whose AutoPay debit was returned so gw_autopay's not-enrolled tier is reachable).
- Charter-wide classes: no AutoPay-linked interest cut anywhere (CG-1); every fall-through reachable (CG-3); no early-closure or late-payment pricing below the schedule (CG-4); methods change formula shape, coinciding tiers fixed (CG-5); every factor-only convention sentence moved into its own factor sentence (CG-6); tie rules and decoy filters (chargebacks, FlexLine status, fee-own return) (CG-7); no AutoPay-history or stop-code due-day tiers (CG-8).

## Round 3 rework plan (audit revision_2: R2-1..R2-6, task-1 rounding tie)
- R2-1: every wait is satisfiable: relief waits become "the relief owed, if any, has been booked" (action form, fallback reason R2-3); each relief rule states when it is not owed (no fee, fee paid, already waived, courtesy limit used, outside the request window, comes to 0.00); fee waits exempt a fee that comes to 0.00; every write policy states its 0.00 outcome.
- R2-2: priority sentences: a fee of an account with a pending early-closure request gets the early-closure relief, and the made-good relief / goodwill credit are then not owed on it.
- R2-3: edges whose waited-on row is shared by two writes use the action form with a fallback reason.
- R2-4: hold add-back removed; paid-part tier covers every past-due case; request-before-return covered (negative lag counted as zero, own tier); same-day ties stated.
- R2-5: one plain binding per shared record selection (most recent return, fee, request, late fee); single-factor reads stay in their factor; reason factors read return-code counts.
- R2-6: clearing-ACH add-back struck; settlement fourth factor = hardship-plan standing (loan payments kept since the plan began), a hardship relief on closing interest.
- Rounding: every rule says "half a cent rounded up"; compute uses int(x*100+0.500001)/100; task-1 world changed so no gold lands on a half cent.
- Round 3 as built: the settlement's fourth factor is the payment-record share (12+ / 6-11 / fewer credited payments), not hardship-plan standing (keeps the hardship reads to the two existing factors and needs no new loan rows); task 1's partial payment is 62.00 (gold 2.0925 / 0.836 / 1.1172, none on a half cent).

## Round 4 rework plan (audit revision_3: R3-1, R3-2, R3-3)
- R3-1: strike cc_record; settlement fourth factor = hardship-cause share (cross hardship: death of a household earner / natural disaster / medical hardship 0.8; job loss / reduced income / divorce or separation 0.9; otherwise 1.0). Relief only for a borrower in hardship, for whom the base names early closure as the Credit Builder's hardship route; nobody outside hardship gets a cheaper closing than keeping the plan. Task 0 sits on the income tier (same 0.9), so no gold value moves.
- R3-2: re-enrollment carries a declared, scoped overwrite of the base due-day sentence (returned-AutoPay re-enrollment only; reset lines the debit up with funds; does not use the one change); a reset that moves the day stays in the same month; a 0-day buffer or the day-28 cap leaves the due day and next due date unchanged; an account with an amount past due keeps its due day and next due date (no unpaid installment moved later).
- R3-3: late fee owed only for the oldest unpaid due date (later lapsed due dates wait until they become the oldest; no fee on an installment late only because an earlier one is unpaid), nothing when that due date already carries its fee; returned-payment fee owed only for the most recent returned payment (a run of returns before the fee is charged costs one fee); both narrowings in the replaced_by of each policy's declared overwrite; prerequisite sentences and conditions already name exactly those records.
