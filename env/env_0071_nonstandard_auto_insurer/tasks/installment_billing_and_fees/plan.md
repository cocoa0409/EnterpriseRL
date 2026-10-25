# plan — installment_billing_and_fees (category billing), M=2

Draw (draw_counts.py --tasks 2):
- task 0: prerequisite_problems 1 (2 problems), factor_counts [6, 5]
- task 1: prerequisite_problems 2 (3 problems), factor_counts [5, 5, 4]

Hard constraints carried (coordinator + XF recipe):
- frozen_time `YYYY-MM-DD HH:MM:SS EDT`; task_tools.py: no datetime/time/random/uuid imports; date maths via class static
  ordinal helper; every write tool calls ctx.create/update in its own body; no example values in docstrings.
- no factor id substring of a tool name; no past_due plan in any world (billing_delinquency_cured would be an
  uncarried obligation); no auto notice of cancellation lit (plan never past_due); agent fee avoided by using
  Monthly EFT / Monthly Card Autopay plans (agent_assisted_payment_fee 0.00) for phone payments.
- events written by my tools and their base triggers (all inside billing):
  billing_nsf_fee (triggers []), billing_late_fee ([]), billing_payment_received ([]),
  billing_installment_billed (-> billing:billing_installment_fee, written in the same tool), billing_installment_fee ([]).
- identifier band k=1: phones <area>5551###, DL last4 1###, surnames A-D, policy 7-digit / BP- / PMT- / acct last4 /
  VIN serial / case numbers start with 1.

Design (v1):
- T1 (3 problems): returned Monthly EFT draft (insufficient_funds), frozen after the 5-day grace, plan current
  (minimum due was paid at the end of its due date; base past_due test), NSF fee and late fee not yet booked.
  root P_mk makeup payment (user, 5) <- P_nsf returned-item fee (agent, 4) [value_input]
                                     <- P_late late fee (agent, 5) [value_input]; the two leaves commute.
- T0 (2 problems): Monthly Card Autopay plan, frozen = draft-notice issue date (due - 10), notice not issued.
  root P_pay phone payment of the coming installment (user, 5) <- P_notice draft notice minimum due (agent, 6)
  [value_input].
- cross-difficulty reads: auto_policies (garaging_state, term_number, status), auto_premium_transactions
  (additional premium), fr_filings (filing on the term).

Worklog: worklog.md (per-task cards, probe table, pairwise method-tier table, gate outputs).
Scratch: /tmp/installment_billing_and_fees_0071/ (verification scripts; deleted at the end).

Revision 4 (rework round 4): task 1 re-treed onto makeup, switch down payment and direct-bill switch (see worklog round 4).

Revision 2 (rework round 2): design superseded by the worklog's "Round 2 rework" section — task 0 notice factors are now
endorsement spread, credit carry, autopay standing, package tier, installment-size charge; task 1 is a returned 560.00 online
payment (account_closed) with returned-item fee (5), late fee (4) and makeup (5).
