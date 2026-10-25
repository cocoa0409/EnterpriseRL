# Rework round 14 claims (personal_loan_servicing; seed-only round from the cross-product re-judge)

S5: closed — task 1's FlexLine late fee is re-priced from the FlexLine late-fee documents (unpaid-part figuring, balance-tier, grace-payment, history and tenure shares, cap and half-even rounding) on the regenerated FlexLine ledger.
S6: closed — task 1's FlexLine returned-payment fee is re-priced from the FlexLine returned-fee documents (flat figure for an R02 return, return-history, late-booking, shared-event and tenure shares).
S7: closed — task 0's FlexLine late fee is re-priced the same way. The borrower's catch-up payment now equals the past-due minimum plus that fee.
S8: closed — task 1's PracticePay late fee is re-priced from the PracticePay late-fee documents (level from the plan's late-fee record, FlexLine, personal-loan and principal-band shares). The payment that covered it carries the same fee, so the plan still pays down to zero.
S9: closed — FlexLine Standard annual-fee rows are added on each line's first anniversary (the tier does not waive the first year).
S9 class (every seeded FlexLine row priced by the line's own rules): closed — both FlexLine ledgers were regenerated from the published FlexLine rules:
- interest at each statement closing on the cycle's daily balances times the APR over 365, with the closing 25 days before each due date;
- minimum payment 3% of the statement balance with the 35.00 floor, paid on each due date;
- draw fees at 2.5%;
- statement closings that fell before frozen time but were missing are added;
- task 0's missed-payment cycle no longer assumes the missed payment was made.
Each line's balance, minimum due, amount past due and next due date now follow its regenerated ledger and the FlexLine record rules. Existing row ids are kept; new rows carry fresh uuid4 ids.
S10: closed — task 0's Short-Term Payment Deferral now expires the day after its acceptance period ends. Task 1's Term Extension Modification now completes on the day its last trial payment was credited.
Own loan rows: closed — installments were checked as level payments at the base rate (task 1's modified installment as audited), and fee rows against the rules in force on their dates. Task 0's closed loan's historical late fee was off by the base schedule's percent and is re-priced. That loan's AutoPay ended at payoff, so its current rate is its base rate again. Its AutoPay servicing history is outside every read the task makes, and the replay gate rejects seed rows nothing reads, so no servicing records were added for it.
Scored values: task 0 is unchanged. In task 1 the FlexLine minimum payment that bounced is larger now, and that changes the pay-cycle share, the bank-event share and therefore the courtesy waiver; the AutoPay rate is unchanged. Gold was recomputed by replaying the real tools. The late-fee line id the waiver points at was re-derived. Every trace, sensitivity, all-baseline result, skip effect, order replay, tracing, objective and dossier figure was regenerated, and every inline arithmetic claim was re-verified. Every prerequisite stays unmet at the opening, and every factor and edge still bears weight.
loan.extended.yaml and task_tools.py are byte-identical to the given hashes.
