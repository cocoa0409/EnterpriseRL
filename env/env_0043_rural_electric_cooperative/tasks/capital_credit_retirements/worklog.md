# worklog capital_credit_retirements (M=2)
- Step 0 draw: task0 prerequisite_problems=1 factor_counts=[6,4]; task1 prerequisite_problems=2 factor_counts=[5,4,6]
- Constraint found: capital_disbursement bill_credit / offset_unpaid_balance trigger into service -> no tool writes those methods (check / donation only).
- DSL cannot read customers; cross-difficulty evidence read from service holdings (final_date).
- Design: task0 = discounted early retirement of a one-season farm renter: agent books the approved distribution-margin row (6 factors) -> member elects the pass-through (G&T) row (user, 4 factors, root).
- task1 = estate of a deceased farm member: later-booked 2025 G&T pass-through allocation retired on the executor's election (user, 6) ; voided March estate check reissued (agent, 4) ; estate check for the new payable (agent, root, 5).
- REVISED design (payout computations proved too thin for 4-6 load-bearing factors; bookings carry the factors):
  tools: book_early_retirement_114ff464 (agent), elect_passthrough_early_retirement_2ee4171d (user),
         book_estate_later_allocation_bc10e318 (agent), elect_estate_passthrough_retirement_e31dc75a (user),
         reissue_capital_check_624c80d7 (agent)
  task0 (frozen 2026-11-24): root = member's election of the 2018 pass-through row (user, 4 factors) <- agent books the approved 2018 distribution-margin row (6 factors); edge value_input (one refiling fee per request, taken by the first row booked).
  task1 (frozen 2026-08-27): root = replacement check for the twice-returned Dec-2025 payout to the estate (agent, 4 factors) <- agent books the later 2025 distribution-margin allocation for the estate (5 factors, state form) and <- executor elects the later 2025 pass-through allocation (user, 6 factors, action form).
- task0 closed: gates green (extended pending task1 tool naming); rationale written
- task1 closed: per-task gates green; values dm 93.30, pass-through 22.93, replacement 137.87 (charges 24.45); prerequisites commute (proved by run).
- FINAL gate block: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK (suite means branches 36.50 / steps 11.00, history_rows_max 102, branches_max 41); GROUNDING OK; CACHE-DIFF INFO (optional, no cache trap designed); SCOPE OK.
- check_traceability.py NOT run: needs the published KB (not rendered yet).
