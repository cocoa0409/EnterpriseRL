# Worklog — whole_life_loans_dividends_and_values (M=2)

## Draws (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems 3, factor_counts [5, 6, 5, 6]
- task 1: prerequisite_problems 2, factor_counts [4, 5, 4]

## Task 0 — Raymond E. Kessler, reduced paid-up election (frozen 2026-09-25 10:40:00 EDT)
Tree: whole_ext_reduced_paid_up_face (user, elect_reduced_paid_up_64725b60, 5 factors)
  <- whole_ext_offset_interest_extinguished (agent, extinguish_policy_loan_1349795c, 5)
       <- whole_ext_anniversary_interest_capitalization (agent, capitalize_loan_interest_55a34971, 6)
  <- whole_ext_election_accumulation_withdrawal (agent, withdraw_election_accumulations_2818c877, 6)
Gold: capitalization 287.67, offset principal 12538.27 / interest 114.93, withdrawal 10146.10, reduced face 76889.00.
Cross-difficulty: continuity counted from the converted term policy's issue date (term holding seeded).

## Task 1 — Lorraine M. Whitfield, full surrender (frozen 2026-10-05 10:15:00 EDT)
Tree: whole_ext_net_surrender_value (user, complete_policy_surrender_23994b0e, 4)
  <- whole_ext_anniversary_dividend_deposit (agent, deposit_anniversary_dividend_704bd37e, 4) <- interest credit (state gate)
  <- whole_ext_accumulation_interest_credit (agent, credit_accumulation_interest_b6da2e99, 5)
Gold: interest credit 397.37, deposit 1752.74, net surrender value 52903.93.

## Revisions
1. Task 0 anniversary moved 2026-09-05 -> 2026-08-20 with a 31-day loan-interest billing window: one-month gaps made the
   withdrawal start factor coincide with its baseline in whole months.
2. Continuing paid-up additions no longer add their face to the reduced face (kept in the additions face; avoids double count).
3. Loan principal for capitalization/offset read as the ledger total (history floor of check_compute).
4. Accumulation interest-credit rule gained the loan-activity cut (consistent with the election withdrawal's rate schedule);
   Task 0's seeded credit history regenerated with the same rule; Task 0 numbers propagated.
5. Coverage start written as `converted_term_issue or F('issue_date')` so continuity ladders register as multi-source.

Both tasks' seeded histories (interest credits, dividend deposits, capitalizations) were generated with the charter's own rules.
check_traceability deferred until the KB is published.

## Round 2 — policy-task audit rework (audits/policy_task/whole_life_loans_dividends_and_values)
- D-2 / T0-F1: billing-mode accrual ladders removed from the capitalization, offset and election withdrawal. Interest now follows the
  convention printed in the policy form by issue date (whole policy months before 1985, actual/360 for 1985-2004 forms, actual/365 from 2005).
  Kessler's capitalizations and repayment interest were regenerated under it (task 0 gold: 308.48 / 12608.88 + 123.29 / 10156.88 / 76775.00).
  A guaranteed-accumulation-rate floor was tried first and dropped, because wherever the floor binds it makes the rate increments inert.
- D-1 / T1-F1 / T1-F2: the surrender premium-record window is now stated as the 24 calendar months before the day the surrender is processed,
  matching compute; the 2024-10-04 return is outside under that anchor, so task 1's net stays 52903.93.
- D-6 / T1-F4: the credit rule states that every count and total is taken on the ledger as it stands on the processing day; the deposit uses the same wording.
- D-3 / T1-F3: the additions dividend is now a real method (apportioned by face once any addition is older than 36 months, by reserve otherwise).
- D-4: the offset policy no longer covers a cash surrender (declared override of the base occasions sentence); the surrender deducts the loan
  balance and its accrued interest itself.
- D-5: capitalization/offset rules now state exactly the latest-entry filters their compute applies.
- T0-F2 / T0-F3 / T0-O3: the face trace divides the stated net cash value; every tier_taken is the tier the world selects (asserted against the ladder);
  the principal tracing quotes the rule's own sentence.
- Whitfield's 2025 loan history regenerated under the actual/365 convention for a 2012 form (row ids unchanged in both tasks).

## Round 3 — audit revision_2
- D-7: surrender loan indebtedness reworked — interest starts at the latest interest-paying repayment (if later than the stale paid-to date),
  the latest capitalization dated after that start is taken back out of the principal, simple interest to the effective date; declared
  override of the base capitalization sentence for the surrender occasion. Order-independence checked on task 0's ledger with a
  hypothetical surrender request: 56,772.52 with or without the pending 2026-08-20 capitalization. Task 1 gold unchanged (52,903.93).
- T0-F4 / T0-O4: task 0 rationale EDGE 1-3 and BUSINESS-OBJECT passages now carry the round-2 world's figures; EDGE 1 quotes the offset rule verbatim.
